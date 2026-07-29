locals { containers = toset(["runtime/config", "data-services/config", "opensearch/foundation"]) }
resource "aws_secretsmanager_secret" "this" {
  for_each                = local.containers
  name                    = "${var.name_prefix}/${each.key}"
  kms_key_id              = var.kms_key_id
  recovery_window_in_days = 30
  tags                    = merge(var.tags, { SecretPurpose = each.key })
}
