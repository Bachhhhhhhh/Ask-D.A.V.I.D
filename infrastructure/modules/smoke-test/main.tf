locals {
  task_assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = var.account_id
        }
        ArnLike = {
          "aws:SourceArn" = "arn:aws:ecs:${var.region}:${var.account_id}:*"
        }
      }
    }]
  })

  smoke_task_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "ListOnlyApprovedRawBucket"
      Effect   = "Allow"
      Action   = ["s3:ListBucket"]
      Resource = "arn:aws:s3:::${var.raw_bucket_name}"
    }]
  })

  smoke_execution_secret_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "ReadOnlyRdsManagedCredentialForSmokeCheck"
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = var.rds_master_secret_arn
    }]
  })

  smoke_execution_pull_through_cache_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "ImportOnlyPinnedPublicImagesThroughPrivateEcr"
      Effect   = "Allow"
      Action   = ["ecr:BatchImportUpstreamImage", "ecr:CreateRepository"]
      Resource = "arn:aws:ecr:${var.region}:${var.account_id}:repository/ecr-public/*"
    }]
  })

  private_ecr_registry = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/ecr-public"

  task_definitions = {
    postgres = {
      image = "${local.private_ecr_registry}/docker/library/postgres@sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777"
      command = [
        "psql --no-psqlrc --set=ON_ERROR_STOP=1 --command 'SELECT 1' >/dev/null",
        "printf 'RDS_SMOKE_PASS\\n'",
      ]
      environment = [
        { name = "PGHOST", value = var.rds_endpoint },
        { name = "PGPORT", value = "5432" },
        { name = "PGDATABASE", value = "platform" },
        { name = "PGSSLMODE", value = "require" },
      ]
      secrets = [
        { name = "PGUSER", valueFrom = "${var.rds_master_secret_arn}:username::" },
        { name = "PGPASSWORD", valueFrom = "${var.rds_master_secret_arn}:password::" },
      ]
    }
    redis = {
      image = "${local.private_ecr_registry}/docker/library/redis@sha256:e7723ff73d963f5cc6d9c4643ea3d989527a402a319239054e9472a7fb9219a2"
      command = [
        "redis-cli --tls --sni \"$REDIS_ENDPOINT\" -h \"$REDIS_ENDPOINT\" -p 6379 ping | grep -qx PONG",
        "printf 'REDIS_TLS_SMOKE_PASS\\n'",
      ]
      environment = [{ name = "REDIS_ENDPOINT", value = var.redis_endpoint }]
      secrets     = []
    }
    s3 = {
      image = "${local.private_ecr_registry}/aws-cli/aws-cli@sha256:7e0331f50ea97c09241521688082ef39a95b5f10ddd2eaabeef4313d974b5258"
      command = [
        "aws s3api head-bucket --bucket \"$RAW_BUCKET\"",
        "if aws s3api head-bucket --bucket \"$CURATED_BUCKET\" 2>/dev/null; then echo S3_DENY_SMOKE_FAILED; exit 1; fi",
        "printf 'S3_POLICY_SMOKE_PASS\\n'",
      ]
      environment = [
        { name = "RAW_BUCKET", value = var.raw_bucket_name },
        { name = "CURATED_BUCKET", value = var.curated_bucket_name },
      ]
      secrets = []
    }
  }
}

resource "aws_iam_role" "execution" {
  name               = "${var.name_prefix}-smoke-execution"
  assume_role_policy = local.task_assume_role_policy
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "execution_rds_secret" {
  name   = "read-rds-managed-credential-only"
  role   = aws_iam_role.execution.id
  policy = local.smoke_execution_secret_policy
}

resource "aws_iam_role_policy" "execution_pull_through_cache" {
  name   = "import-pinned-public-images-through-private-ecr"
  role   = aws_iam_role.execution.id
  policy = local.smoke_execution_pull_through_cache_policy
}

resource "aws_iam_role" "task" {
  name               = "${var.name_prefix}-smoke-task"
  assume_role_policy = local.task_assume_role_policy
  tags               = var.tags
}

resource "aws_iam_role_policy" "task" {
  name   = "list-raw-bucket-only"
  role   = aws_iam_role.task.id
  policy = local.smoke_task_policy
}

resource "aws_ecs_task_definition" "this" {
  for_each = local.task_definitions

  family                   = "${var.name_prefix}-smoke-${each.key}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([{
    name        = "${each.key}-smoke"
    image       = each.value.image
    essential   = true
    entryPoint  = ["/bin/sh", "-ec"]
    command     = [join("; ", each.value.command)]
    environment = each.value.environment
    secrets     = each.value.secrets
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = replace(var.runtime_log_group_arn, "arn:aws:logs:${var.region}:${var.account_id}:log-group:", "")
        awslogs-region        = var.region
        awslogs-stream-prefix = "smoke/${each.key}"
      }
    }
  }])

  tags = merge(var.tags, {
    Component = "synthetic-smoke-test"
    Purpose   = "goal-3b-private-validation"
  })

  depends_on = [
    aws_iam_role_policy_attachment.execution,
    aws_iam_role_policy.execution_rds_secret,
    aws_iam_role_policy.execution_pull_through_cache,
    aws_iam_role_policy.task,
  ]
}
