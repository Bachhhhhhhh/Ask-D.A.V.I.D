mock_provider "aws" {}
mock_provider "databricks" {
  alias = "workspace"
}
mock_provider "databricks" {
  alias = "account"
}

run "development_foundation_is_plannable" {
  command = plan

  variables {
    aws_account_id = "123456789012"
    aws_region     = "ap-southeast-1"
    project        = "ask-david"
    environment    = "development"
    additional_tags = {
      Owner      = "platform-team"
      CostCenter = "development"
    }
    vpc_cidr                        = "10.42.0.0/16"
    public_subnet_cidr              = "10.42.0.0/24"
    application_subnet_cidrs        = ["10.42.16.0/20", "10.42.32.0/20"]
    data_subnet_cidrs               = ["10.42.64.0/20", "10.42.80.0/20"]
    availability_zones              = ["ap-southeast-1a", "ap-southeast-1b"]
    internal_ingress_cidrs          = ["10.42.0.0/16"]
    rds_instance_class              = "db.t4g.micro"
    redis_node_type                 = "cache.t4g.micro"
    rds_deletion_protection         = true
    rds_skip_final_snapshot         = false
    log_retention_days              = 30
    rds_cpu_alarm_threshold_percent = 90
    enable_opensearch_foundation    = false
    opensearch_collection_prefix    = "ask-david"
    bucket_name_prefix              = "ask-david-contract"
    goal_4_stage                    = "disabled"
    goal_6_enabled                  = false
    goal_6_verifier_tasks_enabled   = false
  }

  assert {
    condition     = output.rds_cpu_alarm_name == "ask-david-development-rds-cpu-high"
    error_message = "Development must expose the Terraform-managed base RDS CPU alarm name."
  }
}

run "development_defines_static_synthetic_smoke_tasks" {
  command = plan

  variables {
    aws_account_id = "123456789012"
    aws_region     = "ap-southeast-1"
    project        = "ask-david"
    environment    = "development"
    additional_tags = {
      Owner      = "platform-team"
      CostCenter = "development"
    }
    vpc_cidr                        = "10.42.0.0/16"
    public_subnet_cidr              = "10.42.0.0/24"
    application_subnet_cidrs        = ["10.42.16.0/20", "10.42.32.0/20"]
    data_subnet_cidrs               = ["10.42.64.0/20", "10.42.80.0/20"]
    availability_zones              = ["ap-southeast-1a", "ap-southeast-1b"]
    internal_ingress_cidrs          = ["10.42.0.0/16"]
    rds_instance_class              = "db.t4g.micro"
    redis_node_type                 = "cache.t4g.micro"
    rds_deletion_protection         = true
    rds_skip_final_snapshot         = false
    log_retention_days              = 30
    rds_cpu_alarm_threshold_percent = 90
    enable_opensearch_foundation    = false
    opensearch_collection_prefix    = "ask-david"
    bucket_name_prefix              = "ask-david-contract"
    goal_4_stage                    = "disabled"
    goal_6_enabled                  = false
    goal_6_verifier_tasks_enabled   = false
  }

  assert {
    condition     = length(module.smoke_test.task_definition_families) == 3
    error_message = "Development must expose exactly three static smoke task definitions."
  }
}
