"""Deterministic quality checks used by the synthetic adapters."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from ask_david_ingestion.contracts import QualityRule


@dataclass(frozen=True, slots=True)
class QualityResult:
    """One queryable quality-rule result."""

    rule_name: str
    status: str
    observed_value: int
    expected_value: int
    detail: str


def canonical_json(value: Any) -> str:
    """Serialize a value deterministically for idempotency keys."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def stable_record_hash(record: dict[str, Any]) -> str:
    """Return a SHA-256 hash without depending on dictionary insertion order."""
    return hashlib.sha256(canonical_json(record).encode("utf-8")).hexdigest()


def run_quality_rules(
    records: Iterable[dict[str, Any]],
    rules: Iterable[QualityRule],
) -> tuple[QualityResult, ...]:
    """Run only the small deterministic rules allowed by the MVP contract."""
    values = tuple(records)
    results: list[QualityResult] = []
    for rule in rules:
        if rule.name in {"required_fields", "not_null"}:
            failures = sum(
                1
                for record in values
                if any(
                    record.get(column) is None or record.get(column) == ""
                    for column in rule.columns
                )
            )
            results.append(
                QualityResult(
                    rule_name=rule.name,
                    status="PASS" if failures == 0 else "FAIL",
                    observed_value=failures,
                    expected_value=0,
                    detail="required fields must be present",
                )
            )
        elif rule.name in {"unique_primary_key", "uniqueness"}:
            keys = [tuple(record.get(column) for column in rule.columns) for record in values]
            duplicate_count = len(keys) - len(set(keys))
            results.append(
                QualityResult(
                    rule_name=rule.name,
                    status="PASS" if duplicate_count == 0 else "FAIL",
                    observed_value=duplicate_count,
                    expected_value=0,
                    detail="declared key values must be unique",
                )
            )
        else:
            results.append(
                QualityResult(
                    rule_name=rule.name,
                    status="FAIL",
                    observed_value=0,
                    expected_value=0,
                    detail="unsupported rule",
                )
            )
    return tuple(results)
