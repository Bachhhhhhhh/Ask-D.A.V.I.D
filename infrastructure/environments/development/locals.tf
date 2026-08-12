locals {
  name_prefix              = "${var.project}-${var.environment}"
  goal_4_enabled           = var.goal_4_stage != "disabled"
  goal_4_active            = var.goal_4_stage == "active"
  goal_4_managed_prefix    = "unity-catalog/development"
  goal_4_storage_role_name = "${local.name_prefix}-unity-catalog-storage"
  goal_4_storage_role_arn = (
    "arn:aws:iam::${var.aws_account_id}:role/${local.goal_4_storage_role_name}"
  )
  goal_4_storage_credential_name = "${local.name_prefix}-managed-iceberg"

  goal_4_managed_root_prefixes = {
    catalog           = "${local.goal_4_managed_prefix}/catalog"
    green_sm_raw      = "${local.goal_4_managed_prefix}/green_sm_raw"
    green_sm_curated  = "${local.goal_4_managed_prefix}/green_sm_curated"
    green_sm_business = "${local.goal_4_managed_prefix}/green_sm_business"
    green_sm_ai       = "${local.goal_4_managed_prefix}/green_sm_ai"
    green_sm_platform = "${local.goal_4_managed_prefix}/green_sm_platform"
    green_sm_sandbox  = "${local.goal_4_managed_prefix}/green_sm_sandbox"
  }
  goal_4_managed_root_bucket_names = {
    catalog           = module.storage.bucket_names["artifacts"]
    green_sm_raw      = module.storage.bucket_names["raw"]
    green_sm_curated  = module.storage.bucket_names["curated"]
    green_sm_business = module.storage.bucket_names["business"]
    green_sm_ai       = module.storage.bucket_names["documents"]
    green_sm_platform = module.storage.bucket_names["audit"]
    green_sm_sandbox  = module.storage.bucket_names["artifacts"]
  }
  goal_4_bucket_arns = toset([
    for bucket_name in values(local.goal_4_managed_root_bucket_names) :
    "arn:aws:s3:::${bucket_name}"
  ])
  goal_4_managed_prefixes = toset(values(local.goal_4_managed_root_prefixes))
  goal_4_managed_object_arns = toset([
    for root_name, bucket_name in local.goal_4_managed_root_bucket_names :
    "arn:aws:s3:::${bucket_name}/${local.goal_4_managed_root_prefixes[root_name]}/*"
  ])
  goal_4_managed_root_markers = {
    for root_name, bucket_name in local.goal_4_managed_root_bucket_names :
    root_name => {
      bucket = bucket_name
      key    = "${local.goal_4_managed_root_prefixes[root_name]}/"
    }
  }
  goal_4_external_location_urls = {
    for root_name, bucket_name in local.goal_4_managed_root_bucket_names :
    root_name => "s3://${bucket_name}/${local.goal_4_managed_root_prefixes[root_name]}"
  }
  goal_4_catalog_storage_root = local.goal_4_external_location_urls["catalog"]
  goal_4_schema_storage_roots = {
    for schema_name in keys(local.goal_4_managed_root_prefixes) :
    schema_name => local.goal_4_external_location_urls[schema_name]
    if schema_name != "catalog"
  }
  goal_4_governance_admin_group_name = "${local.name_prefix}-governance-admins"
  goal_4_data_engineer_group_name    = "${local.name_prefix}-data-engineers"
  goal_4_business_reader_group_name  = "${local.name_prefix}-business-readers"
  goal_4_workflow_service_principal_name = (
    "${local.name_prefix}-lakehouse-workflow"
  )
  goal_4_denied_service_principal_name = "${local.name_prefix}-denied-test"

  tags = merge({
    Project            = var.project
    Environment        = var.environment
    Component          = "platform-foundation"
    ManagedBy          = "terraform"
    Purpose            = "platform-foundation"
    DataClassification = "synthetic-only"
  }, var.additional_tags)
}
