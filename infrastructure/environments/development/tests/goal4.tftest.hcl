mock_provider "aws" {
  mock_data "aws_iam_policy_document" {
    defaults = {
      json = "{\"Version\":\"2012-10-17\",\"Statement\":[]}"
    }
  }

  mock_resource "aws_iam_role" {
    override_during = plan

    defaults = {
      arn = "arn:aws:iam::123456789012:role/ask-david-development-unity-catalog-storage"
    }
  }
}

mock_provider "databricks" {
  alias = "workspace"

  mock_data "databricks_current_metastore" {
    defaults = {
      id = "11111111-1111-1111-1111-111111111111"
    }
  }

  mock_data "databricks_sql_warehouse" {
    defaults = {
      id                        = "mock-warehouse-id"
      enable_serverless_compute = true
      max_num_clusters          = 1
      auto_stop_mins            = 10
    }
  }

  mock_resource "databricks_storage_credential" {
    defaults = {
      id   = "ask-david-development-managed-iceberg"
      name = "ask-david-development-managed-iceberg"
      aws_iam_role = [{
        external_id           = "mock-external-id"
        role_arn              = "arn:aws:iam::123456789012:role/ask-david-development-unity-catalog-storage"
        unity_catalog_iam_arn = "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-mock"
      }]
    }
  }
}

mock_provider "databricks" {
  alias = "account"
}

variables {
  aws_account_id = "123456789012"
  aws_region     = "ap-southeast-1"
  project        = "ask-david"
  environment    = "development"
  additional_tags = {
    Owner      = "platform-team"
    CostCenter = "development"
  }
  vpc_cidr                              = "10.42.0.0/16"
  public_subnet_cidr                    = "10.42.0.0/24"
  application_subnet_cidrs              = ["10.42.16.0/20", "10.42.32.0/20"]
  data_subnet_cidrs                     = ["10.42.64.0/20", "10.42.80.0/20"]
  availability_zones                    = ["ap-southeast-1a", "ap-southeast-1b"]
  internal_ingress_cidrs                = ["10.42.0.0/16"]
  rds_instance_class                    = "db.t4g.micro"
  redis_node_type                       = "cache.t4g.micro"
  rds_deletion_protection               = true
  rds_skip_final_snapshot               = false
  log_retention_days                    = 30
  rds_cpu_alarm_threshold_percent       = 90
  enable_opensearch_foundation          = false
  opensearch_collection_prefix          = "ask-david"
  bucket_name_prefix                    = "ask-david-contract"
  databricks_workspace_host             = "https://dbc-example.cloud.databricks.com"
  databricks_workspace_id               = 1234567890123456
  databricks_metastore_id               = "11111111-1111-1111-1111-111111111111"
  databricks_governance_admin_user_name = "governance-admin@example.invalid"
  goal_6_enabled                        = false
  goal_6_verifier_tasks_enabled         = false
}

run "goal4_disabled_has_no_managed_root_markers" {
  command = plan

  variables {
    goal_4_stage                                = "disabled"
    goal_4_storage_role_self_assumption_enabled = false
  }

  assert {
    condition     = length(output.goal_4_managed_root_marker_keys) == 0
    error_message = "The checked-in disabled stage must not create managed-root markers."
  }
}

run "goal4_bootstrap_is_narrow" {
  command = plan

  variables {
    goal_4_stage                                = "bootstrap"
    goal_4_storage_role_self_assumption_enabled = false
  }

  assert {
    condition     = output.goal_4_storage_role_arn == "arn:aws:iam::123456789012:role/ask-david-development-unity-catalog-storage"
    error_message = "Bootstrap must create the deterministic Unity Catalog storage role."
  }

  assert {
    condition     = output.goal_4_catalog_name == null
    error_message = "Bootstrap must not create the Goal 4 catalog."
  }

  assert {
    condition     = length(output.goal_4_schema_names) == 0
    error_message = "Bootstrap must not create Goal 4 schemas."
  }

  assert {
    condition     = output.goal_4_storage_role_self_assumption_enabled == false
    error_message = "Initial bootstrap must leave storage-role self-assumption disabled."
  }

  assert {
    condition = output.goal_4_managed_root_marker_keys == {
      catalog           = "unity-catalog/development/catalog/"
      green_sm_ai       = "unity-catalog/development/green_sm_ai/"
      green_sm_business = "unity-catalog/development/green_sm_business/"
      green_sm_curated  = "unity-catalog/development/green_sm_curated/"
      green_sm_platform = "unity-catalog/development/green_sm_platform/"
      green_sm_raw      = "unity-catalog/development/green_sm_raw/"
      green_sm_sandbox  = "unity-catalog/development/green_sm_sandbox/"
    }
    error_message = "Bootstrap must create exactly the seven approved trailing-slash managed-root markers."
  }
}

run "goal4_bootstrap_self_assumption_is_explicit" {
  command = plan

  variables {
    goal_4_stage                                = "bootstrap"
    goal_4_storage_role_self_assumption_enabled = true
  }

  assert {
    condition     = output.goal_4_storage_role_self_assumption_enabled == true
    error_message = "The second bootstrap sub-step must explicitly enable self-assumption."
  }
}

run "goal4_active_rejects_disabled_self_assumption" {
  command = plan

  variables {
    goal_4_stage                                = "active"
    goal_4_storage_role_self_assumption_enabled = false
    databricks_account_id                       = "22222222-2222-2222-2222-222222222222"
    databricks_sql_warehouse_id                 = "mock-warehouse-id"
  }

  expect_failures = [
    var.goal_4_storage_role_self_assumption_enabled,
  ]
}

run "goal4_active_declares_approved_hierarchy" {
  command = plan

  variables {
    goal_4_stage                                = "active"
    goal_4_storage_role_self_assumption_enabled = true
    databricks_account_id                       = "22222222-2222-2222-2222-222222222222"
    databricks_sql_warehouse_id                 = "mock-warehouse-id"
  }

  assert {
    condition     = output.goal_4_catalog_name == "ask_david_development"
    error_message = "Active Goal 4 must create only the approved development catalog."
  }

  assert {
    condition = output.goal_4_schema_names == tolist([
      "green_sm_ai",
      "green_sm_business",
      "green_sm_curated",
      "green_sm_platform",
      "green_sm_raw",
      "green_sm_sandbox",
    ])
    error_message = "Active Goal 4 must expose exactly the six approved schemas."
  }

  assert {
    condition = output.goal_4_external_location_names == tolist([
      "ask-david-development-catalog",
      "ask-david-development-green-sm-ai",
      "ask-david-development-green-sm-business",
      "ask-david-development-green-sm-curated",
      "ask-david-development-green-sm-platform",
      "ask-david-development-green-sm-raw",
      "ask-david-development-green-sm-sandbox",
    ])
    error_message = "Active Goal 4 must expose exactly the seven approved logical managed-storage roots."
  }

  assert {
    condition = output.goal_5_source_external_location_names == tolist([
      "ask-david-development-goal5-document-sources",
      "ask-david-development-goal5-raw-sources",
    ])
    error_message = "Goal 5 must expose only the two approved read-only synthetic source locations."
  }
}
