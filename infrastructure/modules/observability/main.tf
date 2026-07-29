resource "aws_cloudwatch_log_group" "vpc_flow" {
  name              = "/${var.name_prefix}/vpc-flow"
  retention_in_days = var.retention_days
  kms_key_id        = var.kms_key_arn
  tags              = merge(var.tags, { VpcId = var.vpc_id })
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
