module "network" {
  source                   = "../../modules/network"
  name_prefix              = local.name_prefix
  vpc_cidr                 = var.vpc_cidr
  public_subnet_cidr       = var.public_subnet_cidr
  application_subnet_cidrs = var.application_subnet_cidrs
  data_subnet_cidrs        = var.data_subnet_cidrs
  availability_zones       = var.availability_zones
  internal_ingress_cidrs   = var.internal_ingress_cidrs
  nat_gateway_mode         = var.nat_gateway_mode
  tags                     = local.tags
}
module "kms" {
  source                  = "../../modules/kms"
  name_prefix             = local.name_prefix
  account_id              = var.aws_account_id
  region                  = var.aws_region
  storage_access_role_arn = local.goal_4_enabled ? module.databricks_aws_storage.role_arn : null
  tags                    = local.tags
}
module "storage" {
  source             = "../../modules/storage"
  name_prefix        = local.name_prefix
  bucket_name_prefix = var.bucket_name_prefix
  account_id         = var.aws_account_id
  region             = var.aws_region
  kms_key_arn        = module.kms.storage_key_arn
  tags               = local.tags
}
module "secrets" {
  source      = "../../modules/secrets"
  name_prefix = local.name_prefix
  kms_key_id  = module.kms.secrets_key_id
  tags        = local.tags
}
module "runtime" {
  source                 = "../../modules/runtime"
  name_prefix            = local.name_prefix
  application_subnet_ids = module.network.application_subnet_ids
  alb_security_group_id  = module.network.alb_security_group_id
  tags                   = local.tags
}
module "data_services" {
  source                  = "../../modules/data-services"
  name_prefix             = local.name_prefix
  data_subnet_ids         = module.network.data_subnet_ids
  rds_security_group_id   = module.network.rds_security_group_id
  redis_security_group_id = module.network.redis_security_group_id
  kms_key_arn             = module.kms.data_key_arn
  rds_instance_class      = var.rds_instance_class
  redis_node_type         = var.redis_node_type
  rds_deletion_protection = var.rds_deletion_protection
  rds_skip_final_snapshot = var.rds_skip_final_snapshot
  tags                    = local.tags
}
module "observability" {
  source                          = "../../modules/observability"
  name_prefix                     = local.name_prefix
  vpc_id                          = module.network.vpc_id
  retention_days                  = var.log_retention_days
  kms_key_arn                     = module.kms.observability_key_arn
  account_id                      = var.aws_account_id
  region                          = var.aws_region
  rds_instance_identifier         = module.data_services.rds_instance_identifier
  rds_cpu_alarm_threshold_percent = var.rds_cpu_alarm_threshold_percent
  tags                            = local.tags
}
module "iam" {
  source                = "../../modules/iam"
  name_prefix           = local.name_prefix
  runtime_log_group_arn = module.observability.runtime_log_group_arn
  tags                  = local.tags
}
module "ecr_pull_through" {
  source = "../../modules/ecr-pull-through"
}
module "smoke_test" {
  source = "../../modules/smoke-test"

  name_prefix           = local.name_prefix
  account_id            = var.aws_account_id
  region                = var.aws_region
  runtime_log_group_arn = module.observability.runtime_log_group_arn
  rds_endpoint          = module.data_services.rds_endpoint
  rds_master_secret_arn = module.data_services.rds_master_secret_arn
  redis_endpoint        = module.data_services.redis_endpoint
  raw_bucket_name       = module.storage.bucket_names["raw"]
  curated_bucket_name   = module.storage.bucket_names["curated"]
  tags                  = local.tags

  depends_on = [module.ecr_pull_through]
}
module "opensearch_foundation" {
  source             = "../../modules/opensearch-foundation"
  enabled            = var.enable_opensearch_foundation
  name_prefix        = local.name_prefix
  collection_prefix  = var.opensearch_collection_prefix
  vpc_id             = module.network.vpc_id
  subnet_ids         = module.network.application_subnet_ids
  security_group_ids = [module.network.aoss_endpoint_security_group_id]
}
