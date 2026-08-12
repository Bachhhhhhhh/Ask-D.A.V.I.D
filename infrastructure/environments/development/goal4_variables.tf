variable "goal_4_stage" {
  type        = string
  default     = "disabled"
  description = "Goal 4 rollout gate: disabled, bootstrap, or active."

  validation {
    condition     = contains(["disabled", "bootstrap", "active"], var.goal_4_stage)
    error_message = "goal_4_stage must be disabled, bootstrap, or active."
  }
}

variable "goal_4_storage_role_self_assumption_enabled" {
  type        = bool
  default     = false
  description = "Bootstrap sub-step gate: add storage-role self-assumption only after the initial role apply succeeds."

  validation {
    condition = (
      var.goal_4_stage != "active" ||
      var.goal_4_storage_role_self_assumption_enabled
    )
    error_message = "Goal 4 active requires the storage-role self-assumption bootstrap sub-step to be enabled first."
  }
}

variable "databricks_workspace_host" {
  type        = string
  default     = null
  nullable    = true
  description = "Approved development workspace URL; required when Goal 4 is enabled."

  validation {
    condition = (
      var.goal_4_stage == "disabled" ||
      (var.databricks_workspace_host != null && can(regex(
        "^https://[a-z0-9.-]+\\.cloud\\.databricks\\.com/?$",
        var.databricks_workspace_host,
      )))
    )
    error_message = "databricks_workspace_host must be an AWS Databricks HTTPS workspace URL when Goal 4 is enabled."
  }
}

variable "databricks_workspace_profile" {
  type        = string
  default     = "ask-david-development"
  description = "Named OAuth profile for the approved development workspace."

  validation {
    condition     = var.goal_4_stage == "disabled" || trimspace(var.databricks_workspace_profile) != ""
    error_message = "databricks_workspace_profile must not be empty when Goal 4 is enabled."
  }
}

variable "databricks_account_profile" {
  type        = string
  default     = "ask-david-account"
  description = "Named OAuth profile for Databricks account-level identity resources."

  validation {
    condition     = var.goal_4_stage != "active" || trimspace(var.databricks_account_profile) != ""
    error_message = "databricks_account_profile must not be empty in the active stage."
  }
}

variable "databricks_account_id" {
  type        = string
  default     = null
  nullable    = true
  description = "Databricks account ID; required when Goal 4 is active."

  validation {
    condition = (
      var.goal_4_stage != "active" ||
      (var.databricks_account_id != null && can(regex(
        "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        var.databricks_account_id,
      )))
    )
    error_message = "databricks_account_id must be a UUID when Goal 4 is active."
  }
}

variable "databricks_workspace_id" {
  type        = number
  default     = null
  nullable    = true
  description = "Approved development workspace numeric ID."

  validation {
    condition = (
      var.goal_4_stage == "disabled" ||
      (var.databricks_workspace_id != null && var.databricks_workspace_id > 0)
    )
    error_message = "databricks_workspace_id must be a positive number when Goal 4 is enabled."
  }
}

variable "databricks_metastore_id" {
  type        = string
  default     = null
  nullable    = true
  description = "Existing Unity Catalog metastore ID that must be reused."

  validation {
    condition = (
      var.goal_4_stage == "disabled" ||
      (var.databricks_metastore_id != null && can(regex(
        "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        var.databricks_metastore_id,
      )))
    )
    error_message = "databricks_metastore_id must be a UUID when Goal 4 is enabled."
  }
}

variable "databricks_sql_warehouse_id" {
  type        = string
  default     = null
  nullable    = true
  description = "Existing approved Serverless SQL Warehouse ID."

  validation {
    condition = (
      var.goal_4_stage != "active" ||
      (var.databricks_sql_warehouse_id != null && trimspace(var.databricks_sql_warehouse_id) != "")
    )
    error_message = "databricks_sql_warehouse_id must not be empty in the active stage."
  }
}

variable "databricks_governance_admin_user_name" {
  type        = string
  default     = null
  nullable    = true
  description = "Existing account user to place in the development governance-admin group."

  validation {
    condition = (
      var.goal_4_stage == "disabled" ||
      (var.databricks_governance_admin_user_name != null && trimspace(var.databricks_governance_admin_user_name) != "")
    )
    error_message = "databricks_governance_admin_user_name must not be empty when Goal 4 is enabled."
  }
}

variable "databricks_catalog_name" {
  type        = string
  default     = "ask_david_development"
  description = "Approved Goal 4 development catalog name."

  validation {
    condition     = var.databricks_catalog_name == "ask_david_development"
    error_message = "Goal 4 development must use the approved ask_david_development catalog."
  }
}
