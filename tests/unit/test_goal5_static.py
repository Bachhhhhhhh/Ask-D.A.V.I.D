"""Static Goal 5 repository-scope tests."""

from pathlib import Path

from scripts.validate_goal5 import validate_goal5_repository

ROOT = Path(__file__).resolve().parents[2]


def test_goal5_repository_contract_passes() -> None:
    assert validate_goal5_repository(ROOT) == []


def test_goal5_sql_files_exist() -> None:
    sql_dir = ROOT / "databricks" / "sql" / "goal_05"
    assert sorted(path.name for path in sql_dir.glob("*.sql")) == [
        "01_create_goal5_tables.sql",
        "02_ingest_structured_csv.sql",
        "03_ingest_document.sql",
        "04_ingest_cdc.sql",
        "05_verify_goal5_outputs.sql",
        "06_verify_goal5_idempotency.sql",
    ]


def test_goal5_terraform_has_three_sse_kms_source_objects() -> None:
    source = (ROOT / "infrastructure/environments/development/goal5.tf").read_text(encoding="utf-8")
    assert source.count('resource "aws_s3_object"') == 3
    assert source.count('server_side_encryption = "aws:kms"') == 3
    assert source.count("count        = var.goal_5_source_objects_enabled ? 1 : 0") == 3


def test_goal5_source_access_is_narrow_and_read_only() -> None:
    """The workflow can read only the two fixture prefixes through UC."""
    local_source = (ROOT / "infrastructure/environments/development/locals.tf").read_text(
        encoding="utf-8"
    )
    lakehouse_source = (ROOT / "infrastructure/modules/databricks-lakehouse/main.tf").read_text(
        encoding="utf-8"
    )
    iam_source = (ROOT / "infrastructure/modules/databricks-aws-storage/main.tf").read_text(
        encoding="utf-8"
    )

    assert "goal5_raw_sources" in local_source
    assert "goal5_document_sources" in local_source
    assert lakehouse_source.count('privileges = ["READ_FILES"]') == 1
    assert "var.workflow_service_principal_application_id" in lakehouse_source
    assert "WRITE_FILES" not in lakehouse_source
    assert "ReadApprovedIngestionSourceObjects" in iam_source
    assert '["s3:GetObject", "s3:GetObjectVersion"]' in iam_source


def test_goal5_cdc_materializes_unique_events_for_all_merges() -> None:
    """The CDC CTE must survive across the independent MERGE statements."""
    sql = (ROOT / "databricks/sql/goal_05/04_ingest_cdc.sql").read_text(encoding="utf-8")

    assert "CREATE OR REPLACE TEMP VIEW goal5_cdc_unique_events AS" in sql
    assert sql.count("FROM goal5_cdc_unique_events") == 3
    assert sql.count("FROM unique_events") == 1


def test_goal5_cdc_current_state_assertion_is_numeric_and_tombstone_aware() -> None:
    """Acceptance must not depend on a JSON serializer's `120` versus `120.0` spelling."""
    sql = (ROOT / "databricks/sql/goal_05/05_verify_goal5_outputs.sql").read_text(encoding="utf-8")

    assert "TRY_CAST(get_json_object(payload_json, '$.metric_value') AS DOUBLE)" in sql
    assert "= CAST(120 AS DOUBLE)" in sql
    assert "entity_id = 'entity-002' AND is_deleted = true" in sql
    assert "get_json_object(payload_json, '$.metric_value') = '120'" not in sql
