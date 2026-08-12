"""Regression tests for the fail-closed Goal 4 live table inventory verifier."""

from copy import deepcopy

from scripts.verify_goal4_table_inventory import (
    EXPECTED_TABLES,
    validate_goal4_table_inventory,
)


def _native_iceberg_inventory() -> list[dict[str, object]]:
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
        for full_name in sorted(EXPECTED_TABLES)
    ]


def test_native_iceberg_inventory_passes() -> None:
    assert validate_goal4_table_inventory(_native_iceberg_inventory()) == []


def test_delta_uniform_inventory_fails_closed() -> None:
    inventory = _native_iceberg_inventory()
    inventory[0]["data_source_format"] = "DELTA"
    inventory[0]["properties"] = {
        "delta.enableIcebergCompatV2": "true",
        "delta.universalFormat.enabledFormats": "iceberg",
        "write.metadata.path": "s3://approved/table/_iceberg/metadata",
    }

    errors = validate_goal4_table_inventory(inventory)

    assert any("must have data_source_format ICEBERG" in error for error in errors)
    assert any("contains forbidden Delta table properties" in error for error in errors)


def test_missing_table_fails_closed() -> None:
    inventory = _native_iceberg_inventory()
    inventory.pop()

    errors = validate_goal4_table_inventory(inventory)

    assert any("inventory is missing expected tables" in error for error in errors)


def test_unmanaged_table_fails_closed() -> None:
    inventory = deepcopy(_native_iceberg_inventory())
    inventory[0]["table_type"] = "EXTERNAL"

    errors = validate_goal4_table_inventory(inventory)

    assert any("must have table_type MANAGED" in error for error in errors)


def test_missing_properties_cannot_prove_delta_exclusion() -> None:
    inventory = _native_iceberg_inventory()
    inventory[0].pop("properties")

    errors = validate_goal4_table_inventory(inventory)

    assert any("must include table properties for Delta exclusion" in error for error in errors)
