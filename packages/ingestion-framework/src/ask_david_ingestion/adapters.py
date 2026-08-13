"""Credential-free SourceAdapter implementations for Goal 5 synthetic data."""

from __future__ import annotations

import csv
import hashlib
import json
import mimetypes
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, TypeVar

from ask_david_ingestion.contracts import (
    CDCContract,
    Contract,
    ContractValidationError,
    DocumentContract,
    StructuredContract,
)
from ask_david_ingestion.models import (
    AdapterResult,
    Provenance,
    QuarantinedRecord,
    SourceType,
    utc_now,
)
from ask_david_ingestion.quality import stable_record_hash

Record = dict[str, Any]
ContractT = TypeVar("ContractT", bound=Contract)


class SourceAdapter(Protocol[ContractT]):
    """Typed boundary between a source representation and controlled persistence."""

    contract: ContractT

    def ingest(self, *, ingestion_run_id: str) -> AdapterResult:
        """Read the configured source and return deterministic records."""


def _parse_timestamp(value: Any, path: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} must be a non-blank ISO-8601 timestamp")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{path} must be a valid ISO-8601 timestamp") from error


def _parse_scalar(value: Any, type_name: str, path: str) -> Any:
    if value is None:
        raise ValueError(f"{path} is null")
    if type_name == "string":
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{path} must be a non-blank string")
        return value.strip()
    if type_name == "timestamp":
        return _parse_timestamp(value, path)
    if type_name == "double":
        return float(value)
    if type_name == "int":
        return int(value)
    if type_name == "boolean":
        normalized = str(value).strip().lower()
        if normalized not in {"true", "false"}:
            raise ValueError(f"{path} must be true or false")
        return normalized == "true"
    if type_name == "json":
        if isinstance(value, (dict, list)):
            return value
        return json.loads(str(value))
    raise ValueError(f"{path} has unsupported type {type_name}")


def _provenance(
    contract: Contract, run_id: str, source_record_id: str, version: str | None = None
) -> Provenance:
    return Provenance(
        dataset_id=contract.dataset_id,
        source=contract.source,
        ingestion_run_id=run_id,
        source_record_id=source_record_id,
        source_version=version,
    )


class FileSourceAdapter:
    """CSV adapter with typed row validation, quarantine, and deterministic deduplication."""

    def __init__(self, contract: StructuredContract, source_path: Path) -> None:
        self.contract = contract
        self.source_path = source_path

    def ingest(self, *, ingestion_run_id: str) -> AdapterResult:
        if self.contract.source_type is not SourceType.STRUCTURED_FILE:
            raise ContractValidationError(
                (("SOURCE_TYPE_MISMATCH", "source_type", "expected structured_file"),)
            )
        if not self.source_path.is_file():
            raise FileNotFoundError(self.source_path)
        fields = tuple(name for name, _ in self.contract.schema)
        accepted: list[Record] = []
        quarantined: list[QuarantinedRecord] = []
        provenance: list[Provenance] = []
        with self.source_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != fields:
                raise ContractValidationError(
                    (
                        (
                            "SCHEMA_MISMATCH",
                            "schema",
                            "CSV headers do not exactly match the contract",
                        ),
                    )
                )
            for row_number, raw_row in enumerate(reader, start=2):
                raw_record = {key: value for key, value in raw_row.items() if key is not None}
                try:
                    parsed = {
                        name: _parse_scalar(
                            raw_record.get(name), type_name, f"row {row_number}.{name}"
                        )
                        for name, type_name in self.contract.schema
                    }
                except (TypeError, ValueError, json.JSONDecodeError) as error:
                    quarantined.append(
                        QuarantinedRecord(
                            source_row_number=row_number,
                            reason_code="INVALID_TYPE",
                            reason=str(error),
                            raw_record=raw_record,
                            provenance=_provenance(
                                self.contract, ingestion_run_id, str(row_number)
                            ),
                        )
                    )
                    continue
                parsed["source_row_number"] = row_number
                parsed["source_file"] = self.contract.source
                parsed["record_hash"] = stable_record_hash(parsed)
                accepted.append(parsed)
                provenance.append(
                    _provenance(
                        self.contract, ingestion_run_id, str(row_number), parsed["record_hash"]
                    )
                )
        grouped: dict[tuple[Any, ...], list[Record]] = defaultdict(list)
        for record in accepted:
            grouped[tuple(record[key] for key in self.contract.primary_key)].append(record)
        derived: list[Record] = []
        duplicate_count = 0
        for candidates in grouped.values():
            duplicate_count += max(0, len(candidates) - 1)
            derived.append(
                max(candidates, key=lambda item: (item["source_row_number"], item["record_hash"]))
            )
        derived.sort(
            key=lambda item: (
                tuple(item[key] for key in self.contract.primary_key),
                item["record_hash"],
            )
        )
        return AdapterResult(
            accepted_records=tuple(accepted),
            quarantined_records=tuple(quarantined),
            derived_records=tuple(derived),
            provenance=tuple(provenance),
            statistics={
                "input_count": len(accepted) + len(quarantined),
                "accepted_count": len(accepted),
                "rejected_count": len(quarantined),
                "duplicate_primary_key_count": duplicate_count,
                "curated_count": len(derived),
            },
        )


