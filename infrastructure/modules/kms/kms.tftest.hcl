mock_provider "aws" {}

run "observability_key_policy_is_limited_to_approved_log_groups" {
  command = plan

  variables {
    name_prefix = "ask-david-development"
    account_id  = "123456789012"
    region      = "ap-southeast-1"
    tags = {
      Project = "ask-david"
    }
  }

  assert {
    condition = strcontains(
      aws_kms_key.observability.policy,
      "logs.ap-southeast-1.amazonaws.com",
    )
    error_message = "The observability key must retain the regional CloudWatch Logs service permission."
  }

  assert {
    condition = alltrue([
      strcontains(
        aws_kms_key.observability.policy,
        "arn:aws:logs:ap-southeast-1:123456789012:log-group:/ask-david-development/runtime",
      ),
      strcontains(
        aws_kms_key.observability.policy,
        "arn:aws:logs:ap-southeast-1:123456789012:log-group:/ask-david-development/vpc-flow",
      ),
    ])
    error_message = "The observability key must be limited to the approved runtime and VPC flow log groups."
  }

  assert {
    condition = alltrue([
      length(jsondecode(aws_kms_key.observability.policy).Statement) == 3,
      jsondecode(aws_kms_key.observability.policy).Statement[2].Sid == "AllowApprovedCloudWatchAlarmToUseEncryptedAlertTopic",
      jsondecode(aws_kms_key.observability.policy).Statement[2].Principal.Service == "cloudwatch.amazonaws.com",
      toset(jsondecode(aws_kms_key.observability.policy).Statement[2].Action) == toset([
        "kms:GenerateDataKey*",
        "kms:Decrypt",
      ]),
      jsondecode(aws_kms_key.observability.policy).Statement[2].Resource == "*",
      jsondecode(aws_kms_key.observability.policy).Statement[2].Condition.StringEquals["aws:SourceAccount"] == "123456789012",
      jsondecode(aws_kms_key.observability.policy).Statement[2].Condition.ArnEquals["aws:SourceArn"] == "arn:aws:cloudwatch:ap-southeast-1:123456789012:alarm:ask-david-development-rds-cpu-high",
      length(keys(jsondecode(aws_kms_key.observability.policy).Statement[2].Condition)) == 2,
    ])
    error_message = "Only the exact same-account RDS CPU alarm may use the observability key for encrypted SNS publishing."
  }
}
