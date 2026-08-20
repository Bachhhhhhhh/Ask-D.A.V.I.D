locals {
  task_assume_role = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
  tags = merge(var.tags, {
    Component = "apache-doris-verifier"
    Goal      = "goal-06"
  })
}

resource "aws_ecr_repository" "image" {
  count = var.enabled ? 1 : 0

  name                 = "${var.name_prefix}/doris-verifier"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  tags = local.tags
}

resource "aws_security_group" "admin" {
  count = var.enabled ? 1 : 0

  name                   = "${var.name_prefix}-doris-admin-task"
  description            = "One-off Goal 6 Doris admin-refresh task only."
  vpc_id                 = var.vpc_id
  revoke_rules_on_delete = true
  tags                   = merge(local.tags, { Role = "admin-refresh" })
}

resource "aws_security_group" "verifier" {
  count = var.enabled ? 1 : 0

  name                   = "${var.name_prefix}-doris-verifier-task"
  description            = "One-off Goal 6 read-only Doris verifier only."
  vpc_id                 = var.vpc_id
  revoke_rules_on_delete = true
  tags                   = merge(local.tags, { Role = "read-only-verifier" })
}

resource "aws_vpc_security_group_egress_rule" "admin_https" {
  count = var.enabled ? 1 : 0

  security_group_id = aws_security_group.admin[0].id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  description       = "Private-subnet HTTPS to approved AWS and Databricks endpoints."
}

resource "aws_vpc_security_group_egress_rule" "verifier_https" {
  count = var.enabled ? 1 : 0

  security_group_id = aws_security_group.verifier[0].id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  description       = "Private-subnet HTTPS to approved AWS and Databricks endpoints."
}

resource "aws_vpc_security_group_egress_rule" "admin_to_fe" {
  count = var.enabled ? 1 : 0

  security_group_id            = aws_security_group.admin[0].id
  referenced_security_group_id = var.fe_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 9030
  to_port                      = 9030
  description                  = "Doris administration through the private FE only."
}

resource "aws_vpc_security_group_egress_rule" "verifier_to_fe" {
  count = var.enabled ? 1 : 0

  security_group_id            = aws_security_group.verifier[0].id
  referenced_security_group_id = var.fe_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 9030
  to_port                      = 9030
  description                  = "Read-only verification through the private FE only."
}

resource "aws_iam_role" "admin" {
  count = var.enabled ? 1 : 0

  name               = "${var.name_prefix}-doris-admin-task"
  assume_role_policy = local.task_assume_role
  tags               = local.tags
}

resource "aws_iam_role" "verifier" {
  count = var.enabled ? 1 : 0

  name               = "${var.name_prefix}-doris-verifier-task"
  assume_role_policy = local.task_assume_role
  tags               = local.tags
}

resource "aws_iam_role_policy" "admin" {
  count = var.enabled ? 1 : 0

  name = "read-exact-doris-admin-and-oauth-secrets"
  role = aws_iam_role.admin[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadExactAdminSecrets"
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [var.admin_secret_arn, var.oauth_secret_arn, var.query_secret_arn]
      },
      {
        Sid      = "WriteOnlyDorisLogs"
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "${var.doris_log_group_arn}:*"
      },
    ]
  })
}

resource "aws_iam_role_policy" "verifier" {
  count = var.enabled ? 1 : 0

  name = "read-exact-doris-query-secret"
  role = aws_iam_role.verifier[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadExactQuerySecret"
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [var.query_secret_arn]
      },
      {
        Sid      = "WriteOnlyDorisLogs"
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "${var.doris_log_group_arn}:*"
      },
    ]
  })
}

resource "aws_ecs_task_definition" "admin" {
  count = var.enabled && var.task_definitions_enabled ? 1 : 0

  family                   = "${var.name_prefix}-doris-admin-refresh"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = aws_iam_role.admin[0].arn
  container_definitions = jsonencode([{
    name      = "doris-admin"
    image     = var.image
    essential = true
    command   = ["/app/doris-admin-refresh"]
    environment = [
      { name = "DORIS_FE_HOST", value = var.fe_private_ip },
      { name = "DORIS_BE_HOST", value = var.be_private_ip },
      { name = "DATABRICKS_WORKSPACE_HOST", value = var.databricks_workspace_host },
    ]
    secrets = [
      { name = "DORIS_ADMIN_SECRET", valueFrom = var.admin_secret_arn },
      { name = "DATABRICKS_OAUTH_SECRET", valueFrom = var.oauth_secret_arn },
      { name = "DORIS_QUERY_SECRET", valueFrom = var.query_secret_arn },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = var.doris_log_group_name
        awslogs-region        = var.region
        awslogs-stream-prefix = "admin"
      }
    }
  }])
  tags = local.tags
}

resource "aws_ecs_task_definition" "verifier" {
  count = var.enabled && var.task_definitions_enabled ? 1 : 0

  family                   = "${var.name_prefix}-doris-verifier"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = aws_iam_role.verifier[0].arn
  container_definitions = jsonencode([{
    name        = "doris-verifier"
    image       = var.image
    essential   = true
    command     = ["/app/doris-readonly-verify"]
    environment = [{ name = "DORIS_FE_HOST", value = var.fe_private_ip }]
    secrets     = [{ name = "DORIS_QUERY_SECRET", valueFrom = var.query_secret_arn }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = var.doris_log_group_name
        awslogs-region        = var.region
        awslogs-stream-prefix = "verifier"
      }
    }
  }])
  tags = local.tags
}
