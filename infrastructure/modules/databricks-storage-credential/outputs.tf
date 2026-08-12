output "id" {
  value = try(databricks_storage_credential.this[0].id, null)
}

output "name" {
  value = try(databricks_storage_credential.this[0].name, null)
}

output "external_id" {
  value     = try(databricks_storage_credential.this[0].aws_iam_role[0].external_id, null)
  sensitive = true
}

output "unity_catalog_iam_arn" {
  value = try(
    databricks_storage_credential.this[0].aws_iam_role[0].unity_catalog_iam_arn,
    null,
  )
}
