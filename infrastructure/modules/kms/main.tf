locals {
  observability_log_group_arns = [
    "arn:aws:logs:${var.region}:${var.account_id}:log-group:/${var.name_prefix}/runtime",
    "arn:aws:logs:${var.region}:${var.account_id}:log-group:/${var.name_prefix}/vpc-flow",
  ]
  rds_cpu_alarm_arn = "arn:aws:cloudwatch:${var.region}:${var.account_id}:alarm:${var.name_prefix}-rds-cpu-high"

  storage_key_policy = var.storage_access_role_arn == null ? null : jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnableAccountRootPermissions"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::${var.account_id}:root" }
        Action    = "kms:*"
        Resource  = "*"
      },
      {
        Sid       = "AllowUnityCatalogStorageUse"
        Effect    = "Allow"
        Principal = { AWS = var.storage_access_role_arn }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:GenerateDataKeyWithoutPlaintext",
          "kms:ReEncryptFrom",
          "kms:ReEncryptTo",
        ]
        Resource = "*"
      },
    ]
  })

  observability_key_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnableAccountRootPermissions"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::${var.account_id}:root" }
        Action    = "kms:*"
        Resource  = "*"
      },
      {
        Sid    = "AllowCloudWatchLogsForApprovedGroups"
        Effect = "Allow"
        Principal = {
          Service = "logs.${var.region}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:Describe*",
        ]
        Resource = "*"
        Condition = {
          ArnEquals = {
            "kms:EncryptionContext:aws:logs:arn" = local.observability_log_group_arns
          }
        }
      },
      {
        Sid    = "AllowApprovedCloudWatchAlarmToUseEncryptedAlertTopic"
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action = [
          "kms:GenerateDataKey*",
          "kms:Decrypt",
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = var.account_id
          }
          ArnEquals = {
            "aws:SourceArn" = local.rds_cpu_alarm_arn
          }
        }
      },
    ]
  })
}

resource "aws_kms_key" "storage" {
  description             = "${var.name_prefix} S3 encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = local.storage_key_policy
  tags                    = var.tags
}
resource "aws_kms_alias" "storage" {
  name          = "alias/${var.name_prefix}-storage"
  target_key_id = aws_kms_key.storage.key_id
}
resource "aws_kms_key" "data" {
  description             = "${var.name_prefix} data-service encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  tags                    = var.tags
}
resource "aws_kms_alias" "data" {
  name          = "alias/${var.name_prefix}-data"
  target_key_id = aws_kms_key.data.key_id
}
resource "aws_kms_key" "secrets" {
  description             = "${var.name_prefix} Secrets Manager encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  tags                    = var.tags
}
resource "aws_kms_alias" "secrets" {
  name          = "alias/${var.name_prefix}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}
resource "aws_kms_key" "observability" {
  description             = "${var.name_prefix} log encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = local.observability_key_policy
  tags                    = var.tags
}
resource "aws_kms_alias" "observability" {
  name          = "alias/${var.name_prefix}-observability"
  target_key_id = aws_kms_key.observability.key_id
}
