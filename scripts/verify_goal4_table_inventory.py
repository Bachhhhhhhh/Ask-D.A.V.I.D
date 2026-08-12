"""Fail-closed verification of a sanitized Goal 4 Unity Catalog table inventory."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

EXPECTED_TABLES = frozenset(
    {
        "ask_david_development.green_sm_raw.synthetic_events",
        "ask_david_development.green_sm_curated.synthetic_events",
        "ask_david_development.green_sm_curated.synthetic_entities",
        "ask_david_development.green_sm_business.synthetic_metrics",
        "ask_david_development.green_sm_ai.synthetic_document_metadata",
        "ask_david_development.green_sm_platform.synthetic_agent_execution_audit",
        "ask_david_development.green_sm_platform.synthetic_data_quality_results",
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


def validate_goal4_table_inventory(payload: object) -> list[str]:
    """Return sanitized native-Iceberg contract errors for Tables API JSON."""
    tables = _table_list(payload)
    if tables is None:
        return ["inventory must be a JSON array or an object containing a tables array"]

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

    missing = sorted(EXPECTED_TABLES.difference(indexed))
    unexpected = sorted(set(indexed).difference(EXPECTED_TABLES))
    if missing:
        errors.append("inventory is missing expected tables: " + ", ".join(missing))
    if unexpected:
        errors.append("inventory contains unexpected tables: " + ", ".join(unexpected))

    for full_name in sorted(EXPECTED_TABLES.intersection(indexed)):
        table = indexed[full_name]
        if table.get("table_type") != "MANAGED":
            errors.append(f"{full_name} must have table_type MANAGED")
        if table.get("data_source_format") != "ICEBERG":
            errors.append(f"{full_name} must have data_source_format ICEBERG")

        properties = table.get("properties")
        if not isinstance(properties, Mapping):
            errors.append(f"{full_name} must include table properties for Delta exclusion")
            continue
        delta_properties = sorted(
            str(key) for key in properties if str(key).lower().startswith("delta.")
        )
        if delta_properties:
            errors.append(f"{full_name} contains forbidden Delta table properties")
        metadata_path = properties.get("write.metadata.path")
        if not isinstance(metadata_path, str) or "/_iceberg/metadata" not in metadata_path:
            errors.append(f"{full_name} must expose a managed Iceberg metadata path")

    return errors


def _load_inventory(path: str) -> object:
    source = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    return json.loads(source)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "inventory",
        help="Tables API JSON file, or - to read JSON from standard input.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    try:
        payload = _load_inventory(arguments.inventory)
    except (OSError, json.JSONDecodeError) as read_error:
        print(f"Goal 4 table inventory could not be read: {read_error}")
        return 1

    errors = validate_goal4_table_inventory(payload)
    if errors:
        print("Goal 4 native Iceberg inventory verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Goal 4 native Iceberg inventory verification passed for exactly seven tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
