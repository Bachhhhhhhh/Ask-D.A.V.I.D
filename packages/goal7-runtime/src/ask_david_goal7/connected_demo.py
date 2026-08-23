"""One-shot connected Goal 7 Supervisor demo entry point."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any

from .agents import AnalyticsAgent, StructuredDataAgent, SupervisorAgent, UnstructuredRagAgent
from .connected import (
    AossVectorIndexAdapter,
    DatabricksAnalyticsExecutor,
    DatabricksEmbeddingProvider,
    DorisCliExecutor,
)
from .embedding import CANONICAL_EMBEDDING_CONFIG
from .contracts import AgentResult
from .graph import Goal7Runtime
from .indexer import AossClient, DatabricksSqlClient
from .services import AnalyticsService, QueryService, RetrievalService

_QUESTION = (
    "Compare the latest synthetic metric with the previous period, explain the "
    "main contributor, and provide supporting document evidence."
)

_AGENT_KEYS = ("structured", "unstructured", "analytics")


def _error_category(error: str | None) -> str | None:
    """Return a bounded diagnostic label without copying runtime error text.

    Connected service errors can contain provider-generated details.  The
    integrated task must identify the failing agent without putting endpoints,
    SQL, credentials, document content, or response bodies in CloudWatch.
    Only stable, repository-owned fragments are mapped to labels; everything
    else is deliberately collapsed to ``unclassified_error``.
    """

    if not error:
        return None
    normalized = " ".join(error.split()).lower()
    labels = (
        ("empty retrieval", "empty_retrieval"),
        ("approved analytics source returned no rows", "analytics_no_rows"),
        ("at least two periods are required", "analytics_insufficient_periods"),
        ("metric is not in the approved analytics allowlist", "analytics_metric_denied"),
        ("table is not in the approved doris allowlist", "structured_table_denied"),
        ("metric is not in the approved doris allowlist", "structured_metric_denied"),
        ("connected doris read-only query failed", "doris_query_failed"),
        ("aoss", "aoss_error"),
        ("databricks", "databricks_error"),
    )
    for fragment, label in labels:
        if fragment in normalized:
            return label
    return "unclassified_error"


def _build_agent_diagnostics(state: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Build a secret-safe status summary for a failed connected graph.

    The summary contains only fixed agent keys, a status, an error-presence
    bit, and a bounded category.  It intentionally excludes ``AgentResult``
    summaries, data, provenance, and raw error strings.
    """

    diagnostics: dict[str, dict[str, Any]] = {}
    for key in _AGENT_KEYS:
        result = state.get(key)
        if not isinstance(result, AgentResult):
            diagnostics[key] = {
                "status": "missing",
                "error_present": False,
                "error_category": "missing_result",
            }
            continue
        diagnostics[key] = {
            "status": result.status,
            "error_present": bool(result.error),
            "error_category": _error_category(result.error),
        }
    return diagnostics


def _emit_agent_diagnostics(state: Mapping[str, Any]) -> None:
    """Emit one bounded JSON marker before the aggregate failure."""

    print(
        json.dumps(
            {
                "goal": "goal-07",
                "status": "integrated-demo-agent-diagnostics",
                "agents": _build_agent_diagnostics(state),
            },
            sort_keys=True,
        ),
        flush=True,
    )


def main() -> int:
    sql_client = DatabricksSqlClient.from_environment()
    aoss_client = AossClient(os.environ["GOAL7_AOSS_ENDPOINT"], os.environ["AWS_REGION"])
    provider = DatabricksEmbeddingProvider(sql_client)
    runtime = Goal7Runtime(
        SupervisorAgent(),
        StructuredDataAgent(QueryService(DorisCliExecutor.from_environment())),
        UnstructuredRagAgent(
            RetrievalService(
                AossVectorIndexAdapter(aoss_client, os.environ["GOAL7_INDEX_NAME"]),
                provider,
            )
        ),
        AnalyticsAgent(
            AnalyticsService(DatabricksAnalyticsExecutor(sql_client, os.environ["GOAL7_CATALOG"]))
        ),
    )
    graph = runtime.build_langgraph()
    state = graph.invoke(
        {
            "question": _QUESTION,
            "user_id": "goal7-connected-synthetic-user",
            "graph_id": "goal7-connected-demo",
        }
    )
    result = {
        "goal": "goal-07",
        "status": "integrated-demo-completed",
        "question": _QUESTION,
        "answer": state.get("answer"),
        "agent_statuses": {
            key: getattr(state.get(key), "status", None)
            for key in _AGENT_KEYS
        },
        "embedding_model_id": CANONICAL_EMBEDDING_CONFIG.model_id,
        "embedding_dimension": CANONICAL_EMBEDDING_CONFIG.dimension,
    }
    if not result["answer"] or any(
        status != "success" for status in result["agent_statuses"].values()
    ):
        _emit_agent_diagnostics(state)
        raise RuntimeError("connected Goal 7 integrated demo did not complete all agents")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
