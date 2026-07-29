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
