locals {
  enabled_tags = merge(var.tags, {
    Component = "apache-doris-serving"
    Goal      = "goal-06"
  })

  # Terraform 1.15 does not provide the cidrcontains function.  The approved Goal 6
  # development subnet is /20, so enumerate its 16 /24 blocks and 256 host
  # offsets per block.  A non-/20 selected subnet produces an empty list and
  # fails the check/precondition below rather than silently widening scope.
  selected_subnet_ipv4_hosts = var.enabled ? (
    can(regex("/20$", data.aws_subnet.selected[0].cidr_block)) ? flatten([
      for subnet_number in range(0, 16) : [
        for host_number in range(0, 256) : cidrhost(
          data.aws_subnet.selected[0].cidr_block,
          subnet_number * 256 + host_number
        )
      ]
    ]) : []
  ) : []

  # Keep the rendered bootstrap in one place for the instance assignments.
  fe_user_data = var.enabled ? join("\n", [
    templatefile("${path.module}/templates/doris-host.sh.tftpl", {
      role                = "fe"
      image               = var.fe_image
      data_mount          = "/var/lib/doris"
      log_group           = aws_cloudwatch_log_group.doris[0].name
      region              = var.region
      volume_id           = var.rebuild_serving_state ? aws_ebs_volume.fe_data_rebuild[0].id : aws_ebs_volume.fe_data[0].id
      admin_secret_arn    = var.admin_secret_arn
      priority_networks   = var.priority_networks
      fe_private_ip       = ""
      expected_private_ip = var.fe_private_ip
    }),
    "# Goal 6 FE bootstrap generation: ${var.fe_bootstrap_generation}",
  ]) : ""

  be_user_data = var.enabled ? join("\n", [
    templatefile("${path.module}/templates/doris-host.sh.tftpl", {
      role                = "be"
      image               = var.be_image
      data_mount          = "/var/lib/doris"
      log_group           = aws_cloudwatch_log_group.doris[0].name
      region              = var.region
      volume_id           = var.rebuild_serving_state ? aws_ebs_volume.be_data_rebuild[0].id : aws_ebs_volume.be_data[0].id
      admin_secret_arn    = var.admin_secret_arn
      priority_networks   = var.priority_networks
      fe_private_ip       = var.fe_private_ip
      expected_private_ip = var.be_private_ip
    }),
    "# Goal 6 BE bootstrap generation: ${var.be_bootstrap_generation}",
  ]) : ""

  # EBS volume IDs are fixed-length ASCII values (`vol-` plus 17 hex
  # characters). Substitute that deterministic shape so the pre-plan guard is
  # known even while a replacement volume ID is not yet allocated.
  fe_user_data_size_check = var.enabled ? join("\n", [
    templatefile("${path.module}/templates/doris-host.sh.tftpl", {
      role                = "fe"
      image               = var.fe_image
      data_mount          = "/var/lib/doris"
      log_group           = "/${var.name_prefix}/doris"
      region              = var.region
      volume_id           = "vol-0123456789abcdef0"
      admin_secret_arn    = var.admin_secret_arn
      priority_networks   = var.priority_networks
      fe_private_ip       = ""
      expected_private_ip = var.fe_private_ip
    }),
    "# Goal 6 FE bootstrap generation: ${var.fe_bootstrap_generation}",
  ]) : ""

  be_user_data_size_check = var.enabled ? join("\n", [
    templatefile("${path.module}/templates/doris-host.sh.tftpl", {
      role                = "be"
      image               = var.be_image
      data_mount          = "/var/lib/doris"
      log_group           = "/${var.name_prefix}/doris"
      region              = var.region
      volume_id           = "vol-0123456789abcdef0"
      admin_secret_arn    = var.admin_secret_arn
      priority_networks   = var.priority_networks
      fe_private_ip       = var.fe_private_ip
      expected_private_ip = var.be_private_ip
    }),
    "# Goal 6 BE bootstrap generation: ${var.be_bootstrap_generation}",
  ]) : ""
}

resource "aws_cloudwatch_log_group" "doris" {
  count = var.enabled ? 1 : 0

  name              = "/${var.name_prefix}/doris"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.observability_kms_key_arn
  tags              = local.enabled_tags
}

