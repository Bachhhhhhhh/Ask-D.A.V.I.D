"""Fail-closed verification of a sanitized Goal 5 Tables API inventory."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

EXPECTED_GOAL5_TABLES = frozenset(
    {
        "ask_david_development.green_sm_platform.goal5_ingestion_runs",
        "ask_david_development.green_sm_platform.goal5_quality_results",
        "ask_david_development.green_sm_raw.goal5_structured_raw_events",
        "ask_david_development.green_sm_raw.goal5_structured_quarantine",
        "ask_david_development.green_sm_curated.goal5_structured_curated_events",
        "ask_david_development.green_sm_business.goal5_structured_business_metrics",
        "ask_david_development.green_sm_ai.goal5_document_metadata",
        "ask_david_development.green_sm_raw.goal5_cdc_history",
        "ask_david_development.green_sm_curated.goal5_cdc_current_state",
    }
)


def _table_list(payload: object) -> list[object] | None:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, Mapping):
        tables = payload.get("tables")
        if isinstance(tables, list):
            return tables
    return None


def _properties(table: Mapping[str, Any], full_name: str, errors: list[str]) -> Mapping[str, Any]:
    value = table.get("properties")
    if not isinstance(value, Mapping):
        errors.append(f"{full_name} must include table properties")
        return {}
    return value


def _metadata_path(properties: Mapping[str, Any]) -> str | None:
    for key in ("write.metadata.path", "metadata_location", "metadata_path"):
        value = properties.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def classify_table(table: Mapping[str, Any], errors: list[str]) -> str:
    """Classify one managed table as ICEBERG or DELTA_UNIFORM_ICEBERG."""
    full_name = str(table.get("full_name", "<unknown>"))
    if table.get("table_type") != "MANAGED":
        errors.append(f"{full_name} must have table_type MANAGED")
    properties = _properties(table, full_name, errors)
    data_format = str(table.get("data_source_format", "")).upper()
    metadata_path = _metadata_path(properties)
    if metadata_path is None or "/_iceberg/metadata" not in metadata_path:
        errors.append(f"{full_name} must expose an approved Iceberg metadata path")

    delta_properties = {
        str(key).lower(): str(value).lower()
        for key, value in properties.items()
        if str(key).lower().startswith("delta.")
    }
    if data_format == "ICEBERG":
        if delta_properties:
            errors.append(f"{full_name} native ICEBERG entry contains Delta properties")
        return "ICEBERG"

    if data_format == "DELTA":
        enabled_formats = delta_properties.get("delta.universalformat.enabledformats", "")
        compat_v2 = delta_properties.get("delta.enableicebergcompatv2", "")
        if "iceberg" not in enabled_formats or compat_v2 not in {"true", "1"}:
            errors.append(
                f"{full_name} is plain DELTA or lacks explicit UniForm Iceberg compatibility"
            )
            return "PLAIN_DELTA"
        return "DELTA_UNIFORM_ICEBERG"

    errors.append(f"{full_name} has unsupported data_source_format {data_format or '<missing>'}")
    return "OTHER"


def validate_goal5_table_inventory(
    payload: object, expected_tables: frozenset[str] = EXPECTED_GOAL5_TABLES
) -> tuple[list[str], dict[str, str]]:
    """Return errors and authoritative format classifications for a sanitized inventory."""
    tables = _table_list(payload)
    if tables is None:
        return ["inventory must be a JSON array or an object containing a tables array"], {}

    errors: list[str] = []
    indexed: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(tables):
        if not isinstance(item, Mapping):
            errors.append(f"inventory entry {index} must be a JSON object")
            continue
        full_name = item.get("full_name")
        if not isinstance(full_name, str) or not full_name:
            errors.append(f"inventory entry {index} is missing full_name")
            continue
        if full_name in indexed:
            errors.append(f"inventory contains duplicate table {full_name}")
            continue
        indexed[full_name] = item

    missing = sorted(expected_tables.difference(indexed))
    unexpected = sorted(set(indexed).difference(expected_tables))
    if missing:
        errors.append("inventory is missing expected tables: " + ", ".join(missing))
    if unexpected:
        errors.append("inventory contains unexpected tables: " + ", ".join(unexpected))

    classifications: dict[str, str] = {}
    for full_name in sorted(expected_tables.intersection(indexed)):
        classifications[full_name] = classify_table(indexed[full_name], errors)
    return errors, classifications


def _load_inventory(path: str) -> object:
    source = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    return json.loads(source)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", help="Tables API JSON file, or - to read JSON from stdin.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    try:
        payload = _load_inventory(arguments.inventory)
    except (OSError, json.JSONDecodeError) as read_error:
        print(f"Goal 5 table inventory could not be read: {read_error}")
        return 1

    errors, classifications = validate_goal5_table_inventory(payload)
    if errors:
        print("Goal 5 table-format verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Goal 5 table-format verification passed:")
    for full_name, classification in classifications.items():
        print(f"- {full_name}: {classification}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
