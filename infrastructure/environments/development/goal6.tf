# Goal 6 is disabled by default. Its persistent development resources can only
# appear in a separately reviewed saved plan after all image/AMI inputs exist.
module "doris_serving" {
  source = "../../modules/doris-serving"

  enabled                   = var.goal_6_enabled
  name_prefix               = local.name_prefix
  region                    = var.aws_region
  vpc_id                    = module.network.vpc_id
  data_subnet_id            = var.goal_6_data_subnet_id
  fe_private_ip             = var.goal_6_fe_private_ip
  be_private_ip             = var.goal_6_be_private_ip
  data_kms_key_arn          = module.kms.data_key_arn
  observability_kms_key_arn = module.kms.observability_key_arn
  log_retention_days        = var.log_retention_days
  fe_instance_type          = var.goal_6_fe_instance_type
  be_instance_type          = var.goal_6_be_instance_type
  ami_id                    = var.goal_6_ami_id
  fe_image                  = var.goal_6_fe_image
  be_image                  = var.goal_6_be_image
  fe_data_volume_gib        = var.goal_6_fe_data_volume_gib
  be_data_volume_gib        = var.goal_6_be_data_volume_gib
  rebuild_serving_state     = var.goal_6_rebuild_serving_state
  fe_root_volume_gib        = var.goal_6_fe_root_volume_gib
  be_root_volume_gib        = var.goal_6_be_root_volume_gib
  be_bootstrap_generation   = var.goal_6_be_bootstrap_generation
  fe_bootstrap_generation   = var.goal_6_fe_bootstrap_generation
  admin_secret_arn          = lookup(module.secrets.secret_arns, "doris/admin", null)
  query_secret_arn          = lookup(module.secrets.secret_arns, "doris/query", null)
  priority_networks         = var.vpc_cidr
  tags                      = local.tags

  depends_on = [
    aws_secretsmanager_secret_version.goal6_doris_admin,
    aws_secretsmanager_secret_version.goal6_doris_query,
  ]
}

module "doris_verifier" {
  source = "../../modules/doris-verifier"

  enabled                   = var.goal_6_enabled
  task_definitions_enabled  = var.goal_6_verifier_tasks_enabled
  name_prefix               = local.name_prefix
  region                    = var.aws_region
  vpc_id                    = module.network.vpc_id
  fe_security_group_id      = module.doris_serving.fe_security_group_id
  fe_private_ip             = module.doris_serving.fe_private_ip
  be_private_ip             = module.doris_serving.be_private_ip
  databricks_workspace_host = trimsuffix(coalesce(var.databricks_workspace_host, ""), "/")
  doris_log_group_name      = module.doris_serving.log_group_name
  doris_log_group_arn       = module.doris_serving.log_group_arn
  execution_role_arn        = module.iam.task_execution_role_arn
  admin_secret_arn          = lookup(module.secrets.secret_arns, "doris/admin", null)
  oauth_secret_arn          = lookup(module.secrets.secret_arns, "doris/external-read-oauth", null)
  query_secret_arn          = lookup(module.secrets.secret_arns, "doris/query", null)
  image                     = var.goal_6_verifier_image
  tags                      = local.tags

  depends_on = [
    aws_secretsmanager_secret_version.goal6_doris_admin,
    aws_secretsmanager_secret_version.goal6_doris_query,
    aws_secretsmanager_secret_version.goal6_external_read_oauth,
  ]
}

resource "aws_vpc_security_group_ingress_rule" "goal6_admin_to_aws_endpoints" {
  count = var.goal_6_enabled ? 1 : 0

  security_group_id            = module.network.aws_endpoints_security_group_id
  referenced_security_group_id = module.doris_verifier.admin_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 443
  to_port                      = 443
  description                  = "Goal 6 admin task access to existing private AWS interface endpoints only."
}

# The read-only verifier needs the same private interface-endpoint path only
# to inject its exact query secret before it can perform its bounded FE check.
# This remains SG-to-SG, TCP/443 only; no CIDR or public ingress is introduced.
resource "aws_vpc_security_group_ingress_rule" "goal6_verifier_to_aws_endpoints" {
  count = var.goal_6_enabled ? 1 : 0

  security_group_id            = module.network.aws_endpoints_security_group_id
  referenced_security_group_id = module.doris_verifier.verifier_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 443
  to_port                      = 443
  description                  = "Goal 6 read-only verifier access to existing private AWS interface endpoints only."
}

resource "aws_vpc_security_group_ingress_rule" "goal6_admin_to_fe_mysql" {
  count = var.goal_6_enabled ? 1 : 0

  security_group_id            = module.doris_serving.fe_security_group_id
  referenced_security_group_id = module.doris_verifier.admin_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 9030
  to_port                      = 9030
  description                  = "Goal 6 admin refresh only; Doris TLS is mandatory."
}

resource "aws_vpc_security_group_ingress_rule" "goal6_admin_to_fe_health" {
  count = var.goal_6_enabled ? 1 : 0

  security_group_id            = module.doris_serving.fe_security_group_id
  referenced_security_group_id = module.doris_verifier.admin_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 8030
  to_port                      = 8030
  description                  = "Goal 6 private admin health inspection only."
}

resource "aws_vpc_security_group_ingress_rule" "goal6_verifier_to_fe_mysql" {
  count = var.goal_6_enabled ? 1 : 0

  security_group_id            = module.doris_serving.fe_security_group_id
  referenced_security_group_id = module.doris_verifier.verifier_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 9030
  to_port                      = 9030
  description                  = "Goal 6 read-only verifier only; Doris TLS is mandatory."
}

resource "aws_s3_object" "goal6_increment_fixture" {
  count        = var.goal_6_enabled ? 1 : 0
  bucket       = module.storage.bucket_names["raw"]
  key          = "unity-catalog/development/goal5/structured/goal6_increment.csv"
  source       = "${path.root}/../../../synthetic_data/goal_06/structured/goal6_increment.csv"
  source_hash  = filebase64sha256("${path.root}/../../../synthetic_data/goal_06/structured/goal6_increment.csv")
  content_type = "text/csv"

  server_side_encryption = "aws:kms"
  kms_key_id             = module.kms.storage_key_arn

  tags = merge(local.tags, {
    Goal               = "goal-06"
    DataClassification = "synthetic-only"
    SourcePattern      = "controlled-serving-increment"
  })
}
