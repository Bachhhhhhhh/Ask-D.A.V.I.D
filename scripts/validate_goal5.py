"""Offline static validation for the Goal 5 synthetic ingestion contract."""

from __future__ import annotations

import argparse
import re
from collections.abc import Iterable
from pathlib import Path

from ask_david_ingestion.contracts import ContractValidationError, load_contract

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_NAMES = ("structured", "document", "cdc")
SQL_NAMES = (
    "01_create_goal5_tables.sql",
    "02_ingest_structured_csv.sql",
    "03_ingest_document.sql",
    "04_ingest_cdc.sql",
    "05_verify_goal5_outputs.sql",
    "06_verify_goal5_idempotency.sql",
)
SOURCE_PATH_GUARDS = {
    "02_ingest_structured_csv.sql": "unity-catalog/development/goal5/structured/",
    "03_ingest_document.sql": "unity-catalog/development/goal5/documents/",
    "04_ingest_cdc.sql": "unity-catalog/development/goal5/cdc/",
}
TABLE_NAMES = (
    "goal5_ingestion_runs",
    "goal5_quality_results",
    "goal5_structured_raw_events",
    "goal5_structured_quarantine",
    "goal5_structured_curated_events",
    "goal5_structured_business_metrics",
    "goal5_document_metadata",
    "goal5_cdc_history",
    "goal5_cdc_current_state",
)
FORBIDDEN_SCOPE = re.compile(r"(?i)(doris|opensearch|langgraph|supervisor|specialized.?agent)")
SECRET_MARKERS = re.compile(
    r"(?i)(aws_secret_access_key|aws_access_key_id|client_secret|password\s*=|pat\s*=|token\s*=)"
)


def _contains_all(text: str, values: Iterable[str]) -> list[str]:
    return [value for value in values if value not in text]


