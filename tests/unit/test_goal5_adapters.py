"""Offline adapter, quarantine, quality, and CDC semantics tests."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
from ask_david_ingestion.adapters import CDCSourceAdapter, DocumentSourceAdapter, FileSourceAdapter
from ask_david_ingestion.contracts import ContractValidationError, load_contract
from ask_david_ingestion.models import IngestionRun, RunStatus, SourceType, record_copy
from ask_david_ingestion.quality import QualityRule, run_quality_rules, stable_record_hash

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "synthetic_data" / "goal_05"
CONTRACTS = FIXTURES / "contracts"


def test_structured_valid_rows_pass() -> None:
    result = FileSourceAdapter(
        load_contract(CONTRACTS / "structured.json"),
        FIXTURES / "structured" / "synthetic_events.csv",  # type: ignore[arg-type]
    ).ingest(ingestion_run_id="run-structured-1")
    assert result.statistics["accepted_count"] == 3
    assert result.statistics["rejected_count"] == 1


def test_structured_invalid_row_is_quarantined_with_reason() -> None:
    contract = load_contract(CONTRACTS / "structured.json")
    result = FileSourceAdapter(contract, FIXTURES / "structured" / "synthetic_events.csv").ingest(
        ingestion_run_id="run-structured-2"
    )
    assert len(result.quarantined_records) == 1
    assert result.quarantined_records[0].reason_code == "INVALID_TYPE"
    assert result.quarantined_records[0].provenance.ingestion_run_id == "run-structured-2"


def test_structured_duplicate_primary_key_is_deterministic() -> None:
    contract = load_contract(CONTRACTS / "structured.json")
    adapter = FileSourceAdapter(contract, FIXTURES / "structured" / "synthetic_events.csv")
    first = adapter.ingest(ingestion_run_id="run-structured-3")
    second = adapter.ingest(ingestion_run_id="run-structured-4")
    assert first.statistics["duplicate_primary_key_count"] == 1
    assert first.derived_records == second.derived_records
    assert len(first.derived_records) == 2


def test_structured_provenance_contains_dataset_source_and_run() -> None:
    contract = load_contract(CONTRACTS / "structured.json")
    result = FileSourceAdapter(contract, FIXTURES / "structured" / "synthetic_events.csv").ingest(
        ingestion_run_id="run-structured-5"
    )
    provenance = result.provenance[0]
    assert provenance.dataset_id == "goal5.synthetic.events"
    assert provenance.source == "goal5/structured/synthetic_events.csv"
    assert provenance.ingestion_run_id == "run-structured-5"


def test_structured_header_mismatch_fails_closed(tmp_path: Path) -> None:
    source = tmp_path / "wrong.csv"
    source.write_text("event_id,wrong\n1,2\n", encoding="utf-8")
    contract = load_contract(CONTRACTS / "structured.json")
    with pytest.raises(ContractValidationError, match="SCHEMA_MISMATCH"):
        FileSourceAdapter(contract, source).ingest(ingestion_run_id="run-structured-bad-header")


def test_structured_missing_source_fails_closed() -> None:
    contract = load_contract(CONTRACTS / "structured.json")
    with pytest.raises(FileNotFoundError):
        FileSourceAdapter(contract, FIXTURES / "structured" / "missing.csv").ingest(
            ingestion_run_id="run-structured-missing"
        )


def test_structured_source_type_mismatch_fails_closed() -> None:
    contract = load_contract(CONTRACTS / "structured.json")
    mismatched = replace(contract, source_type=SourceType.DOCUMENT)
    with pytest.raises(ContractValidationError, match="SOURCE_TYPE_MISMATCH"):
        FileSourceAdapter(mismatched, FIXTURES / "structured" / "synthetic_events.csv").ingest(
            ingestion_run_id="run-structured-mismatch"
        )


def test_structured_scalar_types_are_parsed(tmp_path: Path) -> None:
    source = tmp_path / "typed.csv"
    source.write_text(
        "event_id,entity_id,event_time,category,metric_value,count,enabled,payload\n"
        'evt-typed,entity-typed,2026-02-01T00:00:00Z,alpha,1.5,2,true,"{""ok"":true}"\n',
        encoding="utf-8",
    )
    contract = load_contract(CONTRACTS / "structured.json")
    typed_contract = replace(
        contract,
        schema=(
            ("event_id", "string"),
            ("entity_id", "string"),
            ("event_time", "timestamp"),
            ("category", "string"),
            ("metric_value", "double"),
            ("count", "int"),
            ("enabled", "boolean"),
            ("payload", "json"),
        ),
    )
    result = FileSourceAdapter(typed_contract, source).ingest(ingestion_run_id="run-typed")
    assert result.statistics["accepted_count"] == 1
    assert result.accepted_records[0]["count"] == 2
    assert result.accepted_records[0]["enabled"] is True
    assert result.accepted_records[0]["payload"] == {"ok": True}


def test_structured_blank_and_invalid_scalar_values_quarantine(tmp_path: Path) -> None:
    source = tmp_path / "invalid-typed.csv"
    source.write_text(
        "event_id,entity_id,event_time,category,metric_value\n"
        ",entity-1,2026-02-01T00:00:00Z,alpha,1\n"
        "evt-2,entity-2,not-time,beta,1\n",
        encoding="utf-8",
    )
    contract = load_contract(CONTRACTS / "structured.json")
    result = FileSourceAdapter(contract, source).ingest(ingestion_run_id="run-invalid-scalars")
    assert result.statistics["rejected_count"] == 2


def test_document_markdown_is_accepted_and_versioned() -> None:
    contract = load_contract(CONTRACTS / "document.json")
    result = DocumentSourceAdapter(
        contract, FIXTURES / "documents" / "neutral_technical_guide.md"
    ).ingest(ingestion_run_id="run-document-1")
    record = result.accepted_records[0]
    assert record["content_type"] == "text/markdown"
    assert len(record["document_id"]) == 24
    assert len(record["document_version"]) == 64
    assert result.provenance[0].source_record_id == record["document_id"]


def test_document_repeat_has_same_identity_and_version() -> None:
    contract = load_contract(CONTRACTS / "document.json")
    adapter = DocumentSourceAdapter(contract, FIXTURES / "documents" / "neutral_technical_guide.md")
    first = adapter.ingest(ingestion_run_id="run-document-2").accepted_records[0]
    second = adapter.ingest(ingestion_run_id="run-document-3").accepted_records[0]
    assert (first["document_id"], first["document_version"]) == (
        second["document_id"],
        second["document_version"],
    )
    assert first["ingestion_run_id"] != second["ingestion_run_id"]


def test_unsupported_document_content_type_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "unsupported.pdf"
    source.write_bytes(b"not a PDF")
    contract = load_contract(CONTRACTS / "document.json")
    with pytest.raises(ContractValidationError, match="UNSUPPORTED_CONTENT_TYPE"):
        DocumentSourceAdapter(contract, source).ingest(ingestion_run_id="run-document-4")


def test_document_invalid_utf8_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "invalid.md"
    source.write_bytes(b"\xff\xfe")
    contract = load_contract(CONTRACTS / "document.json")
    with pytest.raises(ContractValidationError, match="INVALID_TEXT"):
        DocumentSourceAdapter(contract, source).ingest(ingestion_run_id="run-document-invalid")


def test_document_metadata_contract_is_enforced() -> None:
    contract = load_contract(CONTRACTS / "document.json")
    mismatched = replace(contract, metadata_required=("missing_field",))
    with pytest.raises(ContractValidationError, match="MISSING_METADATA"):
        DocumentSourceAdapter(
            mismatched, FIXTURES / "documents" / "neutral_technical_guide.md"
        ).ingest(ingestion_run_id="run-document-metadata")


def test_document_source_type_mismatch_fails_closed() -> None:
    contract = load_contract(CONTRACTS / "document.json")
    mismatched = replace(contract, source_type=SourceType.STRUCTURED_FILE)
    with pytest.raises(ContractValidationError, match="SOURCE_TYPE_MISMATCH"):
        DocumentSourceAdapter(
            mismatched, FIXTURES / "documents" / "neutral_technical_guide.md"
        ).ingest(ingestion_run_id="run-document-mismatch")


def test_cdc_insert_update_delete_and_tombstone() -> None:
    contract = load_contract(CONTRACTS / "cdc.json")
    result = CDCSourceAdapter(contract, FIXTURES / "cdc" / "synthetic_changes.jsonl").ingest(
        ingestion_run_id="run-cdc-1"
    )
    assert result.statistics["unique_event_count"] == 4
    assert result.statistics["duplicate_event_count"] == 1
    current = {record["entity_id"]: record for record in result.derived_records}
    assert current["entity-001"]["payload"]["metric_value"] == 120
    assert current["entity-001"]["is_deleted"] is False
    assert current["entity-002"]["is_deleted"] is True
    assert current["entity-002"]["payload"] is None


def test_cdc_raw_history_retains_duplicate_occurrence_count() -> None:
    contract = load_contract(CONTRACTS / "cdc.json")
    result = CDCSourceAdapter(contract, FIXTURES / "cdc" / "synthetic_changes.jsonl").ingest(
        ingestion_run_id="run-cdc-2"
    )
    duplicate_event = next(
        record for record in result.accepted_records if record["event_id"] == "cdc-003"
    )
    assert duplicate_event["event_id"] == "cdc-003"
    assert result.statistics["duplicate_event_count"] == 1


def test_cdc_ordering_is_deterministic() -> None:
    contract = load_contract(CONTRACTS / "cdc.json")
    adapter = CDCSourceAdapter(contract, FIXTURES / "cdc" / "synthetic_changes.jsonl")
    first = adapter.ingest(ingestion_run_id="run-cdc-3")
    second = adapter.ingest(ingestion_run_id="run-cdc-4")

    def normalize(records: tuple[dict[str, object], ...]) -> tuple[dict[str, object], ...]:
        return tuple(
            {key: value for key, value in record.items() if key != "ingestion_run_id"}
            for record in records
        )

    assert normalize(first.derived_records) == normalize(second.derived_records)


def test_cdc_invalid_operation_is_quarantined(tmp_path: Path) -> None:
    source = tmp_path / "invalid.jsonl"
    source.write_text(
        json.dumps(
            {
                "event_id": "bad-1",
                "entity_id": "entity-1",
                "operation": "UPSERT",
                "event_time": "2026-02-01T00:00:00Z",
                "sequence": 1,
                "source": "synthetic",
                "payload": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    contract = load_contract(CONTRACTS / "cdc.json")
    result = CDCSourceAdapter(contract, source).ingest(ingestion_run_id="run-cdc-5")
    assert result.statistics["rejected_count"] == 1
    assert result.quarantined_records[0].reason_code == "INVALID_CDC_EVENT"


def test_cdc_invalid_json_and_non_object_are_quarantined(tmp_path: Path) -> None:
    source = tmp_path / "invalid.jsonl"
    source.write_text("not-json\n[]\n\n", encoding="utf-8")
    contract = load_contract(CONTRACTS / "cdc.json")
    result = CDCSourceAdapter(contract, source).ingest(ingestion_run_id="run-cdc-invalid-json")
    assert result.statistics["rejected_count"] == 2


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("event_id", None, "missing event_id"),
        ("event_time", "not-time", "event_time"),
        ("sequence", "bad", "sequence must be an integer"),
        ("sequence", -1, "sequence must not be negative"),
    ],
)
def test_cdc_invalid_event_fields_are_quarantined(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    event: dict[str, object] = {
        "event_id": "bad-1",
        "entity_id": "entity-1",
        "operation": "INSERT",
        "event_time": "2026-02-01T00:00:00Z",
        "sequence": 1,
        "source": "synthetic",
        "payload": {},
    }
    if value is None:
        event.pop(field)
    else:
        event[field] = value
    source = tmp_path / "invalid-event.jsonl"
    source.write_text(json.dumps(event) + "\n", encoding="utf-8")
    contract = load_contract(CONTRACTS / "cdc.json")
    result = CDCSourceAdapter(contract, source).ingest(ingestion_run_id="run-cdc-invalid-field")
    assert result.statistics["rejected_count"] == 1
    assert message in result.quarantined_records[0].reason


def test_cdc_missing_source_and_type_mismatch_fail_closed() -> None:
    contract = load_contract(CONTRACTS / "cdc.json")
    with pytest.raises(FileNotFoundError):
        CDCSourceAdapter(contract, FIXTURES / "cdc" / "missing.jsonl").ingest(
            ingestion_run_id="run-cdc-missing"
        )
    mismatched = replace(contract, source_type=SourceType.DOCUMENT)
    with pytest.raises(ContractValidationError, match="SOURCE_TYPE_MISMATCH"):
        CDCSourceAdapter(mismatched, FIXTURES / "cdc" / "synthetic_changes.jsonl").ingest(
            ingestion_run_id="run-cdc-mismatch"
        )


def test_required_quality_rule_passes() -> None:
    contract = load_contract(CONTRACTS / "structured.json")
    records = [{"event_id": "a", "entity_id": "e", "event_time": "t"}]
    result = run_quality_rules(records, contract.quality_rules[:1])
    assert result[0].status == "PASS"
    assert result[0].observed_value == 0


def test_uniqueness_quality_rule_detects_duplicate() -> None:
    contract = load_contract(CONTRACTS / "structured.json")
    records = [{"event_id": "a"}, {"event_id": "a"}]
    result = run_quality_rules(records, contract.quality_rules[1:])
    assert result[0].status == "FAIL"
    assert result[0].observed_value == 1


def test_record_hash_is_order_independent() -> None:
    assert stable_record_hash({"a": 1, "b": 2}) == stable_record_hash({"b": 2, "a": 1})


def test_quality_unsupported_rule_fails() -> None:
    result = run_quality_rules([{"id": "one"}], (QualityRule("unsupported", ("id",)),))
    assert result[0].status == "FAIL"


def test_ingestion_run_rejects_running_and_negative_completion() -> None:
    started = IngestionRun.start(
        run_id="run-model-errors",
        dataset_id="goal5.synthetic.events",
        source_type=SourceType.STRUCTURED_FILE,
        source="goal5/structured/synthetic_events.csv",
        source_version="1.0",
    )
    with pytest.raises(ValueError, match="RUNNING"):
        started.complete(
            status=RunStatus.RUNNING, input_count=0, accepted_count=0, rejected_count=0
        )
    with pytest.raises(ValueError, match="must not be negative"):
        started.complete(
            status=RunStatus.FAILED, input_count=-1, accepted_count=0, rejected_count=0
        )
    assert record_copy({"id": 1}) == {"id": 1}


def test_ingestion_run_is_auditable_and_immutable() -> None:
    started = IngestionRun.start(
        run_id="run-model-1",
        dataset_id="goal5.synthetic.events",
        source_type=SourceType.STRUCTURED_FILE,
        source="goal5/structured/synthetic_events.csv",
        source_version="1.0",
    )
    completed = started.complete(
        status=RunStatus.PARTIAL,
        input_count=4,
        accepted_count=3,
        rejected_count=1,
        error_summary="one row quarantined",
    )
    assert completed.run_id == started.run_id
    assert completed.started_at == started.started_at
    assert completed.completed_at is not None
    assert completed.status is RunStatus.PARTIAL
    assert completed.error_summary == "one row quarantined"
