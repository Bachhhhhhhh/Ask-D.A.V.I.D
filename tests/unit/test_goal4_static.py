"""Tests for the credential-free Goal 4 static validation gate."""

from pathlib import Path

from scripts.validate_goal4 import REPOSITORY_ROOT, validate_goal4_static

GOAL4_SOURCE_PATHS = (
    "infrastructure/environments/development/main.tf",
    "infrastructure/environments/development/goal4.tf",
    "infrastructure/environments/development/goal4_variables.tf",
    "infrastructure/environments/development/locals.tf",
    "infrastructure/environments/development/outputs.tf",
    "infrastructure/modules/databricks-aws-storage/main.tf",
    "infrastructure/modules/databricks-aws-storage/variables.tf",
    "infrastructure/modules/databricks-aws-storage/outputs.tf",
    "infrastructure/modules/databricks-identities/main.tf",
    "infrastructure/modules/databricks-lakehouse/main.tf",
    "infrastructure/modules/kms/main.tf",
    "databricks/databricks.yml",
    "databricks/bundles/goal_04_lakehouse/resources.yml",
    "databricks/sql/goal_04/remediation/README.md",
    "scripts/verify_goal4_table_inventory.py",
)


def _copy_goal4_fixture(destination_root: Path) -> None:
    for relative in GOAL4_SOURCE_PATHS:
        source = REPOSITORY_ROOT / relative
        destination = destination_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    source_sql = REPOSITORY_ROOT / "databricks/sql/goal_04"
    destination_sql = destination_root / "databricks/sql/goal_04"
    destination_sql.mkdir(parents=True, exist_ok=True)
    for source in source_sql.glob("*.sql"):
        (destination_sql / source.name).write_text(
            source.read_text(encoding="utf-8"), encoding="utf-8"
        )


def test_goal4_repository_contract_passes() -> None:
    """The checked-in Goal 4 source must satisfy the approved offline contract."""
    assert validate_goal4_static(REPOSITORY_ROOT) == []