resource "aws_iam_role" "instance" {
  count = var.enabled ? 1 : 0

  name = "${var.name_prefix}-doris-instance"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
  tags = local.enabled_tags
}

resource "aws_iam_role_policy" "instance_logs" {
  count = var.enabled ? 1 : 0

  name = "doris-write-only-cloudwatch"
  role = aws_iam_role.instance[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "WriteOnlyDorisLogs"
      Effect   = "Allow"
      Action   = ["logs:CreateLogStream", "logs:DescribeLogStreams", "logs:PutLogEvents"]
      Resource = "${aws_cloudwatch_log_group.doris[0].arn}:*"
      }, {
      Sid      = "ReadExactBootstrapSecrets"
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [var.admin_secret_arn, var.query_secret_arn]
    }]
  })
}

resource "aws_iam_instance_profile" "this" {
  count = var.enabled ? 1 : 0

  name = "${var.name_prefix}-doris-instance"
  role = aws_iam_role.instance[0].name
  tags = local.enabled_tags
}

resource "aws_security_group" "fe" {
  count = var.enabled ? 1 : 0

  name                   = "${var.name_prefix}-doris-fe"
  description            = "Private Apache Doris FE; only Goal 6 roles may connect."
  vpc_id                 = var.vpc_id
  revoke_rules_on_delete = true
  tags                   = merge(local.enabled_tags, { Role = "frontend" })
}

resource "aws_security_group" "be" {
  count = var.enabled ? 1 : 0

  name                   = "${var.name_prefix}-doris-be"
  description            = "Private Apache Doris BE; only its paired FE may connect."
  vpc_id                 = var.vpc_id
  revoke_rules_on_delete = true
  tags                   = merge(local.enabled_tags, { Role = "backend" })
}

resource "aws_vpc_security_group_ingress_rule" "fe_to_be" {
  # Doris AuditLoader sends an HTTP stream-load batch through FE and follows
  # the redirect to the BE webserver port (8040). Keep that path paired with
  # the existing FE-to-BE membership/RPC ports and SG-scoped.
  for_each = var.enabled ? toset(["8040", "9050", "9060", "8060"]) : toset([])

  security_group_id            = aws_security_group.be[0].id
  referenced_security_group_id = aws_security_group.fe[0].id
  ip_protocol                  = "tcp"
  from_port                    = tonumber(each.value)
  to_port                      = tonumber(each.value)
  description                  = "Documented Doris FE-to-BE membership traffic."
}

# The FE initiates heartbeat/RPC traffic to the BE.  The dedicated FE security
# group otherwise permits only HTTPS egress, so the matching ingress rules
# above are not sufficient on their own.
resource "aws_vpc_security_group_egress_rule" "fe_to_be" {
  for_each = var.enabled ? toset(["8040", "9050", "9060", "8060"]) : toset([])

  security_group_id            = aws_security_group.fe[0].id
  referenced_security_group_id = aws_security_group.be[0].id
  ip_protocol                  = "tcp"
  from_port                    = tonumber(each.value)
  to_port                      = tonumber(each.value)
  description                  = "Documented Doris FE-to-BE membership traffic."
}

# The official Doris BE Docker entrypoint connects to the FE MySQL/query port
# to inspect membership and issue ALTER SYSTEM ADD BACKEND during bootstrap.
# Keep this path private and scoped to the paired BE security group.
resource "aws_vpc_security_group_ingress_rule" "be_to_fe_registration" {
  count = var.enabled ? 1 : 0

  security_group_id            = aws_security_group.fe[0].id
  referenced_security_group_id = aws_security_group.be[0].id
  ip_protocol                  = "tcp"
  from_port                    = 9030
  to_port                      = 9030
  description                  = "Private Doris BE bootstrap registration with FE."
}

resource "aws_vpc_security_group_egress_rule" "be_to_fe_registration" {
  count = var.enabled ? 1 : 0

  security_group_id            = aws_security_group.be[0].id
  referenced_security_group_id = aws_security_group.fe[0].id
  ip_protocol                  = "tcp"
  from_port                    = 9030
  to_port                      = 9030
  description                  = "Private Doris BE bootstrap registration with FE."
}

