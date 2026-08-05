locals {
  name_prefix = "${var.project}-${var.environment}"
  tags = merge({
    Project            = var.project
    Environment        = var.environment
    Component          = "platform-foundation"
    ManagedBy          = "terraform"
    Purpose            = "platform-foundation"
    DataClassification = "synthetic-only"
  }, var.additional_tags)
}
