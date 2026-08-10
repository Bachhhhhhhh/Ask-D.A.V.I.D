mock_provider "aws" {
  mock_resource "aws_sns_topic" {
    defaults = {
      arn = "arn:aws:sns:ap-southeast-1:123456789012:ask-david-development-alerts"
    }
  }
}

run "vpc_flow_logs_are_delivered_to_the_approved_log_group" {
  command = plan

  variables {
    name_prefix                     = "ask-david-development"
    vpc_id                          = "vpc-0123456789abcdef0"
    retention_days                  = 30
    kms_key_arn                     = "arn:aws:kms:ap-southeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
    account_id                      = "123456789012"
    region                          = "ap-southeast-1"
    rds_instance_identifier         = "ask-david-development-postgres"
    rds_cpu_alarm_threshold_percent = 90
    tags = {
      Project = "ask-david"
    }
  }

  assert {
    condition = alltrue([
      aws_flow_log.vpc.vpc_id == "vpc-0123456789abcdef0",
      aws_flow_log.vpc.traffic_type == "ALL",
      aws_flow_log.vpc.log_destination_type == "cloud-watch-logs",
    ])
    error_message = "VPC Flow Logs must capture all VPC traffic in the approved CloudWatch log group."
  }

  assert {
    condition = alltrue([
      strcontains(aws_iam_role.vpc_flow_logs.assume_role_policy, "vpc-flow-logs.amazonaws.com"),
      strcontains(local.vpc_flow_logs_delivery_policy, "logs:PutLogEvents"),
      strcontains(
        local.vpc_flow_logs_delivery_policy,
        "arn:aws:logs:ap-southeast-1:123456789012:log-group:/ask-david-development/vpc-flow:*",
      ),
    ])
    error_message = "The VPC Flow Logs delivery role must trust only the VPC Flow Logs service and write logs."
  }

  assert {
    condition = alltrue([
      aws_cloudwatch_metric_alarm.rds_cpu_high.alarm_name == "ask-david-development-rds-cpu-high",
      aws_cloudwatch_metric_alarm.rds_cpu_high.namespace == "AWS/RDS",
      aws_cloudwatch_metric_alarm.rds_cpu_high.metric_name == "CPUUtilization",
      aws_cloudwatch_metric_alarm.rds_cpu_high.statistic == "Average",
      aws_cloudwatch_metric_alarm.rds_cpu_high.unit == "Percent",
      aws_cloudwatch_metric_alarm.rds_cpu_high.comparison_operator == "GreaterThanThreshold",
      aws_cloudwatch_metric_alarm.rds_cpu_high.period == 60,
      aws_cloudwatch_metric_alarm.rds_cpu_high.evaluation_periods == 5,
      aws_cloudwatch_metric_alarm.rds_cpu_high.datapoints_to_alarm == 5,
      aws_cloudwatch_metric_alarm.rds_cpu_high.threshold == 90,
      aws_cloudwatch_metric_alarm.rds_cpu_high.treat_missing_data == "missing",
      aws_cloudwatch_metric_alarm.rds_cpu_high.dimensions["DBInstanceIdentifier"] == "ask-david-development-postgres",
    ])
    error_message = "The base alarm must monitor sustained average CPU for only the managed RDS instance."
  }

  assert {
    condition = alltrue([
      aws_cloudwatch_metric_alarm.rds_cpu_high.actions_enabled,
      length(aws_cloudwatch_metric_alarm.rds_cpu_high.alarm_actions) == 1,
      length(aws_cloudwatch_metric_alarm.rds_cpu_high.ok_actions) == 0,
      length(aws_cloudwatch_metric_alarm.rds_cpu_high.insufficient_data_actions) == 0,
    ])
    error_message = "The base alarm must use only the existing encrypted alert topic and no OK or insufficient-data action."
  }
}

run "rds_cpu_alarm_rejects_zero_threshold" {
  command = plan

  variables {
    name_prefix                     = "ask-david-development"
    vpc_id                          = "vpc-0123456789abcdef0"
    retention_days                  = 30
    kms_key_arn                     = "arn:aws:kms:ap-southeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
    account_id                      = "123456789012"
    region                          = "ap-southeast-1"
    rds_instance_identifier         = "ask-david-development-postgres"
    rds_cpu_alarm_threshold_percent = 0
    tags = {
      Project = "ask-david"
    }
  }

  expect_failures = [var.rds_cpu_alarm_threshold_percent]
}

run "rds_cpu_alarm_rejects_threshold_above_one_hundred" {
  command = plan

  variables {
    name_prefix                     = "ask-david-development"
    vpc_id                          = "vpc-0123456789abcdef0"
    retention_days                  = 30
    kms_key_arn                     = "arn:aws:kms:ap-southeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
    account_id                      = "123456789012"
    region                          = "ap-southeast-1"
    rds_instance_identifier         = "ask-david-development-postgres"
    rds_cpu_alarm_threshold_percent = 101
    tags = {
      Project = "ask-david"
    }
  }

  expect_failures = [var.rds_cpu_alarm_threshold_percent]
}