# A running BE reports disk, tablet, task, and index-policy state to the FE
# Thrift RPC listener. Keep both sides of this connection private and scoped
# to the paired Doris security groups.
resource "aws_vpc_security_group_ingress_rule" "be_to_fe_rpc" {
  count = var.enabled ? 1 : 0

  security_group_id            = aws_security_group.fe[0].id
  referenced_security_group_id = aws_security_group.be[0].id
  ip_protocol                  = "tcp"
  from_port                    = 9020
  to_port                      = 9020
  description                  = "Private Doris BE callbacks to the FE RPC listener."
}

resource "aws_vpc_security_group_egress_rule" "be_to_fe_rpc" {
  count = var.enabled ? 1 : 0

  security_group_id            = aws_security_group.be[0].id
  referenced_security_group_id = aws_security_group.fe[0].id
  ip_protocol                  = "tcp"
  from_port                    = 9020
  to_port                      = 9020
  description                  = "Private Doris BE callbacks to the FE RPC listener."
}

resource "aws_vpc_security_group_ingress_rule" "be_to_fe_edit_log" {
  count = var.enabled ? 1 : 0

  security_group_id            = aws_security_group.fe[0].id
  referenced_security_group_id = aws_security_group.be[0].id
  ip_protocol                  = "tcp"
  from_port                    = 9010
  to_port                      = 9010
  description                  = "Documented Doris BE-to-FE edit-log coordination."
}

# Required only for private-subnet TLS egress through the existing NAT to
# Databricks and AWS endpoints. There is no public ingress on this resource.
#trivy:ignore:AVD-AWS-0104
resource "aws_vpc_security_group_egress_rule" "fe_https" {
  count = var.enabled ? 1 : 0

  security_group_id = aws_security_group.fe[0].id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  description       = "Private-subnet HTTPS egress to approved cloud endpoints."
}

# Required only for private-subnet TLS egress through the existing NAT to
# Databricks and AWS endpoints. There is no public ingress on this resource.
#trivy:ignore:AVD-AWS-0104
resource "aws_vpc_security_group_egress_rule" "be_https" {
  count = var.enabled ? 1 : 0

  security_group_id = aws_security_group.be[0].id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  description       = "Private-subnet HTTPS egress to approved cloud endpoints."
}

resource "aws_ebs_volume" "fe_data" {
  count = var.enabled ? 1 : 0

  availability_zone = data.aws_subnet.selected[0].availability_zone
  size              = var.fe_data_volume_gib
  type              = "gp3"
  encrypted         = true
  kms_key_id        = var.data_kms_key_arn
  lifecycle {
    prevent_destroy = true
  }
  tags = merge(local.enabled_tags, { Role = "frontend-metadata" })
}

resource "aws_ebs_volume" "be_data" {
  count = var.enabled ? 1 : 0

  availability_zone = data.aws_subnet.selected[0].availability_zone
  size              = var.be_data_volume_gib
  type              = "gp3"
  encrypted         = true
  kms_key_id        = var.data_kms_key_arn
  lifecycle {
    prevent_destroy = true
  }
  tags = merge(local.enabled_tags, { Role = "backend-serving-data" })
}

# A failed single-node Doris startup must not trigger an implicit metadata or
# serving-data reset. When the explicit recovery gate is enabled, create new
# encrypted volumes and leave the prior Terraform-managed volumes intact for
# later evidence review or separately approved cleanup.
resource "aws_ebs_volume" "fe_data_rebuild" {
  count = var.enabled && var.rebuild_serving_state ? 1 : 0

  availability_zone = data.aws_subnet.selected[0].availability_zone
  size              = var.fe_data_volume_gib
  type              = "gp3"
  encrypted         = true
  kms_key_id        = var.data_kms_key_arn
  lifecycle {
    prevent_destroy = true
  }
  tags = merge(local.enabled_tags, {
    Role          = "frontend-metadata-rebuild"
    StateRecovery = "explicit-goal6-rebuild"
  })
}

