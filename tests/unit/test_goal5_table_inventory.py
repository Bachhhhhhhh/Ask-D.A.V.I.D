"""Offline acceptance-policy tests for Goal 5 Tables API format evidence."""

from __future__ import annotations

from copy import deepcopy

from scripts.verify_goal5_table_inventory import (
    EXPECTED_GOAL5_TABLES,
    validate_goal5_table_inventory,
)


def _native_inventory() -> list[dict[str, object]]:
    return [
        {
            "full_name": full_name,
            "table_type": "MANAGED",
            "data_source_format": "ICEBERG",
            "properties": {
                "data_classification": "synthetic-only",
                "write.metadata.path": f"s3://approved/{full_name}/_iceberg/metadata",
            },
        }
        for full_name in sorted(EXPECTED_GOAL5_TABLES)
    ]


def _uniform_inventory() -> list[dict[str, object]]:
    inventory = _native_inventory()
    for table in inventory:
        table["data_source_format"] = "DELTA"
        table["properties"] = {
            "delta.enableIcebergCompatV2": "true",
            "delta.universalFormat.enabledFormats": "iceberg",
            "write.metadata.path": "s3://approved/table/_iceberg/metadata",
        }
    return inventory


def test_native_inventory_passes() -> None:
    errors, classifications = validate_goal5_table_inventory(_native_inventory())
    assert errors == []
    assert set(classifications.values()) == {"ICEBERG"}


def test_delta_uniform_inventory_passes_with_disclosure() -> None:
    errors, classifications = validate_goal5_table_inventory(_uniform_inventory())
    assert errors == []
    assert set(classifications.values()) == {"DELTA_UNIFORM_ICEBERG"}


def test_plain_delta_fails_closed() -> None:
    inventory = _uniform_inventory()
    inventory[0]["properties"] = {"write.metadata.path": "s3://approved/table/_iceberg/metadata"}

    errors, classifications = validate_goal5_table_inventory(inventory)

    assert any("plain DELTA" in error for error in errors)
    assert classifications[next(iter(sorted(EXPECTED_GOAL5_TABLES)))] == "PLAIN_DELTA"


def test_unmanaged_table_fails_closed() -> None:
    inventory = deepcopy(_native_inventory())
    inventory[0]["table_type"] = "EXTERNAL"

    errors, _ = validate_goal5_table_inventory(inventory)

    assert any("table_type MANAGED" in error for error in errors)


def test_missing_table_fails_closed() -> None:
    inventory = _native_inventory()
    inventory.pop()

    errors, _ = validate_goal5_table_inventory(inventory)

    assert any("inventory is missing expected tables" in error for error in errors)
