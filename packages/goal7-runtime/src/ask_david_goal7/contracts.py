"""Small typed contracts shared by controlled services and agents.

The contracts deliberately contain no credentials, SDK clients, or arbitrary
query/code fields.  Data-store adapters are injected behind protocols in
``services.py`` so agent code cannot bypass the controlled-service boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ServiceStatus = Literal["success", "denied", "error"]


@dataclass(frozen=True, slots=True)
class Provenance:
    """Source information that must travel with every service result."""

    source_system: str
    source_reference: str
    query_id: str
    freshness: str | None = None


@dataclass(frozen=True, slots=True)
class ChunkRecord:
    """Canonical OpenSearch document payload for one deterministic chunk."""

    chunk_id: str
    document_id: str
    title: str
    content: str
    source_uri: str
    allowed_roles: tuple[str, ...]
    embedding_model_id: str
    embedding: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class MetricQueryRequest:
    metric_name: str
    user_id: str
    graph_id: str
    max_rows: int = 20
    table_name: str = "ask_david_serving_development.serving_metric_daily"


@dataclass(frozen=True, slots=True)
class MetricQueryResponse:
    status: ServiceStatus
    columns: tuple[str, ...]
    rows: tuple[dict[str, Any], ...]
    provenance: Provenance
    sql: str
    error: str | None = None


@dataclass(frozen=True, slots=True)
class RetrievalRequest:
    query: str
    top_k: int
    allowed_roles: tuple[str, ...]
    user_id: str
    graph_id: str


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    title: str
    content: str
    source_uri: str
    score: float
    provenance: Provenance


@dataclass(frozen=True, slots=True)
class RetrievalResponse:
    status: ServiceStatus
    query: str
    results: tuple[RetrievedChunk, ...]
    provenance: Provenance
    error: str | None = None


@dataclass(frozen=True, slots=True)
class AnalyticsRequest:
    metric_name: str
    user_id: str
    graph_id: str


@dataclass(frozen=True, slots=True)
class AnalyticsResponse:
    status: ServiceStatus
    latest_period: str | None
    previous_period: str | None
    latest_value: float | None
    previous_value: float | None
    difference: float | None
    percentage_change: float | None
    main_contributor: str | None
    contributor_change: float | None
    provenance: Provenance
    error: str | None = None


@dataclass(frozen=True, slots=True)
class AgentResult:
    agent_name: str
    status: ServiceStatus
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    provenance: tuple[Provenance, ...] = ()
    error: str | None = None


@dataclass(frozen=True, slots=True)
class DemoResponse:
    question: str
    answer: str
    agents_used: tuple[str, ...]
    structured: AgentResult
    unstructured: AgentResult
    analytics: AgentResult
