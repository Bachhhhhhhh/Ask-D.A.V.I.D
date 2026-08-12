"""Offline static validation for Goal 4 Terraform, bundle, and SQL contracts."""

from __future__ import annotations

import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SCHEMAS = {
    "green_sm_raw",
    "green_sm_curated",
    "green_sm_business",
    "green_sm_ai",
    "green_sm_platform",
    "green_sm_sandbox",
}
EXPECTED_MANAGED_ROOTS = EXPECTED_SCHEMAS | {"catalog"}
EXPECTED_SQL_FILES = {f"{index:02d}_" for index in range(1, 14)}
REQUIRED_JOB_KEYS = {
    "synthetic_managed_iceberg_pipeline",
    "managed_iceberg_history_verification",
    "lineage_verification",
    "denied_table_access_verification",
    "denied_direct_path_verification",
}


def _without_sql_comments(source: str) -> str:
    return re.sub(r"--[^\n]*", "", source)


def validate_goal4_static(repository_root: Path) -> list[str]:
    """Return deterministic Goal 4 static-contract errors without cloud access."""
    errors: list[str] = []
    development = repository_root / "infrastructure/environments/development"
    bundle_root = repository_root / "databricks"
    sql_root = bundle_root / "sql/goal_04"

    required_paths = (
        development / "goal4.tf",
        development / "goal4_variables.tf",
        bundle_root / "databricks.yml",
        bundle_root / "bundles/goal_04_lakehouse/resources.yml",
        repository_root / "scripts/verify_goal4_table_inventory.py",
    )
    for path in required_paths:
        if not path.is_file():
            errors.append(f"missing Goal 4 source: {path.relative_to(repository_root)}")
    if errors:
        return errors

    goal4_source = (development / "goal4.tf").read_text(encoding="utf-8")
    development_main_source = (development / "main.tf").read_text(encoding="utf-8")
    variable_source = (development / "goal4_variables.tf").read_text(encoding="utf-8")
    local_source = (development / "locals.tf").read_text(encoding="utf-8")
    bundle_source = (bundle_root / "databricks.yml").read_text(encoding="utf-8")
    resource_source = (bundle_root / "bundles/goal_04_lakehouse/resources.yml").read_text(
        encoding="utf-8"
    )
    inventory_verifier_source = (
        repository_root / "scripts/verify_goal4_table_inventory.py"
    ).read_text(encoding="utf-8")
    aws_storage_source = (
        repository_root / "infrastructure/modules/databricks-aws-storage/main.tf"
    ).read_text(encoding="utf-8")
    aws_storage_variable_source = (
        repository_root / "infrastructure/modules/databricks-aws-storage/variables.tf"
    ).read_text(encoding="utf-8")
    aws_storage_output_source = (
        repository_root / "infrastructure/modules/databricks-aws-storage/outputs.tf"
    ).read_text(encoding="utf-8")
    development_output_source = (development / "outputs.tf").read_text(encoding="utf-8")
    identity_source = (
        repository_root / "infrastructure/modules/databricks-identities/main.tf"
    ).read_text(encoding="utf-8")
    lakehouse_source = (
        repository_root / "infrastructure/modules/databricks-lakehouse/main.tf"
    ).read_text(encoding="utf-8")
    kms_source = (repository_root / "infrastructure/modules/kms/main.tf").read_text(
        encoding="utf-8"
    )

    if not re.search(
        r'variable\s+"goal_4_stage".*?default\s*=\s*"disabled"',
        variable_source,
        flags=re.DOTALL,
    ):
        errors.append("goal_4_stage must default to disabled")
    for stage in ("disabled", "bootstrap", "active"):
        if f'"{stage}"' not in variable_source:
            errors.append(f"goal_4_stage does not declare {stage}")
    if not re.search(
        r'variable\s+"goal_4_storage_role_self_assumption_enabled".*?'
        r"default\s*=\s*false",
        variable_source,
        flags=re.DOTALL,
    ):
        errors.append("Goal 4 storage-role self-assumption must default to false")

    declared_schemas = set(re.findall(r"\b(green_sm_[a-z]+)\s*=", local_source))
    if declared_schemas != EXPECTED_SCHEMAS:
        errors.append("Goal 4 schema hierarchy differs from the six approved green_sm_* schemas")
    managed_roots_match = re.search(
        r"goal_4_managed_root_prefixes\s*=\s*\{(.*?)\n\s*\}",
        local_source,
        flags=re.DOTALL,
    )
    declared_managed_roots = set(
        re.findall(
            r"^\s*([a-z_]+)\s*=",
            managed_roots_match.group(1) if managed_roots_match else "",
            flags=re.MULTILINE,
        )
    )
    if declared_managed_roots != EXPECTED_MANAGED_ROOTS:
        errors.append("Goal 4 must declare exactly the seven approved managed-storage roots")
    if 'default     = "ask_david_development"' not in variable_source:
        errors.append("Goal 4 catalog must default to ask_david_development")
    if 'data "databricks_current_metastore"' not in goal4_source:
        errors.append("Goal 4 must verify and reuse the current metastore")
    if 'data "databricks_sql_warehouse"' not in goal4_source:
        errors.append("Goal 4 must verify and reuse the existing SQL warehouse")
    if 'module "databricks_aws_storage"' not in goal4_source:
        errors.append("Goal 4 is missing Terraform-managed AWS storage integration")
    if "module.storage.bucket_names" not in local_source:
        errors.append("Goal 4 managed roots must derive from Goal 3 storage outputs")
    if not re.search(
        r"goal_4_managed_root_markers\s*=\s*\{.*?"
        r'key\s*=\s*"\$\{local\.goal_4_managed_root_prefixes\[root_name\]\}/"',
        local_source,
        flags=re.DOTALL,
    ):
        errors.append("Goal 4 managed-root marker keys must end with a slash")
    if (
        "storage_access_role_arn = local.goal_4_enabled ? "
        "module.databricks_aws_storage.role_arn : null" not in development_main_source
    ):
        errors.append("storage KMS policy must depend on the created Unity Catalog IAM role")
    if "try(aws_iam_role.this[0].arn, null)" not in aws_storage_output_source:
        errors.append("Unity Catalog role output must derive from the created IAM role resource")
    if not re.search(
        r'variable\s+"self_assumption_enabled".*?default\s*=\s*false',
        aws_storage_variable_source,
        flags=re.DOTALL,
    ):
        errors.append("Unity Catalog storage module self-assumption must default to false")
    if (
        "var.goal_4_storage_role_self_assumption_enabled" not in goal4_source
        or "module.databricks_aws_storage.self_assumption_enabled" not in development_output_source
    ):
        errors.append("Goal 4 must expose and pass through the self-assumption bootstrap gate")
    if not re.search(
        r'variable\s+"goal_4_storage_role_self_assumption_enabled".*?'
        r'var\.goal_4_stage\s*!=\s*"active"\s*\|\|\s*'
        r"var\.goal_4_storage_role_self_assumption_enabled",
        variable_source,
        flags=re.DOTALL,
    ):
        errors.append("Goal 4 active must be blocked until storage-role self-assumption is enabled")

    forbidden_resources = (
        'resource "databricks_metastore"',
        'resource "databricks_metastore_assignment"',
        'resource "databricks_sql_endpoint"',
        'resource "databricks_cluster"',
        'resource "aws_glue_',
    )
    goal4_terraform = "\n".join(
        [goal4_source, aws_storage_source, identity_source, lakehouse_source, kms_source]
    )
    for resource in forbidden_resources:
        if resource in goal4_terraform:
            errors.append(f"Goal 4 contains forbidden resource {resource}")

    if not re.search(
        r"identifiers\s*=\s*concat\(\s*\[var\.unity_catalog_iam_arn\],\s*"
        r"var\.self_assumption_enabled\s*\?\s*\[local\.role_arn\]\s*:\s*\[\]",
        aws_storage_source,
        flags=re.DOTALL,
    ):
        errors.append(
            "Unity Catalog trust must add the role self-principal only through the "
            "disabled-by-default bootstrap gate"
        )
    trust_requirements = (
        'variable = "sts:ExternalId"',
        "values   = [var.external_id]",
    )
    if any(requirement not in aws_storage_source for requirement in trust_requirements):
        errors.append("Unity Catalog trust policy must retain the exact external-ID condition")
    if '"s3:*"' in aws_storage_source or '"kms:*"' in aws_storage_source:
        errors.append("Unity Catalog role policy must not contain wildcard S3 or KMS actions")
    if "resources = var.managed_object_arns" not in aws_storage_source:
        errors.append("Unity Catalog S3 object access must be limited to exact managed roots")
    if 'module.storage.bucket_names["logs"]' in local_source:
        errors.append("Goal 4 must not grant the Unity Catalog role access to the logs bucket")
    if 'catalog           = "${local.goal_4_managed_prefix}/catalog"' not in local_source:
        errors.append("Goal 4 must declare a distinct catalog managed root")
    if "resources = [var.storage_kms_key_arn]" not in aws_storage_source:
        errors.append("Unity Catalog KMS use must be limited to the existing storage key ARN")
    marker_resource = re.search(
        r'resource\s+"aws_s3_object"\s+"managed_root_marker"\s*\{(.*?)\n\}',
        aws_storage_source,
        flags=re.DOTALL,
    )
    if marker_resource is None or not re.search(
        r"for_each\s*=\s*var\.enabled\s*\?\s*var\.managed_root_markers\s*:\s*\{\}",
        marker_resource.group(1) if marker_resource else "",
    ):
        errors.append("Goal 4 must declare Terraform-managed markers only while Goal 4 is enabled")
    marker_source = marker_resource.group(1) if marker_resource else ""
    if not re.search(r'content\s*=\s*""', marker_source):
        errors.append("Goal 4 managed-root markers must be zero-byte objects")
    if not re.search(r'server_side_encryption\s*=\s*"aws:kms"', marker_source) or not re.search(
        r"kms_key_id\s*=\s*var\.storage_kms_key_arn", marker_source
    ):
        errors.append("Goal 4 managed-root markers must use the existing storage KMS key")
    if not re.search(
        r"managed_root_markers\s*=\s*local\.goal_4_managed_root_markers",
        goal4_source,
    ):
        errors.append("Goal 4 must pass all approved managed roots to the marker resource")
    if "module.databricks_aws_storage.managed_root_marker_keys" not in development_output_source:
        errors.append("Goal 4 must expose the Terraform-managed marker inventory")
    if "Principal = { AWS = var.storage_access_role_arn }" not in kms_source:
        errors.append("storage KMS policy must grant only the exact Unity Catalog role")
    if "allow_cluster_create       = false" not in identity_source:
        errors.append("Goal 4 service principals must not be entitled to create clusters")
    if "allow_instance_pool_create = false" not in identity_source:
        errors.append("Goal 4 service principals must not create instance pools")
    if "databricks_workspace_binding" not in lakehouse_source:
        errors.append("Goal 4 lakehouse securables must be bound to development")
    if "READ_FILES" in lakehouse_source or "WRITE_FILES" in lakehouse_source:
        errors.append("Goal 4 data principals must not receive direct file privileges")

    for job_key in REQUIRED_JOB_KEYS:
        if not re.search(rf"^    {re.escape(job_key)}:$", resource_source, flags=re.MULTILINE):
            errors.append(f"bundle is missing required job {job_key}")
    if "new_cluster:" in resource_source or "job_clusters:" in resource_source:
        errors.append("Goal 4 bundle must not provision classic or job-cluster compute")
    if "warehouse_id: ${var.warehouse_id}" not in resource_source:
        errors.append("Goal 4 SQL tasks must use the supplied existing warehouse ID")
    native_assertion_task = re.search(
        r"- task_key: assert_native_iceberg_sql_metadata.*?"
        r"depends_on:\s*\n\s*- task_key: create_managed_iceberg_tables.*?"
        r"path: \$\{workspace\.file_path\}/sql/goal_04/13_assert_native_iceberg_metadata\.sql",
        resource_source,
        flags=re.DOTALL,
    )
    if native_assertion_task is None:
        errors.append("Goal 4 pipeline must assert native Iceberg metadata after table creation")
    load_dependency = re.search(
        r"- task_key: load_raw_and_reference_data\s*\n\s*depends_on:\s*\n"
        r"\s*- task_key: assert_native_iceberg_sql_metadata",
        resource_source,
    )
    if load_dependency is None:
        errors.append("Goal 4 data writes must depend on the native Iceberg metadata assertion")
    if "default: ask_david_development" not in bundle_source:
        errors.append("bundle catalog variable must default to ask_david_development")
    if "workspace_host:" in bundle_source or "${var.workspace_host}" in bundle_source:
        errors.append(
            "Goal 4 bundle authentication must come from the approved CLI profile, "
            "not a bundle host mapping"
        )
    if "/Workspace/Shared" in bundle_source:
        errors.append("Goal 4 bundle deployment root must not use /Workspace/Shared")
    sync_block_match = re.search(
        r"(?ms)^sync:\n(?P<body>.*?)(?=^targets:)",
        bundle_source,
    )
    expected_sync_block = (
        "  include:\n    - sql/goal_04/*.sql\n  exclude:\n    - sql/goal_04/remediation/**\n"
    )
    normalized_sync_body = (
        sync_block_match.group("body").strip("\n") + "\n" if sync_block_match is not None else None
    )
    if normalized_sync_body != expected_sync_block:
        errors.append(
            "Goal 4 bundle sync must include only top-level SQL and explicitly exclude "
            "the nested destructive remediation SQL"
        )
    expected_bundle_root = (
        "/Workspace/Users/${var.governance_admin_user_name}/.bundle/${bundle.name}/${bundle.target}"
    )
    expected_target_workspace = (
        "targets:\n"
        "  development:\n"
        "    default: true\n"
        "    mode: production\n"
        "    workspace:\n"
        f"      root_path: {expected_bundle_root}"
    )
    if expected_target_workspace not in bundle_source:
        errors.append(
            "Goal 4 development target must use the governance administrator workspace root"
        )
    expected_admin_permission = (
        "  - user_name: ${var.governance_admin_user_name}\n    level: CAN_MANAGE"
    )
    if expected_admin_permission not in bundle_source:
        errors.append("Goal 4 bundle must declare governance administrator CAN_MANAGE permission")
    denied_bundle_permissions = re.findall(
        r"(?m)^  - service_principal_name: "
        r"\$\{var\.denied_service_principal_application_id\}\n"
        r"    level: (\S+)$",
        bundle_source,
    )
    if denied_bundle_permissions != ["CAN_VIEW"]:
        errors.append(
            "Goal 4 denied test principal must have exactly one top-level CAN_VIEW permission"
        )

    sql_files = sorted(sql_root.glob("*.sql")) if sql_root.is_dir() else []
    prefixes = {path.name[:3] for path in sql_files}
    if prefixes != EXPECTED_SQL_FILES:
        errors.append("Goal 4 must provide the complete numbered 01-13 SQL contract")

    combined_sql = "\n".join(path.read_text(encoding="utf-8") for path in sql_files)
    executable_sql = _without_sql_comments(combined_sql)
    if len(re.findall(r"\bUSING\s+ICEBERG\b", executable_sql, flags=re.IGNORECASE)) != 7:
        errors.append("Goal 4 must declare exactly seven managed Apache Iceberg test tables")
    if re.search(r"\bUSING\s+DELTA\b", executable_sql, flags=re.IGNORECASE):
        errors.append("Delta substitutes are forbidden in Goal 4 SQL")
    if not re.search(r"\bVERSION\s+AS\s+OF\b", executable_sql, flags=re.IGNORECASE):
        errors.append("Goal 4 must include an Apache Iceberg time-travel read")
    history_source = _without_sql_comments(
        (sql_root / "09_verify_iceberg_history.sql").read_text(encoding="utf-8")
    )
    if "USE CATALOG IDENTIFIER(:catalog_name);" not in history_source:
        errors.append("Goal 4 history SQL must select the approved catalog through IDENTIFIER")
    if re.search(
        r"\b(?:DESCRIBE\s+(?:DETAIL|HISTORY)|FROM)\s+IDENTIFIER\([^)]*\|\|",
        history_source,
        flags=re.IGNORECASE,
    ):
        errors.append("Goal 4 history SQL must not concatenate identifiers in DESCRIBE or FROM")
    required_history_statements = (
        "DESCRIBE DETAIL green_sm_raw.synthetic_events;",
        "DESCRIBE DETAIL green_sm_curated.synthetic_events;",
        "DESCRIBE DETAIL green_sm_curated.synthetic_entities;",
        "DESCRIBE DETAIL green_sm_business.synthetic_metrics;",
        "DESCRIBE DETAIL green_sm_ai.synthetic_document_metadata;",
        "DESCRIBE DETAIL green_sm_platform.synthetic_agent_execution_audit;",
        "DESCRIBE DETAIL green_sm_platform.synthetic_data_quality_results;",
        "DESCRIBE HISTORY green_sm_raw.synthetic_events;",
        "FROM green_sm_raw.synthetic_events VERSION AS OF 1;",
    )
    if any(statement not in history_source for statement in required_history_statements):
        errors.append("Goal 4 history SQL must inspect all managed tables and Raw version 1")
    lineage_source = _without_sql_comments(
        (sql_root / "10_verify_lineage.sql").read_text(encoding="utf-8")
    )
    if "FROM system.access.table_lineage" not in lineage_source:
        errors.append("Goal 4 lineage SQL must query the Unity Catalog lineage system table")
    if lineage_source.lower().count("assert_true(") != 2:
        errors.append("Goal 4 lineage SQL must assert exactly two required lineage edges")
    required_lineage_edges = (
        "source_table_full_name = :catalog_name || '.green_sm_raw.synthetic_events'",
        "target_table_full_name = :catalog_name || '.green_sm_curated.synthetic_events'",
        "source_table_full_name = :catalog_name || '.green_sm_curated.synthetic_events'",
        "target_table_full_name = :catalog_name || '.green_sm_business.synthetic_metrics'",
    )
    if any(edge not in lineage_source for edge in required_lineage_edges):
        errors.append("Goal 4 lineage SQL must assert Raw-to-Curated and Curated-to-Business")
    if re.search(r"\b(?:INSERT|UPDATE|DELETE|MERGE)\b", lineage_source, flags=re.IGNORECASE):
        errors.append("Goal 4 lineage verification must remain read-only")
    quality_source = _without_sql_comments(
        (sql_root / "06_record_quality_results.sql").read_text(encoding="utf-8")
    )
    if "table_type = 'MANAGED'" not in quality_source:
        errors.append("Goal 4 quality checks must require managed tables")
    if "data_source_format = 'ICEBERG'" not in quality_source:
        errors.append("Goal 4 quality checks must require the ICEBERG data-source format")
    if "COUNT(*) = 10 AND COUNT_IF(check_state <> 'PASS') = 0" not in quality_source:
        errors.append("Goal 4 quality recording must fail if any of exactly ten checks is absent")
    pipeline_assertion_source = _without_sql_comments(
        (sql_root / "08_verify_pipeline_results.sql").read_text(encoding="utf-8")
    )
    required_pipeline_assertions = (
        "COUNT(*) = 10",
        "COUNT_IF(check_state <> 'PASS') = 0",
        "check_name = 'managed_iceberg_test_table_count'",
        "observed_value = 7.0D",
        "expected_value = 7.0D",
    )
    if any(marker not in pipeline_assertion_source for marker in required_pipeline_assertions):
        errors.append(
            "Goal 4 final pipeline assertion must fail closed on all ten checks and format"
        )
    native_metadata_source = _without_sql_comments(
        (sql_root / "13_assert_native_iceberg_metadata.sql").read_text(encoding="utf-8")
    )
    native_metadata_markers = (
        "COUNT(*) = 7",
        "COUNT_IF(table_type <> 'MANAGED') = 0",
        "COUNT_IF(data_source_format <> 'ICEBERG') = 0",
        "green_sm_raw' AND table_name = 'synthetic_events'",
        "green_sm_business' AND table_name = 'synthetic_metrics'",
        "green_sm_platform'",
    )
    if any(marker not in native_metadata_source for marker in native_metadata_markers):
        errors.append(
            "Goal 4 pre-write SQL assertion must require exactly seven managed Iceberg tables"
        )
    if re.search(
        r"\b(?:INSERT|UPDATE|DELETE|MERGE|CREATE|DROP|ALTER|REPLACE)\b",
        native_metadata_source,
        flags=re.IGNORECASE,
    ):
        errors.append("Goal 4 pre-write native Iceberg assertion must remain read-only")
    ddl_source = _without_sql_comments(
        (sql_root / "01_create_managed_iceberg_tables.sql").read_text(encoding="utf-8")
    )
    if re.search(r"\bLOCATION\b", ddl_source, flags=re.IGNORECASE):
        errors.append("Goal 4 managed-table DDL must not specify LOCATION")

    remediation_root = sql_root / "remediation"
    if remediation_root.exists() and any(remediation_root.rglob("*.sql")):
        errors.append("Goal 4 destructive remediation SQL must not remain in the repository")

    inventory_verifier_markers = (
        'table.get("table_type") != "MANAGED"',
        'table.get("data_source_format") != "ICEBERG"',
        'startswith("delta.")',
        '"/_iceberg/metadata" not in metadata_path',
    )
    if any(marker not in inventory_verifier_source for marker in inventory_verifier_markers):
        errors.append("Goal 4 live table inventory verifier must fail closed on native Iceberg")

    for path in sql_files:
        expected_reference = f"${{workspace.file_path}}/sql/goal_04/{path.name}"
        if expected_reference not in resource_source:
            errors.append(f"bundle does not reference {path.name}")
    denied_table_source = (sql_root / "11_denied_table_access.sql").read_text(encoding="utf-8")
    if not all(
        marker in denied_table_source for marker in ("INSUFFICIENT_PERMISSIONS", "SQLSTATE 42501")
    ):
        errors.append("denied table-access SQL must document its principal-specific UC rejection")
    denied_path_source = (sql_root / "12_denied_direct_path_access.sql").read_text(encoding="utf-8")
    if "LOCATION_OVERLAP" not in denied_path_source:
        errors.append("denied path-access SQL must document the managed-storage overlap guard")
    if "clean UC/IAM/KMS/S3 policy inspection" not in denied_path_source:
        errors.append("denied path-access evidence must require clean UC/AWS policy inspection")

    forbidden_patterns = (
        r"(?i)aws_access_key_id\s*=",
        r"(?i)aws_secret_access_key\s*=",
        r"(?i)databricks_token\s*=",
        r"(?i)client_secret\s*=",
    )
    tracked_goal4_source = "\n".join(
        [
            goal4_source,
            variable_source,
            bundle_source,
            resource_source,
            combined_sql,
            inventory_verifier_source,
        ]
    )
    for pattern in forbidden_patterns:
        if re.search(pattern, tracked_goal4_source):
            errors.append("Goal 4 source contains a forbidden credential assignment")

    return errors


def main() -> int:
    errors = validate_goal4_static(REPOSITORY_ROOT)
    if errors:
        print("Goal 4 offline validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Goal 4 offline static validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
