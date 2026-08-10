locals {
  vpc_flow_log_group_arn = "arn:aws:logs:${var.region}:${var.account_id}:log-group:/${var.name_prefix}/vpc-flow"

  vpc_flow_logs_assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "vpc-flow-logs.amazonaws.com" }
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = var.account_id
        }
        ArnLike = {
          "aws:SourceArn" = "arn:aws:ec2:${var.region}:${var.account_id}:vpc-flow-log/*"
        }
      }
    }]
  })

  vpc_flow_logs_delivery_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "DescribeApprovedLogGroup"
        Effect   = "Allow"
        Action   = ["logs:DescribeLogGroups", "logs:DescribeLogStreams"]
        Resource = "*"
      },
      {
        Sid      = "WriteApprovedVpcFlowLog"
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "${local.vpc_flow_log_group_arn}:*"
      },
    ]
  })
}

resource "aws_cloudwatch_log_group" "vpc_flow" {
  name              = "/${var.name_prefix}/vpc-flow"
  retention_in_days = var.retention_days
  kms_key_id        = var.kms_key_arn
  tags              = merge(var.tags, { VpcId = var.vpc_id })
}

resource "aws_iam_role" "vpc_flow_logs" {
  name               = "${var.name_prefix}-vpc-flow-logs"
  assume_role_policy = local.vpc_flow_logs_assume_role_policy
  tags               = var.tags
}

resource "aws_iam_role_policy" "vpc_flow_logs" {
  name   = "deliver-vpc-flow-logs"
  role   = aws_iam_role.vpc_flow_logs.id
  policy = local.vpc_flow_logs_delivery_policy
}

resource "aws_flow_log" "vpc" {
  log_destination_type     = "cloud-watch-logs"
  log_destination          = aws_cloudwatch_log_group.vpc_flow.arn
  iam_role_arn             = aws_iam_role.vpc_flow_logs.arn
  vpc_id                   = var.vpc_id
  traffic_type             = "ALL"
  max_aggregation_interval = 600
  tags                     = var.tags

  depends_on = [aws_iam_role_policy.vpc_flow_logs]
}

resource "aws_cloudwatch_log_group" "runtime" {
  name              = "/${var.name_prefix}/runtime"
  retention_in_days = var.retention_days
  kms_key_id        = var.kms_key_arn
  tags              = var.tags
}
resource "aws_sns_topic" "alerts" {
  name              = "${var.name_prefix}-alerts"
  kms_master_key_id = var.kms_key_arn
  tags              = var.tags
}

resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${var.name_prefix}-rds-cpu-high"
  alarm_description   = "Sustained high average CPU utilization on the development PostgreSQL RDS instance."
  actions_enabled     = true
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 5
  datapoints_to_alarm = 5
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 60
  statistic           = "Average"
  threshold           = var.rds_cpu_alarm_threshold_percent
  unit                = "Percent"
  treat_missing_data  = "missing"

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_identifier
  }

  alarm_actions             = [aws_sns_topic.alerts.arn]
  ok_actions                = []
  insufficient_data_actions = []

  tags = var.tags
}