def validate_goal5_repository(repository_root: Path = REPOSITORY_ROOT) -> list[str]:
    """Return deterministic static-contract errors without cloud access."""
    errors: list[str] = []
    contract_dir = repository_root / "synthetic_data" / "goal_05" / "contracts"
    fixture_dir = repository_root / "synthetic_data" / "goal_05"
    sql_dir = repository_root / "databricks" / "sql" / "goal_05"
    bundle_root = repository_root / "databricks" / "databricks.yml"
    resource_path = (
        repository_root / "databricks" / "bundles" / "goal_05_ingestion" / "resources.yml"
    )
    terraform_path = (
        repository_root / "infrastructure" / "environments" / "development" / "goal5.tf"
    )
    local_path = repository_root / "infrastructure" / "environments" / "development" / "locals.tf"
    goal4_path = repository_root / "infrastructure" / "environments" / "development" / "goal4.tf"
    lakehouse_path = (
        repository_root / "infrastructure" / "modules" / "databricks-lakehouse" / "main.tf"
    )
    aws_storage_path = (
        repository_root / "infrastructure" / "modules" / "databricks-aws-storage" / "main.tf"
    )

    for name in CONTRACT_NAMES:
        path = contract_dir / f"{name}.json"
        if not path.is_file():
            errors.append(f"missing Goal 5 contract: {path.relative_to(repository_root)}")
            continue
        try:
            contract = load_contract(path)
        except ContractValidationError as error:
            errors.append(f"invalid Goal 5 contract {name}: {error}")
            continue
        if contract.target_catalog != "ask_david_development":
            errors.append(f"Goal 5 contract {name} must target the development catalog")
        if contract.table_format_policy != "iceberg-or-delta-uniform-iceberg":
            errors.append(f"Goal 5 contract {name} has an unsupported table-format policy")

    fixture_paths = (
        fixture_dir / "structured" / "synthetic_events.csv",
        fixture_dir / "documents" / "neutral_technical_guide.md",
        fixture_dir / "cdc" / "synthetic_changes.jsonl",
    )
    for path in fixture_paths:
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty Goal 5 fixture: {path.relative_to(repository_root)}")

    for sql_name in SQL_NAMES:
        path = sql_dir / sql_name
        if not path.is_file():
            errors.append(f"missing Goal 5 SQL: {path.relative_to(repository_root)}")
            continue
        text = path.read_text(encoding="utf-8")
        if "goal-05" not in text and sql_name != "05_verify_goal5_outputs.sql":
            errors.append(f"Goal 5 SQL missing goal-05 marker: {sql_name}")
        if re.search(r"(?im)^\s*LOCATION\s+['\"]", text):
            errors.append(f"Goal 5 SQL must not create unmanaged LOCATION tables: {sql_name}")
        if SECRET_MARKERS.search(text):
            errors.append(f"Goal 5 SQL contains a credential marker: {sql_name}")
        if sql_name in SOURCE_PATH_GUARDS and SOURCE_PATH_GUARDS[sql_name] not in text:
            errors.append(f"Goal 5 SQL is missing approved source-path guard: {sql_name}")
        if sql_name.startswith("05_") or sql_name.startswith("06_"):
            executable_text = re.sub(r"(?m)--.*$", "", text)
            forbidden_mutation = re.search(
                r"(?im)^\s*(CREATE|ALTER|DROP|TRUNCATE|INSERT|UPDATE|DELETE|MERGE)\b",
                executable_text,
            )
            if forbidden_mutation:
                errors.append(f"Goal 5 verification SQL must be read-only: {sql_name}")
        elif sql_name == "01_create_goal5_tables.sql" and "USING ICEBERG" not in text:
            errors.append(f"Goal 5 table-creation SQL must declare USING ICEBERG: {sql_name}")

    create_sql = (
        (sql_dir / SQL_NAMES[0]).read_text(encoding="utf-8")
        if (sql_dir / SQL_NAMES[0]).is_file()
        else ""
    )
    if len(re.findall(r"(?im)^CREATE TABLE IF NOT EXISTS", create_sql)) != len(TABLE_NAMES):
        errors.append("Goal 5 must declare exactly nine managed source-of-truth tables")
    for table_name in TABLE_NAMES:
        if (
            f"goal5_{table_name.removeprefix('goal5_')}" not in create_sql
            and table_name not in create_sql
        ):
            errors.append(f"Goal 5 table creation SQL is missing {table_name}")
    required_common_sql_markers = (
        "ingestion_run_id",
        "source_uri",
        "validation_status",
        "table_format_policy",
    )
    for marker in _contains_all(create_sql, required_common_sql_markers):
        errors.append(f"Goal 5 table creation SQL is missing common contract field {marker}")
    for sql_name, markers in {
        "02_ingest_structured_csv.sql": (
            "goal5_structured_run_context",
            "goal5_structured_valid_rows",
            "goal5_structured_invalid_rows",
        ),
        "03_ingest_document.sql": (
            "goal5_document_run_context",
            "document_version",
            "validation_status",
            "source_uri",
        ),
        "04_ingest_cdc.sql": (
            "goal5_cdc_run_context",
            "CREATE OR REPLACE TEMP VIEW goal5_cdc_unique_events AS",
            "FROM goal5_cdc_unique_events",
            "event_id",
            "sequence",
            "validation_status",
        ),
    }.items():
        text = (
            (sql_dir / sql_name).read_text(encoding="utf-8")
            if (sql_dir / sql_name).is_file()
            else ""
        )
        for marker in _contains_all(text, markers):
            errors.append(f"{sql_name} is missing required validation/provenance marker: {marker}")

    output_verification = (
        (sql_dir / "05_verify_goal5_outputs.sql").read_text(encoding="utf-8")
        if (sql_dir / "05_verify_goal5_outputs.sql").is_file()
        else ""
    )
    numeric_metric_assertion = "TRY_CAST(get_json_object(payload_json, '$.metric_value') AS DOUBLE)"
    if numeric_metric_assertion not in output_verification:
        errors.append("Goal 5 CDC output verification must compare metric_value numerically")
    if "entity_id = 'entity-002' AND is_deleted = true" not in output_verification:
        errors.append("Goal 5 CDC output verification must assert the DELETE tombstone")
    if "get_json_object(payload_json, '$.metric_value') = '120'" in output_verification:
        errors.append("Goal 5 CDC output verification must not rely on JSON numeric spelling")

    if not bundle_root.is_file():
        errors.append("missing shared Databricks bundle root")
    else:
        bundle_text = bundle_root.read_text(encoding="utf-8")
        required_bundle_markers = (
            "- bundles/goal_05_ingestion/resources.yml",
            "goal5_structured_source_uri:",
            "goal5_document_source_uri:",
            "goal5_cdc_source_uri:",
            "- sql/goal_05/*.sql",
        )
        for marker in _contains_all(bundle_text, required_bundle_markers):
            errors.append(f"shared bundle root is missing Goal 5 marker: {marker}")
        if "workspace_host:" in bundle_text or "${var.workspace_host}" in bundle_text:
            errors.append("Goal 5 must preserve profile-based bundle authentication")

    if not resource_path.is_file():
        errors.append("missing Goal 5 bundle resource manifest")
    else:
        resource_text = resource_path.read_text(encoding="utf-8")
        required_resource_markers = (
            "goal5_synthetic_ingestion",
            "warehouse_id: ${var.warehouse_id}",
            "goal_05/01_create_goal5_tables.sql",
            "goal_05/05_verify_goal5_outputs.sql",
            "goal_05/06_verify_goal5_idempotency.sql",
        )
        for marker in _contains_all(resource_text, required_resource_markers):
            errors.append(f"Goal 5 bundle resource missing: {marker}")
        if re.search(r"(?i)\b(cluster|warehouse)\s*:\s*", resource_text):
            errors.append("Goal 5 bundle must reuse the existing warehouse and declare no compute")

    if not terraform_path.is_file():
        errors.append("missing Terraform-managed Goal 5 source fixture resources")
    else:
        terraform_text = terraform_path.read_text(encoding="utf-8")
        if terraform_text.count('resource "aws_s3_object"') != 3:
            errors.append(
                "Goal 5 Terraform source fixture contract must contain exactly "
                "three aws_s3_object resources"
            )
        if 'server_side_encryption = "aws:kms"' not in terraform_text:
            errors.append("Goal 5 source fixtures must use SSE-KMS")
        if "module.kms.storage_key_arn" not in terraform_text:
            errors.append("Goal 5 source fixtures must use the existing storage KMS key")
        if terraform_text.count("count        = var.goal_5_source_objects_enabled ? 1 : 0") != 3:
            errors.append(
                "Goal 5 source fixture objects must be disabled by default behind the approval flag"
            )

    source_access_paths = (local_path, goal4_path, lakehouse_path, aws_storage_path)
    if not all(path.is_file() for path in source_access_paths):
        errors.append("Goal 5 source access remediation is missing Terraform source")
    else:
        local_text = local_path.read_text(encoding="utf-8")
        goal4_text = goal4_path.read_text(encoding="utf-8")
        lakehouse_text = lakehouse_path.read_text(encoding="utf-8")
        aws_storage_text = aws_storage_path.read_text(encoding="utf-8")
        required_source_access = {
            "locals": (
                "goal5_raw_sources",
                "goal5_document_sources",
                '"${local.goal_4_managed_prefix}/goal5"',
                '"${local.goal_4_managed_prefix}/goal5/documents"',
            ),
            "goal4": (
                "source_read_prefixes",
                "source_read_object_arns",
                "source_external_location_urls",
                "workflow_service_principal_application_id",
            ),
            "lakehouse": (
                "source_external_location_urls",
                "workflow_service_principal_application_id",
                'privileges = ["READ_FILES"]',
                "read_only       = contains(keys(var.source_external_location_urls), each.key)",
            ),
            "aws_storage": (
                "ListApprovedIngestionSourcePrefixes",
                "ReadApprovedIngestionSourceObjects",
                '["s3:GetObject", "s3:GetObjectVersion"]',
            ),
        }
        for label, required_markers in required_source_access.items():
            source = {
                "locals": local_text,
                "goal4": goal4_text,
                "lakehouse": lakehouse_text,
                "aws_storage": aws_storage_text,
            }[label]
            for marker in _contains_all(source, required_markers):
                errors.append(f"Goal 5 source access remediation is missing {label}:{marker}")
        if lakehouse_text.count('privileges = ["READ_FILES"]') != 1:
            errors.append("Goal 5 must grant READ_FILES exactly once to its workflow principal")
        if "WRITE_FILES" in lakehouse_text:
            errors.append("Goal 5 source locations must not grant WRITE_FILES")
        source_read_statement = aws_storage_text.split("ReadApprovedIngestionSourceObjects", 1)[
            -1
        ].split("statement {", 1)[0]
        if "s3:PutObject" in source_read_statement:
            errors.append("Goal 5 source IAM permission must remain read-only")

    for path in (resource_path, terraform_path, bundle_root):
        if path.is_file() and FORBIDDEN_SCOPE.search(path.read_text(encoding="utf-8")):
            errors.append(f"Goal 5 configuration contains deferred/future scope: {path.name}")

    return errors


def main() -> int:
    """Run the credential-free validator."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    arguments = parser.parse_args()
    errors = validate_goal5_repository(arguments.repository_root.resolve())
    if errors:
        print("Goal 5 static validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Goal 5 static validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
