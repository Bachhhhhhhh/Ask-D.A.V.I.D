locals {
  ecs_tasks_assume_role = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
  workload_observability_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "WriteRuntimeObservability"
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = ["${var.runtime_log_group_arn}:*"]
      },
      {
        Sid      = "WriteXRayTelemetry"
        Effect   = "Allow"
        Action   = ["xray:PutTraceSegments", "xray:PutTelemetryRecords"]
        Resource = ["*"]
      },
    ]
  })
}

resource "aws_iam_role" "task_execution" {
  name               = "${var.name_prefix}-ecs-execution"
  assume_role_policy = local.ecs_tasks_assume_role
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "task_execution_goal6_secrets" {
  count = length(var.goal6_secret_arns) > 0 ? 1 : 0

  name = "read-goal6-secret-containers"
  role = aws_iam_role.task_execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadExactGoal6SecretContainers"
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = var.goal6_secret_arns
      },
      {
        Sid      = "DecryptGoal6SecretKey"
        Effect   = "Allow"
        Action   = ["kms:Decrypt"]
        Resource = var.goal6_secrets_kms_key_arn
      },
    ]
  })
}

resource "aws_iam_role_policy" "task_execution_goal7_secrets" {
  count = var.goal7_secrets_enabled ? 1 : 0

  name = "read-goal7-secret-containers"
  role = aws_iam_role.task_execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadExactGoal7SecretContainers"
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = var.goal7_secret_arns
      },
      {
        Sid      = "DecryptGoal7SecretKey"
        Effect   = "Allow"
        Action   = ["kms:Decrypt"]
        Resource = var.goal7_secrets_kms_key_arn
      },
    ]
  })
}

resource "aws_iam_role" "workload" {
  name               = "${var.name_prefix}-ecs-workload"
  assume_role_policy = local.ecs_tasks_assume_role
  tags               = var.tags
}

resource "aws_iam_role_policy" "workload" {
  name   = "runtime-observability-only"
  role   = aws_iam_role.workload.id
  policy = local.workload_observability_policy
}

resource "aws_iam_role_policy" "workload_goal7_opensearch" {
  count = var.goal7_enabled ? 1 : 0

  name = "goal7-opensearch-data-plane"
  role = aws_iam_role.workload.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "UseApprovedGoal7CollectionDataPlane"
      Effect   = "Allow"
      Action   = ["aoss:APIAccessAll"]
      Resource = ["*"]
      Condition = {
        StringEquals = {
          "aoss:collection" = var.goal7_collection_name
        }
      }
    }]
  })
}
