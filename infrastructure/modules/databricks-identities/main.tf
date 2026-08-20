data "databricks_user" "governance_admin" {
  count = var.enabled ? 1 : 0

  provider  = databricks.account
  user_name = var.governance_admin_user_name
}

resource "databricks_group" "governance_admins" {
  count = var.enabled ? 1 : 0

  provider     = databricks.account
  display_name = var.governance_admin_group_name
}

resource "databricks_group" "data_engineers" {
  count = var.enabled ? 1 : 0

  provider     = databricks.account
  display_name = var.data_engineer_group_name
}

resource "databricks_group" "business_readers" {
  count = var.enabled ? 1 : 0

  provider     = databricks.account
  display_name = var.business_reader_group_name
}

resource "databricks_service_principal" "workflow" {
  count = var.enabled ? 1 : 0

  provider                 = databricks.account
  display_name             = var.workflow_service_principal_name
  disable_as_user_deletion = true
}

resource "databricks_service_principal" "denied_test" {
  count = var.enabled ? 1 : 0

  provider                 = databricks.account
  display_name             = var.denied_service_principal_name
  disable_as_user_deletion = true
}

resource "databricks_service_principal" "doris_external_read" {
  count = var.enabled && var.doris_external_read_service_principal_name != null ? 1 : 0

  provider                 = databricks.account
  display_name             = var.doris_external_read_service_principal_name
  disable_as_user_deletion = true
}

resource "databricks_service_principal_secret" "doris_external_read" {
  count = var.enabled && var.doris_external_read_service_principal_name != null ? 1 : 0

  provider             = databricks.account
  service_principal_id = databricks_service_principal.doris_external_read[0].id
  lifetime             = "2592000s"
  provider_config {
    workspace_id = var.workspace_id
  }
}

resource "databricks_group_member" "governance_admin" {
  count = var.enabled ? 1 : 0

  provider  = databricks.account
  group_id  = databricks_group.governance_admins[0].id
  member_id = data.databricks_user.governance_admin[0].id
}

resource "databricks_group_member" "workflow" {
  count = var.enabled ? 1 : 0

  provider  = databricks.account
  group_id  = databricks_group.data_engineers[0].id
  member_id = databricks_service_principal.workflow[0].id
}

locals {
  workspace_assignments = var.enabled ? merge({
    governance_admins = databricks_group.governance_admins[0].id
    data_engineers    = databricks_group.data_engineers[0].id
    business_readers  = databricks_group.business_readers[0].id
    workflow          = databricks_service_principal.workflow[0].id
    denied_test       = databricks_service_principal.denied_test[0].id
    }, var.doris_external_read_service_principal_name == null ? {} : {
    doris_external_read = databricks_service_principal.doris_external_read[0].id
  }) : {}
}

resource "databricks_mws_permission_assignment" "this" {
  for_each = local.workspace_assignments

  provider     = databricks.account
  workspace_id = var.workspace_id
  principal_id = each.value
  permissions  = ["USER"]
}

resource "databricks_entitlements" "workflow" {
  count = var.enabled ? 1 : 0

  provider                   = databricks.workspace
  service_principal_id       = databricks_service_principal.workflow[0].id
  allow_cluster_create       = false
  allow_instance_pool_create = false
  databricks_sql_access      = true
  workspace_access           = true
}

resource "databricks_entitlements" "denied_test" {
  count = var.enabled ? 1 : 0

  provider                   = databricks.workspace
  service_principal_id       = databricks_service_principal.denied_test[0].id
  allow_cluster_create       = false
  allow_instance_pool_create = false
  databricks_sql_access      = true
  workspace_access           = true
}

resource "databricks_entitlements" "doris_external_read" {
  count = var.enabled && var.doris_external_read_service_principal_name != null ? 1 : 0

  provider                   = databricks.workspace
  service_principal_id       = databricks_service_principal.doris_external_read[0].id
  allow_cluster_create       = false
  allow_instance_pool_create = false
  databricks_sql_access      = false
  workspace_access           = true
}

resource "databricks_access_control_rule_set" "workflow" {
  count = var.enabled ? 1 : 0

  provider = databricks.account
  name = format(
    "accounts/%s/servicePrincipals/%s/ruleSets/default",
    var.databricks_account_id,
    databricks_service_principal.workflow[0].application_id,
  )

  grant_rules {
    principals = ["groups/${var.governance_admin_group_name}"]
    role       = "roles/servicePrincipal.manager"
  }

  grant_rules {
    principals = ["groups/${var.governance_admin_group_name}"]
    role       = "roles/servicePrincipal.user"
  }
}

resource "databricks_access_control_rule_set" "denied_test" {
  count = var.enabled ? 1 : 0

  provider = databricks.account
  name = format(
    "accounts/%s/servicePrincipals/%s/ruleSets/default",
    var.databricks_account_id,
    databricks_service_principal.denied_test[0].application_id,
  )

  grant_rules {
    principals = ["groups/${var.governance_admin_group_name}"]
    role       = "roles/servicePrincipal.manager"
  }

  grant_rules {
    principals = ["groups/${var.governance_admin_group_name}"]
    role       = "roles/servicePrincipal.user"
  }
}

resource "databricks_access_control_rule_set" "doris_external_read" {
  count = var.enabled && var.doris_external_read_service_principal_name != null ? 1 : 0

  provider = databricks.account
  name = format(
    "accounts/%s/servicePrincipals/%s/ruleSets/default",
    var.databricks_account_id,
    databricks_service_principal.doris_external_read[0].application_id,
  )

  grant_rules {
    principals = ["groups/${var.governance_admin_group_name}"]
    role       = "roles/servicePrincipal.manager"
  }

  grant_rules {
    principals = ["groups/${var.governance_admin_group_name}"]
    role       = "roles/servicePrincipal.user"
  }
}
