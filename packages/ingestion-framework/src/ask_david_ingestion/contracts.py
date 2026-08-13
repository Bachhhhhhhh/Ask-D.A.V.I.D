"""Machine-readable Goal 5 contract parsing and validation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from ask_david_ingestion.models import SourceType

SUPPORTED_SCHEMA_TYPES: Final[frozenset[str]] = frozenset(
    {"string", "timestamp", "double", "int", "boolean", "json"}
)
SUPPORTED_QUALITY_RULES: Final[frozenset[str]] = frozenset(
    {"required_fields", "unique_primary_key", "not_null", "uniqueness"}
)
APPROVED_SCHEMAS: Final[frozenset[str]] = frozenset(
    {"green_sm_raw", "green_sm_curated", "green_sm_business", "green_sm_ai", "green_sm_platform"}
)
APPROVED_TABLE_FORMAT_POLICY: Final[str] = "iceberg-or-delta-uniform-iceberg"
APPROVED_CATALOG: Final[str] = "ask_david_development"
DOCUMENT_METADATA_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "document_id",
        "document_version",
        "filename",
        "content_type",
        "source_uri",
        "source_system",
        "ingestion_run_id",
        "ingested_at",
        "classification",
    }
)
LOGICAL_SOURCE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^goal5/(structured|documents|cdc)/[A-Za-z0-9_.-]+$"
)
COMMON_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "contract_version",
        "dataset_id",
        "source_type",
        "source",
        "target_catalog",
        "target_schema",
        "target_table",
        "sensitivity_classification",
        "quality_rules",
        "table_format_policy",
    }
)


@dataclass(frozen=True, slots=True)
class QualityRule:
    """A small deterministic quality-rule declaration."""

    name: str
    columns: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BaseContract:
    """Fields common to all three source patterns."""

    contract_version: str
    dataset_id: str
    source_type: SourceType
    source: str
    target_catalog: str
    target_schema: str
    target_table: str
    sensitivity_classification: str
    quality_rules: tuple[QualityRule, ...]
    table_format_policy: str


@dataclass(frozen=True, slots=True)
class StructuredContract(BaseContract):
    """Contract for a structured CSV file."""

    schema: tuple[tuple[str, str], ...]
    primary_key: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DocumentContract(BaseContract):
    """Contract for a text/plain or text/markdown document."""

    allowed_content_types: tuple[str, ...]
    document_id_strategy: str
    metadata_required: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CDCContract(BaseContract):
    """Contract for deterministic CDC JSON Lines."""

    primary_key: tuple[str, ...]
    operation_field: str
    event_id_field: str
    event_time_field: str
    sequence_field: str


type Contract = StructuredContract | DocumentContract | CDCContract


class ContractValidationError(ValueError):
    """A stable, field-addressable contract validation failure."""

    def __init__(self, issues: tuple[tuple[str, str, str], ...]) -> None:
        self.issues = issues
        message = "; ".join(f"{code} at {path}: {detail}" for code, path, detail in issues)
        super().__init__(message)


def _issue(code: str, path: str, detail: str) -> tuple[str, str, str]:
    return code, path, detail


def _string(value: Any, path: str, issues: list[tuple[str, str, str]]) -> str:
    if not isinstance(value, str) or not value.strip():
        issues.append(_issue("REQUIRED_FIELD", path, "must be a non-blank string"))
        return ""
    return value.strip()


def _string_list(value: Any, path: str, issues: list[tuple[str, str, str]]) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        issues.append(_issue("REQUIRED_LIST", path, "must be a non-empty list"))
        return ()
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_string(item, f"{path}[{index}]", issues))
    if len(set(result)) != len(result):
        issues.append(_issue("DUPLICATE_VALUE", path, "must not contain duplicates"))
    return tuple(result)


def _quality_rules(value: Any, issues: list[tuple[str, str, str]]) -> tuple[QualityRule, ...]:
    if not isinstance(value, list) or not value:
        issues.append(_issue("REQUIRED_LIST", "quality_rules", "must be a non-empty list"))
        return ()
    rules: list[QualityRule] = []
    for index, raw_rule in enumerate(value):
        path = f"quality_rules[{index}]"
        if not isinstance(raw_rule, dict):
            issues.append(_issue("INVALID_TYPE", path, "must be an object"))
            continue
        allowed = {"name", "columns"}
        for extra in sorted(set(raw_rule) - allowed):
            issues.append(_issue("UNKNOWN_FIELD", f"{path}.{extra}", "is not supported"))
        name = _string(raw_rule.get("name"), f"{path}.name", issues)
        if name and name not in SUPPORTED_QUALITY_RULES:
            issues.append(_issue("UNSUPPORTED_RULE", f"{path}.name", name))
        columns = _string_list(raw_rule.get("columns"), f"{path}.columns", issues)
        rules.append(QualityRule(name=name, columns=columns))
    return tuple(rules)


def _common(raw: dict[str, Any], issues: list[tuple[str, str, str]]) -> BaseContract:
    contract_version = _string(raw.get("contract_version"), "contract_version", issues)
    dataset_id = _string(raw.get("dataset_id"), "dataset_id", issues)
    raw_source_type = _string(raw.get("source_type"), "source_type", issues)
    try:
        source_type = SourceType(raw_source_type)
    except ValueError:
        issues.append(_issue("UNSUPPORTED_SOURCE_TYPE", "source_type", raw_source_type))
        source_type = SourceType.STRUCTURED_FILE
    source = _string(raw.get("source"), "source", issues)
    if source and not LOGICAL_SOURCE_PATTERN.fullmatch(source):
        issues.append(_issue("UNSAFE_SOURCE", "source", "must use an approved goal5 logical key"))
    target_catalog = _string(raw.get("target_catalog"), "target_catalog", issues)
    if target_catalog != APPROVED_CATALOG:
        issues.append(_issue("UNSAFE_TARGET_CATALOG", "target_catalog", target_catalog))
    target_schema = _string(raw.get("target_schema"), "target_schema", issues)
    if target_schema and target_schema not in APPROVED_SCHEMAS:
        issues.append(_issue("UNSAFE_TARGET_SCHEMA", "target_schema", target_schema))
    target_table = _string(raw.get("target_table"), "target_table", issues)
    if target_table and not target_table.startswith("goal5_"):
        issues.append(_issue("UNSAFE_TARGET_TABLE", "target_table", target_table))
    sensitivity = _string(
        raw.get("sensitivity_classification"), "sensitivity_classification", issues
    )
    if sensitivity != "synthetic_technical":
        issues.append(_issue("UNSAFE_CLASSIFICATION", "sensitivity_classification", sensitivity))
    table_policy = _string(
        raw.get("table_format_policy", APPROVED_TABLE_FORMAT_POLICY),
        "table_format_policy",
        issues,
    )
    if table_policy != APPROVED_TABLE_FORMAT_POLICY:
        issues.append(_issue("UNSUPPORTED_TABLE_POLICY", "table_format_policy", table_policy))
    return BaseContract(
        contract_version=contract_version,
        dataset_id=dataset_id,
        source_type=source_type,
        source=source,
        target_catalog=target_catalog,
        target_schema=target_schema,
        target_table=target_table,
        sensitivity_classification=sensitivity,
        quality_rules=_quality_rules(raw.get("quality_rules"), issues),
        table_format_policy=table_policy,
    )


def _structured(
    raw: dict[str, Any], base: BaseContract, issues: list[tuple[str, str, str]]
) -> Contract:
    allowed = COMMON_FIELDS | {"schema", "primary_key"}
    for extra in sorted(set(raw) - allowed):
        issues.append(_issue("UNKNOWN_FIELD", extra, "is not supported by a structured contract"))
    raw_schema = raw.get("schema")
    fields: list[tuple[str, str]] = []
    if not isinstance(raw_schema, dict) or not raw_schema:
        issues.append(_issue("REQUIRED_OBJECT", "schema", "must be a non-empty object"))
    else:
        for name, type_name in raw_schema.items():
            field_name = _string(name, f"schema.{name}", issues)
            normalized = _string(type_name, f"schema.{name}", issues)
            if normalized and normalized not in SUPPORTED_SCHEMA_TYPES:
                issues.append(_issue("UNSUPPORTED_SCHEMA_TYPE", f"schema.{name}", normalized))
            fields.append((field_name, normalized))
    primary_key = _string_list(raw.get("primary_key"), "primary_key", issues)
    field_names = {name for name, _ in fields}
    for key in primary_key:
        if key not in field_names:
            issues.append(_issue("UNKNOWN_COLUMN", "primary_key", key))
    return StructuredContract(
        contract_version=base.contract_version,
        dataset_id=base.dataset_id,
        source_type=base.source_type,
        source=base.source,
        target_catalog=base.target_catalog,
        target_schema=base.target_schema,
        target_table=base.target_table,
        sensitivity_classification=base.sensitivity_classification,
        quality_rules=base.quality_rules,
        table_format_policy=base.table_format_policy,
        schema=tuple(fields),
        primary_key=primary_key,
    )


def _document(
    raw: dict[str, Any], base: BaseContract, issues: list[tuple[str, str, str]]
) -> Contract:
    allowed = COMMON_FIELDS | {"allowed_content_types", "document_id_strategy", "metadata_required"}
    for extra in sorted(set(raw) - allowed):
        issues.append(_issue("UNKNOWN_FIELD", extra, "is not supported by a document contract"))
    allowed_content_types = _string_list(
        raw.get("allowed_content_types"), "allowed_content_types", issues
    )
    supported = {"text/plain", "text/markdown"}
    for content_type in allowed_content_types:
        if content_type not in supported:
            issues.append(_issue("UNSUPPORTED_CONTENT_TYPE", "allowed_content_types", content_type))
    strategy = _string(raw.get("document_id_strategy"), "document_id_strategy", issues)
    if strategy != "sha256_dataset_source":
        issues.append(_issue("UNSUPPORTED_ID_STRATEGY", "document_id_strategy", strategy))
    metadata_required = _string_list(raw.get("metadata_required"), "metadata_required", issues)
    for field in metadata_required:
        if field not in DOCUMENT_METADATA_FIELDS:
            issues.append(_issue("UNSUPPORTED_METADATA_FIELD", "metadata_required", field))
    return DocumentContract(
        contract_version=base.contract_version,
        dataset_id=base.dataset_id,
        source_type=base.source_type,
        source=base.source,
        target_catalog=base.target_catalog,
        target_schema=base.target_schema,
        target_table=base.target_table,
        sensitivity_classification=base.sensitivity_classification,
        quality_rules=base.quality_rules,
        table_format_policy=base.table_format_policy,
        allowed_content_types=allowed_content_types,
        document_id_strategy=strategy,
        metadata_required=metadata_required,
    )


def _cdc(raw: dict[str, Any], base: BaseContract, issues: list[tuple[str, str, str]]) -> Contract:
    allowed = COMMON_FIELDS | {
        "primary_key",
        "operation_field",
        "event_id_field",
        "event_time_field",
        "sequence_field",
    }
    for extra in sorted(set(raw) - allowed):
        issues.append(_issue("UNKNOWN_FIELD", extra, "is not supported by a CDC contract"))
    primary_key = _string_list(raw.get("primary_key"), "primary_key", issues)
    operation_field = _string(raw.get("operation_field"), "operation_field", issues)
    event_id_field = _string(raw.get("event_id_field"), "event_id_field", issues)
    event_time_field = _string(raw.get("event_time_field"), "event_time_field", issues)
    sequence_field = _string(raw.get("sequence_field"), "sequence_field", issues)
    fields = {operation_field, event_id_field, event_time_field, sequence_field}
    fields.update(primary_key)
    if len(fields) != len(primary_key) + 4:
        issues.append(_issue("DUPLICATE_FIELD", "cdc", "CDC identity fields must be distinct"))
    return CDCContract(
        contract_version=base.contract_version,
        dataset_id=base.dataset_id,
        source_type=base.source_type,
        source=base.source,
        target_catalog=base.target_catalog,
        target_schema=base.target_schema,
        target_table=base.target_table,
        sensitivity_classification=base.sensitivity_classification,
        quality_rules=base.quality_rules,
        table_format_policy=base.table_format_policy,
        primary_key=primary_key,
        operation_field=operation_field,
        event_id_field=event_id_field,
        event_time_field=event_time_field,
        sequence_field=sequence_field,
    )


def load_contract(path: Path) -> Contract:
    """Load and fail closed on a JSON contract file."""
    issues: list[tuple[str, str, str]] = []
    try:
        raw_value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractValidationError(((_issue("INVALID_JSON", str(path), str(error))),)) from error
    if not isinstance(raw_value, dict):
        raise ContractValidationError(
            (_issue("INVALID_ROOT", "$", "contract must be a JSON object"),)
        )
    base = _common(raw_value, issues)
    if base.source_type is SourceType.STRUCTURED_FILE:
        contract = _structured(raw_value, base, issues)
    elif base.source_type is SourceType.DOCUMENT:
        contract = _document(raw_value, base, issues)
    else:
        contract = _cdc(raw_value, base, issues)
    if issues:
        raise ContractValidationError(tuple(issues))
    return contract
