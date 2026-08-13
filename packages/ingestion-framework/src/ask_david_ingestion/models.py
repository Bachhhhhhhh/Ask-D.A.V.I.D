"""Typed models shared by the synthetic ingestion adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class SourceType(StrEnum):
    """Supported MVP source patterns."""

    STRUCTURED_FILE = "structured_file"
    DOCUMENT = "document"
    CDC = "cdc"


class RunStatus(StrEnum):
    """Auditable ingestion-run states."""

    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


def utc_now() -> datetime:
    """Return an aware UTC timestamp for run/provenance records."""
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class Provenance:
    """Source lineage attached to a record, document, or CDC event."""

    dataset_id: str
    source: str
    ingestion_run_id: str
    source_record_id: str | None = None
    source_version: str | None = None


@dataclass(frozen=True, slots=True)
class QuarantinedRecord:
    """An input record excluded from trusted output with a stable reason."""

    source_row_number: int
    reason_code: str
    reason: str
    raw_record: dict[str, Any]
    provenance: Provenance


@dataclass(frozen=True, slots=True)
class AdapterResult:
    """Deterministic adapter output before persistence by a controlled job."""

    accepted_records: tuple[dict[str, Any], ...]
    quarantined_records: tuple[QuarantinedRecord, ...]
    derived_records: tuple[dict[str, Any], ...]
    provenance: tuple[Provenance, ...]
    statistics: dict[str, int]


@dataclass(frozen=True, slots=True)
class IngestionRun:
    """Immutable execution metadata; credentials are intentionally absent."""

    run_id: str
    dataset_id: str
    source_type: SourceType
    source: str
    source_version: str
    started_at: datetime
    completed_at: datetime | None
    status: RunStatus
    input_count: int
    accepted_count: int
    rejected_count: int
    error_summary: str | None = None

    @classmethod
    def start(
        cls,
        *,
        run_id: str,
        dataset_id: str,
        source_type: SourceType,
        source: str,
        source_version: str,
    ) -> IngestionRun:
        """Create a run in the auditable RUNNING state."""
        return cls(
            run_id=run_id,
            dataset_id=dataset_id,
            source_type=source_type,
            source=source,
            source_version=source_version,
            started_at=utc_now(),
            completed_at=None,
            status=RunStatus.RUNNING,
            input_count=0,
            accepted_count=0,
            rejected_count=0,
        )

    def complete(
        self,
        *,
        status: RunStatus,
        input_count: int,
        accepted_count: int,
        rejected_count: int,
        error_summary: str | None = None,
    ) -> IngestionRun:
        """Return a completed copy while preserving the original start time."""
        if status is RunStatus.RUNNING:
            raise ValueError("a completed run cannot retain RUNNING status")
        for name, value in (
            ("input_count", input_count),
            ("accepted_count", accepted_count),
            ("rejected_count", rejected_count),
        ):
            if value < 0:
                raise ValueError(f"{name} must not be negative")
        return IngestionRun(
            run_id=self.run_id,
            dataset_id=self.dataset_id,
            source_type=self.source_type,
            source=self.source,
            source_version=self.source_version,
            started_at=self.started_at,
            completed_at=utc_now(),
            status=status,
            input_count=input_count,
            accepted_count=accepted_count,
            rejected_count=rejected_count,
            error_summary=error_summary,
        )


def record_copy(record: dict[str, Any]) -> dict[str, Any]:
    """Make a shallow copy with a stable type for adapter outputs."""
    return dict(record)
