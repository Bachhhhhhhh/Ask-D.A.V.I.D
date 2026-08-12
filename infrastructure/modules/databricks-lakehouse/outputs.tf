output "catalog_name" {
  value = try(databricks_catalog.this[0].name, null)
}

output "schema_names" {
  value = sort(keys(databricks_schema.this))
}

output "external_location_names" {
  value = sort([for location in databricks_external_location.this : location.name])
}
