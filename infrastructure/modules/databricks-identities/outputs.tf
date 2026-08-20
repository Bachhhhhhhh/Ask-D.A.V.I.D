output "governance_admin_group_name" {
  value = try(databricks_group.governance_admins[0].display_name, null)
}

output "data_engineer_group_name" {
  value = try(databricks_group.data_engineers[0].display_name, null)
}

output "business_reader_group_name" {
  value = try(databricks_group.business_readers[0].display_name, null)
}

output "workflow_service_principal_application_id" {
  value = try(databricks_service_principal.workflow[0].application_id, null)
}

output "denied_service_principal_application_id" {
  value = try(databricks_service_principal.denied_test[0].application_id, null)
}
output "doris_external_read_service_principal_application_id" {
  value = try(databricks_service_principal.doris_external_read[0].application_id, null)
}
output "doris_external_read_service_principal_secret" {
  value     = try(databricks_service_principal_secret.doris_external_read[0].secret, null)
  sensitive = true
}
