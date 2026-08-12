output "vpc_id" { value = module.network.vpc_id }
output "task_execution_role_arn" { value = module.iam.task_execution_role_arn }
output "workload_role_arn" { value = module.iam.workload_role_arn }
output "ecs_cluster_name" { value = module.runtime.cluster_name }
output "application_subnet_ids" { value = module.network.application_subnet_ids }
output "workload_security_group_id" { value = module.network.workload_security_group_id }
output "smoke_security_group_id" { value = module.network.smoke_security_group_id }
output "smoke_task_definition_arns" { value = module.smoke_test.task_definition_arns }
output "alert_topic_arn" { value = module.observability.alert_topic_arn }
output "rds_cpu_alarm_name" { value = module.observability.rds_cpu_alarm_name }
output "storage_bucket_names" { value = module.storage.bucket_names }
output "storage_kms_key_arn" { value = module.kms.storage_key_arn }
output "goal_4_stage" { value = var.goal_4_stage }
output "goal_4_storage_role_arn" { value = module.databricks_aws_storage.role_arn }
output "goal_4_storage_role_self_assumption_enabled" {
  value = module.databricks_aws_storage.self_assumption_enabled
}
output "goal_4_managed_root_marker_keys" {
  value = module.databricks_aws_storage.managed_root_marker_keys
}
output "goal_4_storage_credential_name" { value = module.databricks_storage_credential.name }
output "goal_4_catalog_name" { value = module.databricks_lakehouse.catalog_name }
output "goal_4_schema_names" { value = module.databricks_lakehouse.schema_names }
output "goal_4_external_location_names" { value = module.databricks_lakehouse.external_location_names }
output "goal_4_workflow_service_principal_application_id" {
  value = module.databricks_identities.workflow_service_principal_application_id
}
output "goal_4_denied_service_principal_application_id" {
  value = module.databricks_identities.denied_service_principal_application_id
}
