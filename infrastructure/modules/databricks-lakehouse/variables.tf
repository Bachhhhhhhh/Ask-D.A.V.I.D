variable "enabled" { type = bool }
variable "workspace_id" { type = number }
variable "catalog_name" { type = string }
variable "catalog_storage_root" { type = string }
variable "schema_storage_roots" { type = map(string) }
variable "managed_external_location_urls" { type = map(string) }
variable "source_external_location_urls" {
  description = "Read-only source locations for approved governed ingestion."
  type        = map(string)
  default     = {}
}
variable "storage_credential_name" { type = string }
variable "governance_admin_group_name" { type = string }
variable "data_engineer_group_name" { type = string }
variable "business_reader_group_name" { type = string }
variable "workflow_service_principal_application_id" {
  description = "Workflow service-principal application ID granted read-only source access."
  type        = string
}