class DocumentSourceAdapter:
    """TXT/Markdown adapter that emits metadata without parsing document semantics."""

    def __init__(
        self,
        contract: DocumentContract,
        source_path: Path,
        *,
        source_system: str = "goal5-synthetic-fixture",
        classification: str = "synthetic_technical",
    ) -> None:
        self.contract = contract
        self.source_path = source_path
        self.source_system = source_system
        self.classification = classification

    def ingest(self, *, ingestion_run_id: str) -> AdapterResult:
        if self.contract.source_type is not SourceType.DOCUMENT:
            raise ContractValidationError(
                (("SOURCE_TYPE_MISMATCH", "source_type", "expected document"),)
            )
        content_type, _ = mimetypes.guess_type(self.source_path.name)
        content_type = content_type or "application/octet-stream"
        if content_type not in self.contract.allowed_content_types:
            raise ContractValidationError(
                (("UNSUPPORTED_CONTENT_TYPE", "content_type", content_type),)
            )
        content = self.source_path.read_bytes()
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ContractValidationError((("INVALID_TEXT", "document", str(error)),)) from error
        content_sha256 = hashlib.sha256(content).hexdigest()
        source_identity = f"{self.contract.dataset_id}:{self.contract.source}"
        document_id = hashlib.sha256(source_identity.encode("utf-8")).hexdigest()[:24]
        record = {
            "document_id": document_id,
            "document_version": content_sha256,
            "filename": self.source_path.name,
            "content_type": content_type,
            "source_uri": self.contract.source,
            "source_system": self.source_system,
            "ingestion_run_id": ingestion_run_id,
            "ingested_at": utc_now().isoformat(),
            "classification": self.classification,
            "content_size_bytes": len(content),
            "content_sha256": content_sha256,
        }
        missing_metadata = sorted(set(self.contract.metadata_required).difference(record))
        if missing_metadata:
            raise ContractValidationError(
                (("MISSING_METADATA", "metadata_required", ",".join(missing_metadata)),)
            )
        provenance = _provenance(self.contract, ingestion_run_id, document_id, content_sha256)
        return AdapterResult(
            accepted_records=(record,),
            quarantined_records=(),
            derived_records=(record,),
            provenance=(provenance,),
            statistics={"input_count": 1, "accepted_count": 1, "rejected_count": 0},
        )


