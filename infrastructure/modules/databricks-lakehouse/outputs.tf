output "catalog_name" {
  value = try(databricks_catalog.this[0].name, null)
}

output "schema_names" {
  value = sort(keys(databricks_schema.this))
}

output "external_location_names" {
  value = sort([
    for key, location in databricks_external_location.this : location.name
    if contains(keys(var.managed_external_location_urls), key)
  ])
}

output "source_external_location_names" {
  value = sort([
    for key, location in databricks_external_location.this : location.name
    if contains(keys(var.source_external_location_urls), key)
  ])
}
