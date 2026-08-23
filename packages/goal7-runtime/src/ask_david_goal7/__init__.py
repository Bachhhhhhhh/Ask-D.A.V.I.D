"""Minimal, controlled Goal 7 retrieval and agent demo runtime."""

from .contracts import (
    AgentResult,
    AnalyticsRequest,
    AnalyticsResponse,
    ChunkRecord,
    DemoResponse,
    MetricQueryRequest,
    MetricQueryResponse,
    RetrievalRequest,
    RetrievalResponse,
    RetrievedChunk,
)
from .embedding import CANONICAL_EMBEDDING_CONFIG, EmbeddingConfig, HashEmbeddingProvider
from .services import (
    APPROVED_ANALYTICS_METRIC,
    AnalyticsService,
    IndexingService,
    InMemoryAnalyticsExecutor,
    InMemoryDorisExecutor,
    InMemoryVectorIndex,
    MetadataService,
    OpenSearchVectorIndex,
    QueryService,
    RetrievalService,
)

__all__ = [
    "AgentResult",
    "AnalyticsRequest",
    "AnalyticsResponse",
    "AnalyticsService",
    "APPROVED_ANALYTICS_METRIC",
    "CANONICAL_EMBEDDING_CONFIG",
    "ChunkRecord",
    "DemoResponse",
    "EmbeddingConfig",
    "HashEmbeddingProvider",
    "InMemoryAnalyticsExecutor",
    "InMemoryDorisExecutor",
    "InMemoryVectorIndex",
    "IndexingService",
    "MetadataService",
    "OpenSearchVectorIndex",
    "MetricQueryRequest",
    "MetricQueryResponse",
    "QueryService",
    "RetrievedChunk",
    "RetrievalRequest",
    "RetrievalResponse",
    "RetrievalService",
]