class CDCSourceAdapter:
    """JSONL CDC adapter with event deduplication, ordering, and tombstones."""

    def __init__(self, contract: CDCContract, source_path: Path) -> None:
        self.contract = contract
        self.source_path = source_path

    def ingest(self, *, ingestion_run_id: str) -> AdapterResult:
        if self.contract.source_type is not SourceType.CDC:
            raise ContractValidationError(
                (("SOURCE_TYPE_MISMATCH", "source_type", "expected cdc"),)
            )
        if not self.source_path.is_file():
            raise FileNotFoundError(self.source_path)
        accepted: list[Record] = []
        quarantined: list[QuarantinedRecord] = []
        provenance: list[Provenance] = []
        with self.source_path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                raw: object = None
                try:
                    raw = json.loads(line)
                    if not isinstance(raw, dict):
                        raise ValueError("event must be an object")
                    event = self._validate_event(raw, line_number)
                except (TypeError, ValueError, json.JSONDecodeError) as error:
                    quarantined.append(
                        QuarantinedRecord(
                            source_row_number=line_number,
                            reason_code="INVALID_CDC_EVENT",
                            reason=str(error),
                            raw_record=raw if isinstance(raw, dict) else {"raw": line.rstrip()},
                            provenance=_provenance(
                                self.contract, ingestion_run_id, str(line_number)
                            ),
                        )
                    )
                    continue
                event["source_line_number"] = line_number
                event["source_hash"] = stable_record_hash(event)
                accepted.append(event)
                provenance.append(
                    _provenance(
                        self.contract, ingestion_run_id, event[self.contract.event_id_field]
                    )
                )
        by_event_id: dict[str, list[Record]] = defaultdict(list)
        for event in accepted:
            by_event_id[str(event[self.contract.event_id_field])].append(event)
        unique_events: list[Record] = []
        duplicate_occurrences = 0
        for events in by_event_id.values():
            selected = min(
                events,
                key=lambda item: (item[self.contract.sequence_field], item["source_line_number"]),
            )
            selected = dict(selected)
            selected["duplicate_occurrence_count"] = len(events)
            selected["duplicate_event"] = len(events) > 1
            unique_events.append(selected)
            duplicate_occurrences += max(0, len(events) - 1)
        unique_events.sort(
            key=lambda item: (
                tuple(str(item.get(key, "")) for key in self.contract.primary_key),
                item[self.contract.event_time_field],
                item[self.contract.sequence_field],
                str(item[self.contract.event_id_field]),
            )
        )
        current: dict[tuple[Any, ...], Record] = {}
        for event in unique_events:
            key = tuple(event[field] for field in self.contract.primary_key)
            operation = str(event[self.contract.operation_field]).upper()
            current[key] = {
                "entity_id": key[0] if len(key) == 1 else json.dumps(key),
                "operation_applied": operation,
                "event_id": event[self.contract.event_id_field],
                "event_time": event[self.contract.event_time_field],
                "sequence": event[self.contract.sequence_field],
                "payload": None if operation == "DELETE" else event.get("payload"),
                "is_deleted": operation == "DELETE",
                "source": event.get("source", self.contract.source),
                "ingestion_run_id": ingestion_run_id,
            }
        return AdapterResult(
            accepted_records=tuple(accepted),
            quarantined_records=tuple(quarantined),
            derived_records=tuple(current.values()),
            provenance=tuple(provenance),
            statistics={
                "input_count": len(accepted) + len(quarantined),
                "accepted_count": len(accepted),
                "rejected_count": len(quarantined),
                "unique_event_count": len(unique_events),
                "duplicate_event_count": duplicate_occurrences,
                "current_state_count": len(current),
            },
        )

    def _validate_event(self, raw: dict[str, Any], line_number: int) -> Record:
        required = (
            *self.contract.primary_key,
            self.contract.operation_field,
            self.contract.event_id_field,
            self.contract.event_time_field,
            self.contract.sequence_field,
            "source",
            "payload",
        )
        for field in required:
            if field not in raw:
                raise ValueError(f"line {line_number} missing {field}")
        operation = str(raw[self.contract.operation_field]).upper()
        if operation not in {"INSERT", "UPDATE", "DELETE"}:
            raise ValueError(f"line {line_number} has unsupported operation {operation}")
        _parse_timestamp(raw[self.contract.event_time_field], f"line {line_number}.event_time")
        try:
            sequence = int(raw[self.contract.sequence_field])
        except (TypeError, ValueError) as error:
            raise ValueError(f"line {line_number} sequence must be an integer") from error
        if sequence < 0:
            raise ValueError(f"line {line_number} sequence must not be negative")
        result = dict(raw)
        result[self.contract.operation_field] = operation
        result[self.contract.sequence_field] = sequence
        return result
