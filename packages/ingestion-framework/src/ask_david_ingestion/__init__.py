"""Reusable, credential-free ingestion contracts and synthetic adapters."""

from ask_david_ingestion.adapters import (
    CDCSourceAdapter,
    DocumentSourceAdapter,
    FileSourceAdapter,
    SourceAdapter,
)
from ask_david_ingestion.contracts import (
    CDCContract,
    Contract,
    ContractValidationError,
    DocumentContract,
    StructuredContract,
    load_contract,
)
from ask_david_ingestion.models import (
    AdapterResult,
    IngestionRun,
    Provenance,
    QuarantinedRecord,
    RunStatus,
    SourceType,
)

__all__ = [
    "AdapterResult",
    "CDCContract",
    "CDCSourceAdapter",
    "Contract",
    "ContractValidationError",
    "DocumentContract",
    "DocumentSourceAdapter",
    "FileSourceAdapter",
    "IngestionRun",
    "Provenance",
    "QuarantinedRecord",
    "RunStatus",
    "SourceAdapter",
    "SourceType",
    "StructuredContract",
    "load_contract",
]