def test_goal4_bundle_authentication_comes_from_cli_profile(tmp_path: Path) -> None:
    """An unresolved bundle-host variable must not override profile authentication."""
    _copy_goal4_fixture(tmp_path)
    bundle = tmp_path / "databricks/databricks.yml"
    bundle.write_text(
        bundle.read_text(encoding="utf-8").replace(
            "    workspace:\n      root_path:",
            "    workspace:\n      host: ${var.workspace_host}\n      root_path:",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert (
        "Goal 4 bundle authentication must come from the approved CLI profile, "
        "not a bundle host mapping" in errors
    )


def test_goal4_bundle_rejects_shared_deployment_root(tmp_path: Path) -> None:
    """Bundle files must deploy under the approved administrator's workspace path."""
    _copy_goal4_fixture(tmp_path)
    bundle = tmp_path / "databricks/databricks.yml"
    bundle.write_text(
        bundle.read_text(encoding="utf-8").replace(
            "/Workspace/Users/${var.governance_admin_user_name}",
            "/Workspace/Shared",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 bundle deployment root must not use /Workspace/Shared" in errors
    assert (
        "Goal 4 development target must use the governance administrator workspace root" in errors
    )


def test_goal4_bundle_requires_target_scoped_deployment_root(tmp_path: Path) -> None:
    """Production-mode root configuration must live under the development target."""
    _copy_goal4_fixture(tmp_path)
    bundle = tmp_path / "databricks/databricks.yml"
    bundle.write_text(
        bundle.read_text(encoding="utf-8").replace(
            "    workspace:\n"
            "      root_path: /Workspace/Users/${var.governance_admin_user_name}/"
            ".bundle/${bundle.name}/${bundle.target}\n",
            "",
        )
        + "\nworkspace:\n"
        "  root_path: /Workspace/Users/${var.governance_admin_user_name}/"
        ".bundle/${bundle.name}/${bundle.target}\n",
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert (
        "Goal 4 development target must use the governance administrator workspace root" in errors
    )


def test_goal4_bundle_requires_governance_admin_permission(tmp_path: Path) -> None:
    """Bundle ACLs must match the inherited administrator permission on the user root."""
    _copy_goal4_fixture(tmp_path)
    bundle = tmp_path / "databricks/databricks.yml"
    bundle.write_text(
        bundle.read_text(encoding="utf-8").replace(
            "  - user_name: ${var.governance_admin_user_name}\n    level: CAN_MANAGE\n",
            "",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 bundle must declare governance administrator CAN_MANAGE permission" in errors


def test_goal4_bundle_requires_denied_principal_can_view(tmp_path: Path) -> None:
    """The denied run identity must be able to read synchronized SQL files."""
    _copy_goal4_fixture(tmp_path)
    bundle = tmp_path / "databricks/databricks.yml"
    bundle.write_text(
        bundle.read_text(encoding="utf-8").replace(
            "  - service_principal_name: ${var.denied_service_principal_application_id}\n"
            "    level: CAN_VIEW\n",
            "",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert (
        "Goal 4 denied test principal must have exactly one top-level CAN_VIEW permission" in errors
    )


def test_goal4_bundle_rejects_denied_principal_can_run(tmp_path: Path) -> None:
    """The denied principal cannot receive permission to trigger privileged jobs."""
    _copy_goal4_fixture(tmp_path)
    bundle = tmp_path / "databricks/databricks.yml"
    bundle.write_text(
        bundle.read_text(encoding="utf-8").replace(
            "  - service_principal_name: ${var.denied_service_principal_application_id}\n"
            "    level: CAN_VIEW\n",
            "  - service_principal_name: ${var.denied_service_principal_application_id}\n"
            "    level: CAN_RUN\n",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert (
        "Goal 4 denied test principal must have exactly one top-level CAN_VIEW permission" in errors
    )


def test_goal4_bundle_rejects_denied_principal_can_manage(tmp_path: Path) -> None:
    """The denied principal cannot modify bundle resources or workspace files."""
    _copy_goal4_fixture(tmp_path)
    bundle = tmp_path / "databricks/databricks.yml"
    bundle.write_text(
        bundle.read_text(encoding="utf-8").replace(
            "  - service_principal_name: ${var.denied_service_principal_application_id}\n"
            "    level: CAN_VIEW\n",
            "  - service_principal_name: ${var.denied_service_principal_application_id}\n"
            "    level: CAN_MANAGE\n",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert (
        "Goal 4 denied test principal must have exactly one top-level CAN_VIEW permission" in errors
    )


def test_goal4_denied_table_contract_requires_principal_specific_rejection(
    tmp_path: Path,
) -> None:
    """The protected-table test must name the observed Unity Catalog denial contract."""
    _copy_goal4_fixture(tmp_path)
    denied_sql = tmp_path / "databricks/sql/goal_04/11_denied_table_access.sql"
    denied_sql.write_text(
        denied_sql.read_text(encoding="utf-8").replace(
            "INSUFFICIENT_PERMISSIONS", "UNEXPECTED_ERROR"
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "denied table-access SQL must document its principal-specific UC rejection" in errors


def test_goal4_denied_path_contract_requires_managed_storage_guard(tmp_path: Path) -> None:
    """A generic job failure cannot substitute for the managed-path overlap control."""
    _copy_goal4_fixture(tmp_path)
    denied_sql = tmp_path / "databricks/sql/goal_04/12_denied_direct_path_access.sql"
    denied_sql.write_text(
        denied_sql.read_text(encoding="utf-8").replace("LOCATION_OVERLAP", "UNEXPECTED_ERROR"),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "denied path-access SQL must document the managed-storage overlap guard" in errors


def test_goal4_denied_path_contract_requires_policy_inspection_pairing(tmp_path: Path) -> None:
    """Structural path rejection alone cannot prove principal-specific storage isolation."""
    _copy_goal4_fixture(tmp_path)
    denied_sql = tmp_path / "databricks/sql/goal_04/12_denied_direct_path_access.sql"
    denied_sql.write_text(
        denied_sql.read_text(encoding="utf-8").replace(
            "clean UC/IAM/KMS/S3 policy inspection", "an unverified policy assumption"
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "denied path-access evidence must require clean UC/AWS policy inspection" in errors


def test_goal4_negative_sql_executable_statements_are_exact() -> None:
    """Evidence-contract comments must not alter either approved negative query."""

    def executable_sql(name: str) -> str:
        source = (REPOSITORY_ROOT / "databricks/sql/goal_04" / name).read_text(encoding="utf-8")
        return "\n".join(
            line
            for line in source.splitlines()
            if line.strip() and not line.lstrip().startswith("--")
        )

    assert executable_sql("11_denied_table_access.sql") == (
        "SELECT *\n"
        "FROM IDENTIFIER(:catalog_name || '.green_sm_business.synthetic_metrics')\n"
        "LIMIT 1;"
    )
    assert executable_sql("12_denied_direct_path_access.sql") == (
        "SELECT *\nFROM IDENTIFIER('iceberg.`' || :denied_s3_probe_url || '`')\nLIMIT 1;"
    )


def test_goal4_rejects_delta_substitution(tmp_path: Path) -> None:
    """Managed Iceberg DDL cannot silently become Delta DDL."""
    _copy_goal4_fixture(tmp_path)
    ddl = tmp_path / "databricks/sql/goal_04/01_create_managed_iceberg_tables.sql"
    ddl.write_text(
        ddl.read_text(encoding="utf-8").replace("USING ICEBERG", "USING DELTA", 1),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Delta substitutes are forbidden in Goal 4 SQL" in errors


def test_goal4_pipeline_requires_pre_write_native_format_gate(tmp_path: Path) -> None:
    """Synthetic writes cannot start until the new tables pass a format assertion."""
    _copy_goal4_fixture(tmp_path)
    resources = tmp_path / "databricks/bundles/goal_04_lakehouse/resources.yml"
    resources.write_text(
        resources.read_text(encoding="utf-8").replace(
            "- task_key: assert_native_iceberg_sql_metadata\n"
            "          sql_task:\n"
            "            file:\n"
            "              path: ${workspace.file_path}/sql/goal_04/"
            "02_load_raw_and_reference_data.sql",
            "- task_key: create_managed_iceberg_tables\n"
            "          sql_task:\n"
            "            file:\n"
            "              path: ${workspace.file_path}/sql/goal_04/"
            "02_load_raw_and_reference_data.sql",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 data writes must depend on the native Iceberg metadata assertion" in errors


def test_goal4_pre_write_format_assertion_requires_iceberg(tmp_path: Path) -> None:
    """The SQL metadata gate must reject a non-Iceberg result before writes."""
    _copy_goal4_fixture(tmp_path)
    assertion = tmp_path / "databricks/sql/goal_04/13_assert_native_iceberg_metadata.sql"
    assertion.write_text(
        assertion.read_text(encoding="utf-8").replace(
            "COUNT_IF(data_source_format <> 'ICEBERG') = 0",
            "COUNT_IF(data_source_format <> 'DELTA') = 0",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert (
        "Goal 4 pre-write SQL assertion must require exactly seven managed Iceberg tables" in errors
    )


def test_goal4_quality_assertion_rejects_missing_rows(tmp_path: Path) -> None:
    """A zero-row or partial quality result set cannot satisfy acceptance."""
    _copy_goal4_fixture(tmp_path)
    verification = tmp_path / "databricks/sql/goal_04/08_verify_pipeline_results.sql"
    verification.write_text(
        verification.read_text(encoding="utf-8").replace("COUNT(*) = 10", "COUNT(*) >= 0"),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 final pipeline assertion must fail closed on all ten checks and format" in errors


def test_goal4_rejects_destructive_remediation_sql(tmp_path: Path) -> None:
    """The permanent compatibility profile cannot retain a destructive drop script."""
    _copy_goal4_fixture(tmp_path)
    remediation = (
        tmp_path / "databricks/sql/goal_04/remediation/01_drop_delta_uniform_synthetic_tables.sql"
    )
    remediation.parent.mkdir(parents=True, exist_ok=True)
    remediation.write_text(
        "DROP TABLE IF EXISTS green_sm_business.synthetic_metrics;\n",
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 destructive remediation SQL must not remain in the repository" in errors


def test_goal4_requires_non_executable_remediation_marker(tmp_path: Path) -> None:
    """The explicit sync exclusion must match a durable non-executable marker."""
    _copy_goal4_fixture(tmp_path)
    marker = tmp_path / "databricks/sql/goal_04/remediation/README.md"
    marker.unlink()

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 remediation exclusion marker must exist" in errors


def test_goal4_bundle_does_not_sync_destructive_remediation(tmp_path: Path) -> None:
    """The drop script cannot become an ordinary bundle workspace artifact."""
    _copy_goal4_fixture(tmp_path)
    bundle = tmp_path / "databricks/databricks.yml"
    bundle.write_text(
        bundle.read_text(encoding="utf-8").replace(
            "  exclude:\n    - sql/goal_04/remediation/**\n",
            "",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert (
        "Goal 4 bundle sync must include only top-level SQL and explicitly exclude "
        "the nested destructive remediation SQL" in errors
    )


def test_goal4_bundle_rejects_recursive_sync_include(tmp_path: Path) -> None:
    """A recursive include would leak the destructive remediation script."""
    _copy_goal4_fixture(tmp_path)
    bundle = tmp_path / "databricks/databricks.yml"
    bundle.write_text(
        bundle.read_text(encoding="utf-8").replace(
            "    - sql/goal_04/*.sql",
            "    - sql/goal_04/**/*.sql",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert (
        "Goal 4 bundle sync must include only top-level SQL and explicitly exclude "
        "the nested destructive remediation SQL" in errors
    )


def test_goal4_history_sql_requires_approved_catalog_context(tmp_path: Path) -> None:
    """History inspection must parameterize only the approved catalog boundary."""
    _copy_goal4_fixture(tmp_path)
    history = tmp_path / "databricks/sql/goal_04/09_verify_iceberg_history.sql"
    history.write_text(
        history.read_text(encoding="utf-8").replace(
            "USE CATALOG IDENTIFIER(:catalog_name);",
            "USE CATALOG workspace;",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 history SQL must select the approved catalog through IDENTIFIER" in errors


def test_goal4_history_sql_rejects_concatenated_describe_identifier(tmp_path: Path) -> None:
    """The Serverless SQL DESCRIBE parser must receive a static name in catalog context."""
    _copy_goal4_fixture(tmp_path)
    history = tmp_path / "databricks/sql/goal_04/09_verify_iceberg_history.sql"
    history.write_text(
        history.read_text(encoding="utf-8").replace(
            "DESCRIBE DETAIL green_sm_raw.synthetic_events;",
            "DESCRIBE DETAIL IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events');",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 history SQL must not concatenate identifiers in DESCRIBE or FROM" in errors
    assert "Goal 4 history SQL must inspect all managed tables and Raw version 1" in errors


def test_goal4_lineage_sql_requires_raw_to_curated_edge(tmp_path: Path) -> None:
    """Lineage verification cannot omit the first governed transformation edge."""
    _copy_goal4_fixture(tmp_path)
    lineage = tmp_path / "databricks/sql/goal_04/10_verify_lineage.sql"
    lineage.write_text(
        lineage.read_text(encoding="utf-8").replace(
            ":catalog_name || '.green_sm_raw.synthetic_events'",
            ":catalog_name || '.green_sm_raw.missing_edge'",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 lineage SQL must assert Raw-to-Curated and Curated-to-Business" in errors


def test_goal4_lineage_sql_requires_curated_to_business_edge(tmp_path: Path) -> None:
    """Lineage verification cannot stop at the Curated layer."""
    _copy_goal4_fixture(tmp_path)
    lineage = tmp_path / "databricks/sql/goal_04/10_verify_lineage.sql"
    lineage.write_text(
        lineage.read_text(encoding="utf-8").replace(
            ":catalog_name || '.green_sm_business.synthetic_metrics'",
            ":catalog_name || '.green_sm_business.missing_edge'",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 lineage SQL must assert Raw-to-Curated and Curated-to-Business" in errors


def test_goal4_lineage_sql_requires_two_assertions(tmp_path: Path) -> None:
    """A zero-row lineage query must fail rather than appear verified."""
    _copy_goal4_fixture(tmp_path)
    lineage = tmp_path / "databricks/sql/goal_04/10_verify_lineage.sql"
    lineage.write_text(
        lineage.read_text(encoding="utf-8").replace("assert_true(", "coalesce("),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 lineage SQL must assert exactly two required lineage edges" in errors


def test_goal4_requires_resource_level_iam_to_kms_dependency(tmp_path: Path) -> None:
    """The KMS policy cannot reference an IAM ARN that Terraform merely constructs."""
    _copy_goal4_fixture(tmp_path)
    outputs = tmp_path / "infrastructure/modules/databricks-aws-storage/outputs.tf"
    outputs.write_text(
        outputs.read_text(encoding="utf-8").replace(
            "try(aws_iam_role.this[0].arn, null)", "var.enabled ? local.role_arn : null"
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Unity Catalog role output must derive from the created IAM role resource" in errors


def test_goal4_self_assumption_defaults_off(tmp_path: Path) -> None:
    """The initial-role plan must not contain an IAM self-principal."""
    _copy_goal4_fixture(tmp_path)
    variables = tmp_path / "infrastructure/environments/development/goal4_variables.tf"
    variables.write_text(
        variables.read_text(encoding="utf-8").replace(
            'variable "goal_4_storage_role_self_assumption_enabled" {\n'
            "  type        = bool\n"
            "  default     = false",
            'variable "goal_4_storage_role_self_assumption_enabled" {\n'
            "  type        = bool\n"
            "  default     = true",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 storage-role self-assumption must default to false" in errors


def test_goal4_rejects_unconditional_storage_role_self_principal(tmp_path: Path) -> None:
    """Terraform must create the role before a later plan adds its own ARN."""
    _copy_goal4_fixture(tmp_path)
    storage = tmp_path / "infrastructure/modules/databricks-aws-storage/main.tf"
    storage.write_text(
        storage.read_text(encoding="utf-8").replace(
            "identifiers = concat(\n"
            "        [var.unity_catalog_iam_arn],\n"
            "        var.self_assumption_enabled ? [local.role_arn] : [],\n"
            "      )",
            "identifiers = [var.unity_catalog_iam_arn, local.role_arn]",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert (
        "Unity Catalog trust must add the role self-principal only through the "
        "disabled-by-default bootstrap gate" in errors
    )


def test_goal5_source_access_requires_workflow_only_read_files(tmp_path: Path) -> None:
    """The Goal 5 source exception cannot become a broad data-engineer grant."""
    _copy_goal4_fixture(tmp_path)
    lakehouse = tmp_path / "infrastructure/modules/databricks-lakehouse/main.tf"
    lakehouse.write_text(
        lakehouse.read_text(encoding="utf-8").replace(
            "principal  = var.workflow_service_principal_application_id\n"
            '      privileges = ["READ_FILES"]',
            'principal  = var.data_engineer_group_name\n      privileges = ["READ_FILES"]',
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert (
        "Goal 5 READ_FILES must be scoped to the workflow principal and source locations" in errors
    )


def test_goal5_source_access_rejects_write_files(tmp_path: Path) -> None:
    """Source fixtures are immutable to the workflow principal."""
    _copy_goal4_fixture(tmp_path)
    lakehouse = tmp_path / "infrastructure/modules/databricks-lakehouse/main.tf"
    lakehouse.write_text(
        lakehouse.read_text(encoding="utf-8").replace(
            'privileges = ["READ_FILES"]', 'privileges = ["READ_FILES", "WRITE_FILES"]'
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4/5 source locations must never grant WRITE_FILES" in errors


def test_goal4_requires_active_self_assumption_guard(tmp_path: Path) -> None:
    """The active namespace stage cannot bypass the completed trust bootstrap."""
    _copy_goal4_fixture(tmp_path)
    variables = tmp_path / "infrastructure/environments/development/goal4_variables.tf"
    variables.write_text(
        variables.read_text(encoding="utf-8").replace(
            'var.goal_4_stage != "active" ||',
            "true ||",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 active must be blocked until storage-role self-assumption is enabled" in errors


def test_goal4_requires_enabled_stage_managed_root_markers(tmp_path: Path) -> None:
    """Empty S3 prefixes must have Terraform-owned path-existence markers."""
    _copy_goal4_fixture(tmp_path)
    storage = tmp_path / "infrastructure/modules/databricks-aws-storage/main.tf"
    storage.write_text(
        storage.read_text(encoding="utf-8").replace(
            "for_each = var.enabled ? var.managed_root_markers : {}",
            "for_each = var.managed_root_markers",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 must declare Terraform-managed markers only while Goal 4 is enabled" in errors


def test_goal4_requires_zero_byte_managed_root_markers(tmp_path: Path) -> None:
    """A marker must not introduce synthetic records or other payload data."""
    _copy_goal4_fixture(tmp_path)
    storage = tmp_path / "infrastructure/modules/databricks-aws-storage/main.tf"
    storage.write_text(
        storage.read_text(encoding="utf-8").replace(
            'content                = ""',
            'content                = "payload"',
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 managed-root markers must be zero-byte objects" in errors


def test_goal4_requires_kms_encrypted_managed_root_markers(tmp_path: Path) -> None:
    """Marker creation cannot weaken the existing SSE-KMS storage boundary."""
    _copy_goal4_fixture(tmp_path)
    storage = tmp_path / "infrastructure/modules/databricks-aws-storage/main.tf"
    storage.write_text(
        storage.read_text(encoding="utf-8").replace(
            'server_side_encryption = "aws:kms"',
            'server_side_encryption = "AES256"',
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 managed-root markers must use the existing storage KMS key" in errors


def test_goal4_requires_trailing_slash_managed_root_markers(tmp_path: Path) -> None:
    """Each zero-byte object must use the S3 folder-marker key convention."""
    _copy_goal4_fixture(tmp_path)
    local_source = tmp_path / "infrastructure/environments/development/locals.tf"
    local_source.write_text(
        local_source.read_text(encoding="utf-8").replace(
            'key    = "${local.goal_4_managed_root_prefixes[root_name]}/"',
            "key    = local.goal_4_managed_root_prefixes[root_name]",
        ),
        encoding="utf-8",
    )

    errors = validate_goal4_static(tmp_path)

    assert "Goal 4 managed-root marker keys must end with a slash" in errors
