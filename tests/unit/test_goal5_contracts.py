"""Offline contract validation coverage for Goal 5."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from ask_david_ingestion.contracts import (
    CDCContract,
    ContractValidationError,
    DocumentContract,
    StructuredContract,
    load_contract,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "synthetic_data" / "goal_05" / "contracts"


def test_valid_structured_contract_passes() -> None:
    contract = load_contract(CONTRACTS / "structured.json")
    assert isinstance(contract, StructuredContract)
    assert contract.primary_key == ("event_id",)
    assert contract.source == "goal5/structured/synthetic_events.csv"


def test_valid_document_contract_passes() -> None:
    contract = load_contract(CONTRACTS / "document.json")
    assert isinstance(contract, DocumentContract)
    assert "text/markdown" in contract.allowed_content_types


def test_valid_cdc_contract_passes() -> None:
    contract = load_contract(CONTRACTS / "cdc.json")
    assert isinstance(contract, CDCContract)
    assert contract.operation_field == "operation"
    assert contract.sequence_field == "sequence"


def test_missing_common_field_fails(tmp_path: Path) -> None:
    raw = json.loads((CONTRACTS / "structured.json").read_text(encoding="utf-8"))
    del raw["dataset_id"]
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ContractValidationError, match="REQUIRED_FIELD"):
        load_contract(path)


def test_unknown_field_fails(tmp_path: Path) -> None:
    raw = json.loads((CONTRACTS / "document.json").read_text(encoding="utf-8"))
    raw["unexpected_field"] = "never-allowed"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ContractValidationError, match="UNKNOWN_FIELD"):
        load_contract(path)


def test_unsafe_source_key_fails(tmp_path: Path) -> None:
    raw = json.loads((CONTRACTS / "cdc.json").read_text(encoding="utf-8"))
    raw["source"] = "s3://unapproved-bucket/file.jsonl"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ContractValidationError, match="UNSAFE_SOURCE"):
        load_contract(path)


def test_unsafe_target_catalog_fails(tmp_path: Path) -> None:
    raw = json.loads((CONTRACTS / "structured.json").read_text(encoding="utf-8"))
    raw["target_catalog"] = "workspace"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ContractValidationError, match="UNSAFE_TARGET_CATALOG"):
        load_contract(path)


def test_plain_delta_policy_declaration_fails(tmp_path: Path) -> None:
    raw = json.loads((CONTRACTS / "structured.json").read_text(encoding="utf-8"))
    raw["table_format_policy"] = "plain-delta"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ContractValidationError, match="UNSUPPORTED_TABLE_POLICY"):
        load_contract(path)


def test_unsupported_document_content_type_fails(tmp_path: Path) -> None:
    raw = json.loads((CONTRACTS / "document.json").read_text(encoding="utf-8"))
    raw["allowed_content_types"] = ["application/pdf"]
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ContractValidationError, match="UNSUPPORTED_CONTENT_TYPE"):
        load_contract(path)


def test_unsupported_document_metadata_field_fails(tmp_path: Path) -> None:
    raw = json.loads((CONTRACTS / "document.json").read_text(encoding="utf-8"))
    raw["metadata_required"].append("raw_content")
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ContractValidationError, match="UNSUPPORTED_METADATA_FIELD"):
        load_contract(path)


def test_invalid_json_fails(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(ContractValidationError, match="INVALID_JSON"):
        load_contract(path)


@pytest.mark.parametrize(
    ("filename", "updates", "error_code"),
    [
        ("structured.json", {"quality_rules": []}, "REQUIRED_LIST"),
        (
            "structured.json",
            {"quality_rules": [{"name": "unknown", "columns": [], "extra": 1}]},
            "UNSUPPORTED_RULE",
        ),
        ("structured.json", {"source_type": "other"}, "UNSUPPORTED_SOURCE_TYPE"),
        ("structured.json", {"target_schema": "not-approved"}, "UNSAFE_TARGET_SCHEMA"),
        ("structured.json", {"target_table": "not-goal5"}, "UNSAFE_TARGET_TABLE"),
        ("structured.json", {"sensitivity_classification": "restricted"}, "UNSAFE_CLASSIFICATION"),
        ("structured.json", {"schema": []}, "REQUIRED_OBJECT"),
        (
            "structured.json",
            {"schema": {"event_id": "unsupported"}},
            "UNSUPPORTED_SCHEMA_TYPE",
        ),
        ("structured.json", {"primary_key": ["missing"]}, "UNKNOWN_COLUMN"),
        ("document.json", {"document_id_strategy": "random"}, "UNSUPPORTED_ID_STRATEGY"),
        ("cdc.json", {"unknown": True}, "UNKNOWN_FIELD"),
        ("cdc.json", {"sequence_field": "event_id"}, "DUPLICATE_FIELD"),
    ],
)
def test_contract_invalid_variants_fail_closed(
    tmp_path: Path, filename: str, updates: dict[str, object], error_code: str
) -> None:
    raw = json.loads((CONTRACTS / filename).read_text(encoding="utf-8"))
    raw.update(updates)
    path = tmp_path / f"invalid-{error_code}.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ContractValidationError, match=error_code):
        load_contract(path)


def test_contract_non_object_root_fails(tmp_path: Path) -> None:
    path = tmp_path / "list.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ContractValidationError, match="INVALID_ROOT"):
        load_contract(path)
