resource "databricks_storage_credential" "this" {
  count = var.enabled ? 1 : 0

  name            = var.name
  comment         = var.comment
  owner           = var.owner
  isolation_mode  = "ISOLATION_MODE_ISOLATED"
  force_destroy   = false
  skip_validation = var.skip_validation

  aws_iam_role {
    role_arn = var.iam_role_arn
  }
}

resource "databricks_workspace_binding" "this" {
  count = var.enabled && var.bind_to_workspace ? 1 : 0

  securable_name = databricks_storage_credential.this[0].name
  securable_type = "storage_credential"
  workspace_id   = var.workspace_id
  binding_type   = "BINDING_TYPE_READ_WRITE"
}
