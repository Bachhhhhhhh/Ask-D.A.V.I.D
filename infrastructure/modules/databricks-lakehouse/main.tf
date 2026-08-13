resource "databricks_external_location" "this" {
  for_each = var.enabled ? merge(
    var.managed_external_location_urls,
    var.source_external_location_urls,
  ) : {}

  name            = "ask-david-development-${replace(each.key, "_", "-")}"
  url             = each.value
  credential_name = var.storage_credential_name
  owner           = var.governance_admin_group_name
  comment = contains(keys(var.source_external_location_urls), each.key) ? (
    "Ask DAVID development read-only synthetic ingestion source for ${each.key}"
  ) : "Ask DAVID development managed-Iceberg root for ${each.key}"
  isolation_mode  = "ISOLATION_MODE_ISOLATED"
  force_destroy   = false
  read_only       = contains(keys(var.source_external_location_urls), each.key)
  skip_validation = false
}

resource "databricks_workspace_binding" "external_locations" {
  for_each = databricks_external_location.this

  securable_name = each.value.name
  securable_type = "external_location"
  workspace_id   = var.workspace_id
  binding_type   = "BINDING_TYPE_READ_WRITE"
}

resource "databricks_catalog" "this" {
  count = var.enabled ? 1 : 0

  name           = var.catalog_name
  comment        = "Ask DAVID development catalog for neutral synthetic validation"
  owner          = var.governance_admin_group_name
  storage_root   = var.catalog_storage_root
  isolation_mode = "ISOLATED"
  force_destroy  = false
  properties = {
    data_classification = "synthetic-only"
    environment         = "development"
    managed_by          = "terraform"
    system_of_record    = "s3-apache-iceberg"
  }

  depends_on = [databricks_workspace_binding.external_locations]
}

resource "databricks_workspace_binding" "catalog" {
  count = var.enabled ? 1 : 0

  securable_name = databricks_catalog.this[0].name
  securable_type = "catalog"
  workspace_id   = var.workspace_id
  binding_type   = "BINDING_TYPE_READ_WRITE"
}

resource "databricks_schema" "this" {
  for_each = var.enabled ? var.schema_storage_roots : {}

  catalog_name  = databricks_catalog.this[0].name
  name          = each.key
  comment       = "Ask DAVID ${each.key} namespace for neutral synthetic validation"
  owner         = var.governance_admin_group_name
  storage_root  = each.value
  force_destroy = false
  properties = {
    data_classification = "synthetic-only"
    environment         = "development"
    managed_by          = "terraform"
    table_format        = "apache-iceberg"
  }

  depends_on = [databricks_workspace_binding.catalog]
}

resource "databricks_grants" "storage_credential" {
  count = var.enabled ? 1 : 0

  storage_credential = var.storage_credential_name

  grant {
    principal  = var.governance_admin_group_name
    privileges = ["CREATE_EXTERNAL_LOCATION"]
  }
}

resource "databricks_grants" "external_locations" {
  for_each = databricks_external_location.this

  external_location = each.value.name

  dynamic "grant" {
    for_each = contains(keys(var.managed_external_location_urls), each.key) ? [1] : []

    content {
      principal  = var.governance_admin_group_name
      privileges = ["CREATE_MANAGED_STORAGE"]
    }
  }

  dynamic "grant" {
    for_each = contains(keys(var.source_external_location_urls), each.key) ? [1] : []

    content {
      principal  = var.workflow_service_principal_application_id
      privileges = ["READ_FILES"]
    }
  }
}

resource "databricks_grants" "catalog" {
  count = var.enabled ? 1 : 0

  catalog = databricks_catalog.this[0].name

  grant {
    principal  = var.data_engineer_group_name
    privileges = ["USE_CATALOG"]
  }

  grant {
    principal  = var.business_reader_group_name
    privileges = ["USE_CATALOG"]
  }
}

resource "databricks_grants" "schemas" {
  for_each = databricks_schema.this

  schema = each.value.id

  grant {
    principal = var.data_engineer_group_name
    privileges = [
      "CREATE_TABLE",
      "MODIFY",
      "SELECT",
      "USE_SCHEMA",
    ]
  }

  dynamic "grant" {
    for_each = each.key == "green_sm_business" ? [1] : []
    content {
      principal  = var.business_reader_group_name
      privileges = ["SELECT", "USE_SCHEMA"]
    }
  }
}
