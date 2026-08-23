variable "enabled" { type = bool }
variable "databricks_account_id" { type = string }
variable "workspace_id" { type = number }
variable "governance_admin_user_name" { type = string }
variable "governance_admin_group_name" { type = string }
variable "data_engineer_group_name" { type = string }
variable "business_reader_group_name" { type = string }
variable "workflow_service_principal_name" { type = string }
variable "denied_service_principal_name" { type = string }
variable "doris_external_read_service_principal_name" {
  description = "Goal 6 external-read principal. Null keeps the Doris scope disabled."
  type        = string
  default     = null
  nullable    = true
}

variable "goal7_indexer_enabled" {
  description = "Create the workflow OAuth secret only when the Goal 7 indexer task is enabled."
  type        = bool
  default     = false
}
