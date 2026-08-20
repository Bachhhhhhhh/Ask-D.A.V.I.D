# Passwords and OAuth secrets are sensitive Terraform state values only. They
# are never outputs and this file contains no literal secret material.
resource "random_password" "goal6_doris_admin" {
  count            = var.goal_6_enabled ? 1 : 0
  length           = 40
  special          = true
  override_special = "_%@+="
}

resource "random_password" "goal6_doris_query" {
  count            = var.goal_6_enabled ? 1 : 0
  length           = 40
  special          = true
  override_special = "_%@+="
}

resource "aws_secretsmanager_secret_version" "goal6_doris_admin" {
  count = var.goal_6_enabled ? 1 : 0

  secret_id = module.secrets.secret_arns["doris/admin"]
  secret_string = jsonencode({
    username = "doris_goal6_admin"
    password = random_password.goal6_doris_admin[0].result
  })
}

resource "aws_secretsmanager_secret_version" "goal6_doris_query" {
  count = var.goal_6_enabled ? 1 : 0

  secret_id = module.secrets.secret_arns["doris/query"]
  secret_string = jsonencode({
    username = "doris_goal6_query"
    password = random_password.goal6_doris_query[0].result
  })
}

resource "aws_secretsmanager_secret_version" "goal6_external_read_oauth" {
  count = var.goal_6_enabled ? 1 : 0

  secret_id = module.secrets.secret_arns["doris/external-read-oauth"]
  secret_string = jsonencode({
    client_id     = module.databricks_identities.doris_external_read_service_principal_application_id
    client_secret = module.databricks_identities.doris_external_read_service_principal_secret
  })
}
