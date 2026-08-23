"""One deterministic synthetic offline scenario for Goal 7 acceptance."""

from __future__ import annotations

from pathlib import Path

from .agents import AnalyticsAgent, StructuredDataAgent, SupervisorAgent, UnstructuredRagAgent
from .contracts import ChunkRecord
from .embedding import CANONICAL_EMBEDDING_CONFIG, HashEmbeddingProvider
from .graph import Goal7Runtime
from .services import (
    AnalyticsService,
    InMemoryAnalyticsExecutor,
    InMemoryDorisExecutor,
    InMemoryVectorIndex,
    QueryService,
    RetrievalService,
    deterministic_chunk_id,
)


def build_offline_runtime(repository_root: Path) -> Goal7Runtime:
    rows = (
        {
            "metric_date": "2026-01-01",
            "category": "alpha",
            "event_count": 10,
            "metric_total": 100.0,
        },
        {"metric_date": "2026-01-01", "category": "beta", "event_count": 6, "metric_total": 60.0},
        {"metric_date": "2026-01-02", "category": "alpha", "event_count": 8, "metric_total": 80.0},
        {"metric_date": "2026-01-02", "category": "beta", "event_count": 7, "metric_total": 70.0},
    )
    embedding_provider = HashEmbeddingProvider(CANONICAL_EMBEDDING_CONFIG)
    index = InMemoryVectorIndex(embedding_provider)
    fixture = repository_root / "synthetic_data/goal_05/documents/neutral_technical_guide.md"
    content = fixture.read_text(encoding="utf-8").strip()
    document_id = "goal5-synthetic-document"
    chunk = ChunkRecord(
        chunk_id=deterministic_chunk_id(document_id, content, 0),
        document_id=document_id,
        title="Synthetic ingestion guide",
        content=content,
        source_uri="s3://approved-goal5-documents/neutral_technical_guide.md",
        allowed_roles=("business-reader",),
        embedding_model_id=CANONICAL_EMBEDDING_CONFIG.model_id,
        embedding=embedding_provider.embed(content),
    )
    index.upsert((chunk,))
    return Goal7Runtime(
        SupervisorAgent(),
        StructuredDataAgent(QueryService(InMemoryDorisExecutor(rows))),
        UnstructuredRagAgent(RetrievalService(index, embedding_provider)),
        AnalyticsAgent(AnalyticsService(InMemoryAnalyticsExecutor(rows))),
    )
