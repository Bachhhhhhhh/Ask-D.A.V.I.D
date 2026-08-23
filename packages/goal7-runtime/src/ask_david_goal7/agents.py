"""Exactly one Supervisor and three service-bound specialized agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import AgentResult, AnalyticsRequest, MetricQueryRequest, RetrievalRequest
from .providers import SPECIALIZED_PROVIDER, SUPERVISOR_PROVIDER, ReasoningProviderConfig
from .services import AnalyticsService, QueryService, RetrievalService

STRUCTURED_AGENT_NAME = "Structured Data Agent"
RAG_AGENT_NAME = "Unstructured Data / RAG Agent"
ANALYTICS_AGENT_NAME = "Analytics Agent"
SPECIALIZED_AGENT_NAMES = (STRUCTURED_AGENT_NAME, RAG_AGENT_NAME, ANALYTICS_AGENT_NAME)


@dataclass(slots=True)
class StructuredDataAgent:
    """Natural-language interpretation around Query Service only."""

    query_service: QueryService
    provider: ReasoningProviderConfig = SPECIALIZED_PROVIDER

    def run(self, question: str, user_id: str, graph_id: str) -> AgentResult:
        response = self.query_service.query_metric(
            MetricQueryRequest("goal6-serving-metric", user_id, graph_id)
        )
        if response.status != "success":
            return AgentResult(
                STRUCTURED_AGENT_NAME,
                response.status,
                "Structured query denied.",
                error=response.error,
            )
        return AgentResult(
            STRUCTURED_AGENT_NAME,
            "success",
            f"Structured query returned {len(response.rows)} rows for the approved serving metric.",
            data={"question": question, "rows": response.rows},
            provenance=(response.provenance,),
        )


@dataclass(slots=True)
class UnstructuredRagAgent:
    """Evidence synthesis around Retrieval Service only."""

    retrieval_service: RetrievalService
    provider: ReasoningProviderConfig = SPECIALIZED_PROVIDER

    def run(self, question: str, user_id: str, graph_id: str) -> AgentResult:
        response = self.retrieval_service.retrieve(
            RetrievalRequest(
                query=question.strip(),
                top_k=3,
                allowed_roles=("business-reader",),
                user_id=user_id,
                graph_id=graph_id,
            )
        )
        if response.status != "success":
            return AgentResult(
                RAG_AGENT_NAME,
                response.status,
                "Evidence retrieval denied.",
                error=response.error,
            )
        if not response.results:
            return AgentResult(
                RAG_AGENT_NAME,
                "error",
                "No supporting evidence was found.",
                error="empty retrieval",
            )
        evidence = response.results[0]
        return AgentResult(
            RAG_AGENT_NAME,
            "success",
            f"Supporting evidence: {evidence.content}",
            data={"results": response.results},
            provenance=tuple(item.provenance for item in response.results),
        )


@dataclass(slots=True)
class AnalyticsAgent:
    """Approved calculation interpretation around Analytics Service only."""

    analytics_service: AnalyticsService
    provider: ReasoningProviderConfig = SPECIALIZED_PROVIDER

    def run(self, question: str, user_id: str, graph_id: str) -> AgentResult:
        response = self.analytics_service.compare_periods(
            AnalyticsRequest("goal6-serving-metric", user_id, graph_id)
        )
        if response.status != "success":
            return AgentResult(
                ANALYTICS_AGENT_NAME,
                response.status,
                "Analytics failed.",
                error=response.error,
            )
        return AgentResult(
            ANALYTICS_AGENT_NAME,
            "success",
            (
                f"Main contributor is {response.main_contributor} "
                f"({response.contributor_change:+.2f})."
            ),
            data={
                "latest_period": response.latest_period,
                "previous_period": response.previous_period,
                "latest_value": response.latest_value,
                "previous_value": response.previous_value,
                "difference": response.difference,
                "percentage_change": response.percentage_change,
                "main_contributor": response.main_contributor,
                "contributor_change": response.contributor_change,
            },
            provenance=(response.provenance,),
        )


@dataclass(slots=True)
class SupervisorAgent:
    """Routes work to exactly three agents and synthesizes their results."""

    provider: ReasoningProviderConfig = SUPERVISOR_PROVIDER

    def plan(self, question: str) -> tuple[str, ...]:
        if not question.strip():
            raise ValueError("question must not be empty")
        return SPECIALIZED_AGENT_NAMES

    def synthesize(
        self,
        question: str,
        structured: AgentResult,
        unstructured: AgentResult,
        analytics: AgentResult,
    ) -> str:
        if any(result.status != "success" for result in (structured, unstructured, analytics)):
            return "The integrated answer is unavailable because one controlled service failed."
        analytics_data: dict[str, Any] = analytics.data
        rows = structured.data.get("rows", [])
        evidence = unstructured.data.get("results", [])
        citation = evidence[0].source_uri if evidence else "unavailable"
        return (
            f"Question: {question}\n"
            f"Latest metric ({analytics_data['latest_period']}): {analytics_data['latest_value']}. "
            f"Previous period ({analytics_data['previous_period']}): "
            f"{analytics_data['previous_value']}. "
            f"Change: {analytics_data['difference']:+.2f} "
            f"({analytics_data['percentage_change']:+.2f}%).\n"
            f"Main contributor: {analytics_data['main_contributor']} "
            f"({analytics_data['contributor_change']:+.2f}). "
            f"Structured rows inspected: {len(rows)}.\n"
            f"Supporting evidence: {unstructured.summary} Source: {citation}."
        )
