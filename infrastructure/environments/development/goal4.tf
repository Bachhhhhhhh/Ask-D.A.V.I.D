data "databricks_current_metastore" "this" {
  count    = local.goal_4_enabled ? 1 : 0
  provider = databricks.workspace
}

data "databricks_sql_warehouse" "this" {
  count    = local.goal_4_active ? 1 : 0
  provider = databricks.workspace
  id       = var.databricks_sql_warehouse_id
}

module "databricks_storage_credential" {
  source = "../../modules/databricks-storage-credential"

  providers = {
    databricks = databricks.workspace
  }

  enabled           = local.goal_4_enabled
  name              = local.goal_4_storage_credential_name
  iam_role_arn      = local.goal_4_storage_role_arn
  owner             = local.goal_4_active ? local.goal_4_governance_admin_group_name : var.databricks_governance_admin_user_name
  workspace_id      = var.databricks_workspace_id
  bind_to_workspace = local.goal_4_active
  skip_validation   = var.goal_4_stage == "bootstrap"

  depends_on = [module.databricks_identities]
}

module "databricks_aws_storage" {
  source = "../../modules/databricks-aws-storage"

  enabled               = local.goal_4_enabled
  account_id            = var.aws_account_id
  role_name             = local.goal_4_storage_role_name
  bucket_arns           = local.goal_4_bucket_arns
  managed_prefixes      = local.goal_4_managed_prefixes
  managed_object_arns   = local.goal_4_managed_object_arns
  managed_root_markers  = local.goal_4_managed_root_markers
  storage_kms_key_arn   = module.kms.storage_key_arn
  external_id           = module.databricks_storage_credential.external_id
  unity_catalog_iam_arn = module.databricks_storage_credential.unity_catalog_iam_arn
  self_assumption_enabled = (
    var.goal_4_storage_role_self_assumption_enabled
  )
  tags = local.tags
}

module "databricks_identities" {
  source = "../../modules/databricks-identities"

  providers = {
    databricks.account   = databricks.account
    databricks.workspace = databricks.workspace
  }

  enabled                         = local.goal_4_active
  databricks_account_id           = var.databricks_account_id
  workspace_id                    = var.databricks_workspace_id
  governance_admin_user_name      = var.databricks_governance_admin_user_name
  governance_admin_group_name     = local.goal_4_governance_admin_group_name
  data_engineer_group_name        = local.goal_4_data_engineer_group_name
  business_reader_group_name      = local.goal_4_business_reader_group_name
  workflow_service_principal_name = local.goal_4_workflow_service_principal_name
  denied_service_principal_name   = local.goal_4_denied_service_principal_name
}

module "databricks_lakehouse" {
  source = "../../modules/databricks-lakehouse"

  providers = {
    databricks = databricks.workspace
  }

  enabled                     = local.goal_4_active
  workspace_id                = var.databricks_workspace_id
  catalog_name                = var.databricks_catalog_name
  catalog_storage_root        = local.goal_4_catalog_storage_root
  schema_storage_roots        = local.goal_4_schema_storage_roots
  external_location_urls      = local.goal_4_external_location_urls
  storage_credential_name     = module.databricks_storage_credential.name
  governance_admin_group_name = module.databricks_identities.governance_admin_group_name
  data_engineer_group_name    = module.databricks_identities.data_engineer_group_name
  business_reader_group_name  = module.databricks_identities.business_reader_group_name

  depends_on = [module.databricks_aws_storage]
}

check "goal_4_reuses_expected_metastore" {
  assert {
    condition = (
      !local.goal_4_enabled ||
      data.databricks_current_metastore.this[0].id == var.databricks_metastore_id
    )
    error_message = "The workspace is not attached to the approved existing Unity Catalog metastore."
  }
}

check "goal_4_reuses_serverless_sql_warehouse" {
  assert {
    condition = (
      !local.goal_4_active ||
      (
        data.databricks_sql_warehouse.this[0].enable_serverless_compute &&
        data.databricks_sql_warehouse.this[0].max_num_clusters == 1 &&
        data.databricks_sql_warehouse.this[0].auto_stop_mins <= 10
      )
    )
    error_message = "Goal 4 requires the approved serverless, max-one-cluster, auto-stopping SQL warehouse."
  }
}