resource "aws_ebs_volume" "be_data_rebuild" {
  count = var.enabled && var.rebuild_serving_state ? 1 : 0

  availability_zone = data.aws_subnet.selected[0].availability_zone
  size              = var.be_data_volume_gib
  type              = "gp3"
  encrypted         = true
  kms_key_id        = var.data_kms_key_arn
  lifecycle {
    prevent_destroy = true
  }
  tags = merge(local.enabled_tags, {
    Role          = "backend-serving-data-rebuild"
    StateRecovery = "explicit-goal6-rebuild"
  })
}

data "aws_subnet" "selected" {
  count = var.enabled ? 1 : 0
  id    = var.data_subnet_id
}

check "private_ips_are_valid_for_selected_subnet" {
  assert {
    condition = !var.enabled || (
      length(local.selected_subnet_ipv4_hosts) > 0 &&
      var.fe_private_ip != var.be_private_ip &&
      contains(local.selected_subnet_ipv4_hosts, var.fe_private_ip) &&
      contains(local.selected_subnet_ipv4_hosts, var.be_private_ip)
    )
    error_message = "Goal 6 FE and BE private IPs must be distinct IPv4 addresses inside the selected private data subnet."
  }
}

check "ec2_user_data_is_within_aws_limit" {
  assert {
    condition = !var.enabled || (
      length(local.fe_user_data_size_check) <= 16384 &&
      length(local.be_user_data_size_check) <= 16384
    )
    error_message = "Goal 6 rendered EC2 user_data must be at most 16384 bytes for both FE and BE."
  }
}

resource "aws_instance" "fe" {
  count = var.enabled ? 1 : 0

  ami                         = var.ami_id
  instance_type               = var.fe_instance_type
  subnet_id                   = var.data_subnet_id
  private_ip                  = var.fe_private_ip
  associate_public_ip_address = false
  lifecycle {
    precondition {
      condition = (
        length(local.selected_subnet_ipv4_hosts) > 0 &&
        var.fe_private_ip != var.be_private_ip &&
        contains(local.selected_subnet_ipv4_hosts, var.fe_private_ip) &&
        contains(local.selected_subnet_ipv4_hosts, var.be_private_ip)
      )
      error_message = "Goal 6 FE/BE private IPs must be distinct and inside the selected private data subnet."
    }
  }
  vpc_security_group_ids      = [aws_security_group.fe[0].id]
  iam_instance_profile        = aws_iam_instance_profile.this[0].name
  user_data                   = local.fe_user_data
  user_data_replace_on_change = true

  root_block_device {
    encrypted   = true
    kms_key_id  = var.data_kms_key_arn
    volume_size = var.fe_root_volume_gib
    volume_type = "gp3"
  }
  metadata_options { http_tokens = "required" }
  tags = merge(local.enabled_tags, { Role = "frontend" })
}

resource "aws_instance" "be" {
  count = var.enabled ? 1 : 0

  ami                         = var.ami_id
  instance_type               = var.be_instance_type
  subnet_id                   = var.data_subnet_id
  private_ip                  = var.be_private_ip
  associate_public_ip_address = false
  vpc_security_group_ids      = [aws_security_group.be[0].id]
  iam_instance_profile        = aws_iam_instance_profile.this[0].name
  user_data                   = local.be_user_data
  user_data_replace_on_change = true

  root_block_device {
    encrypted   = true
    kms_key_id  = var.data_kms_key_arn
    volume_size = var.be_root_volume_gib
    volume_type = "gp3"
  }
  metadata_options { http_tokens = "required" }
  tags = merge(local.enabled_tags, { Role = "backend" })
}

resource "aws_volume_attachment" "fe" {
  count = var.enabled ? 1 : 0

  device_name = "/dev/sdf"
  volume_id   = var.rebuild_serving_state ? aws_ebs_volume.fe_data_rebuild[0].id : aws_ebs_volume.fe_data[0].id
  instance_id = aws_instance.fe[0].id
}

resource "aws_volume_attachment" "be" {
  count = var.enabled ? 1 : 0

  device_name = "/dev/sdf"
  volume_id   = var.rebuild_serving_state ? aws_ebs_volume.be_data_rebuild[0].id : aws_ebs_volume.be_data[0].id
  instance_id = aws_instance.be[0].id
}
