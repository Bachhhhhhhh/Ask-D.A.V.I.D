# Goal 7's private indexer reads the governed outbox through the existing
# workflow service principal. The generated OAuth secret is stored only in the
# Terraform-managed, KMS-encrypted Secrets Manager container and injected by
# ECS; it is never an agent input or repository value.
resource "aws_secretsmanager_secret_version" "goal7_workflow_oauth" {
  count = (var.goal_7_indexer_task_enabled || var.goal_7_demo_task_enabled) ? 1 : 0

  secret_id = module.secrets.secret_arns["goal7/workflow-oauth"]
  secret_string = jsonencode({
    client_id     = module.databricks_identities.workflow_service_principal_application_id
    client_secret = module.databricks_identities.workflow_service_principal_secret
  })
}
