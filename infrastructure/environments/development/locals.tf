locals {
  name_prefix = "${var.project}-${var.environment}"
  tags = merge({
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "Terraform"
    Purpose     = "platform-foundation"
    DataClass   = "synthetic-only"
  }, var.additional_tags)
}
