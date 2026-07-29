resource "aws_kms_key" "storage" {
  description             = "${var.name_prefix} S3 encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 30
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
  tags                    = var.tags
}
resource "aws_kms_alias" "observability" {
  name          = "alias/${var.name_prefix}-observability"
  target_key_id = aws_kms_key.observability.key_id
}
