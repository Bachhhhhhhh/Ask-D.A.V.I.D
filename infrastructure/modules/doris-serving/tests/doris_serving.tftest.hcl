mock_provider "aws" {}

override_data {
  target = data.aws_subnet.selected[0]
  values = {
    availability_zone = "ap-southeast-1a"
    cidr_block        = "10.42.64.0/20"
  }
}

# Make the rendered user-data size check deterministic during the offline plan.
override_resource {
  target = aws_cloudwatch_log_group.doris[0]
  values = {
    name = "/ask-david-development/doris"
  }
}

override_resource {
  target = aws_ebs_volume.fe_data_rebuild[0]
  values = {
    id = "vol-0123456789abcdef0"
  }
}

override_resource {
  target = aws_ebs_volume.be_data_rebuild[0]
  values = {
    id = "vol-0123456789abcdef1"
  }
}

run "private_cluster_initiated_traffic_is_bidirectional" {
  command = plan

  variables {
    enabled                   = true
    name_prefix               = "ask-david-development"
    region                    = "ap-southeast-1"
    vpc_id                    = "vpc-0123456789abcdef0"
    data_subnet_id            = "subnet-0123456789abcdef0"
    fe_private_ip             = "10.42.64.238"
    be_private_ip             = "10.42.71.97"
    data_kms_key_arn          = "arn:aws:kms:ap-southeast-1:123456789012:key/00000000-0000-0000-0000-000000000001"
    observability_kms_key_arn = "arn:aws:kms:ap-southeast-1:123456789012:key/00000000-0000-0000-0000-000000000002"
    log_retention_days        = 30
    fe_instance_type          = "m7i.xlarge"
    be_instance_type          = "m7i.xlarge"
    ami_id                    = "ami-0123456789abcdef0"
    fe_image                  = "docker.io/apache/doris:fe-4.0.1@sha256:0000000000000000000000000000000000000000000000000000000000000001"
    be_image                  = "docker.io/apache/doris:be-4.0.1@sha256:0000000000000000000000000000000000000000000000000000000000000002"
    fe_data_volume_gib        = 20
    be_data_volume_gib        = 50
    rebuild_serving_state     = true
    fe_root_volume_gib        = 30
    be_root_volume_gib        = 30
    be_bootstrap_generation   = 2
    fe_bootstrap_generation   = 2
    admin_secret_arn          = "arn:aws:secretsmanager:ap-southeast-1:123456789012:secret:ask-david-development-doris-admin"
    query_secret_arn          = "arn:aws:secretsmanager:ap-southeast-1:123456789012:secret:ask-david-development-doris-query"
    priority_networks         = "10.42.0.0/16"
    tags = {
      Environment = "development"
      Goal        = "goal-06"
    }
  }

  assert {
    condition = (
      length(aws_vpc_security_group_ingress_rule.fe_to_be) == 4 &&
      length(aws_vpc_security_group_egress_rule.fe_to_be) == 4
    )
    error_message = "FE-to-BE SG rules must cover audit HTTP 8040 and all three approved membership ports."
  }

  assert {
    condition = (
      contains(keys(aws_vpc_security_group_ingress_rule.fe_to_be), "8040") &&
      contains(keys(aws_vpc_security_group_egress_rule.fe_to_be), "8040")
    )
    error_message = "Doris AuditLoader requires paired FE-to-BE TCP/8040 SG rules."
  }

  assert {
    condition = (
      aws_vpc_security_group_ingress_rule.be_to_fe_registration[0].from_port == 9030 &&
      aws_vpc_security_group_egress_rule.be_to_fe_registration[0].from_port == 9030
    )
    error_message = "BE registration requires paired private ingress/egress on FE port 9030."
  }

  assert {
    condition = (
      aws_vpc_security_group_ingress_rule.be_to_fe_rpc[0].from_port == 9020 &&
      aws_vpc_security_group_ingress_rule.be_to_fe_rpc[0].to_port == 9020 &&
      aws_vpc_security_group_egress_rule.be_to_fe_rpc[0].from_port == 9020 &&
      aws_vpc_security_group_egress_rule.be_to_fe_rpc[0].to_port == 9020
    )
    error_message = "BE callbacks require paired SG-to-SG ingress/egress on FE RPC port 9020."
  }

}
