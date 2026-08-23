"""Minimal LangGraph assembly with a deterministic offline fallback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict

from .agents import AnalyticsAgent, StructuredDataAgent, SupervisorAgent, UnstructuredRagAgent
from .contracts import AgentResult, DemoResponse


class GraphState(TypedDict, total=False):
    question: str
    user_id: str
    graph_id: str
    route: tuple[str, ...]
    structured: AgentResult
    unstructured: AgentResult
    analytics: AgentResult
    answer: str


@dataclass(slots=True)
class Goal7Runtime:
    supervisor: SupervisorAgent
    structured_agent: StructuredDataAgent
    rag_agent: UnstructuredRagAgent
    analytics_agent: AnalyticsAgent

    def run_offline(self, question: str, user_id: str = "synthetic-user") -> DemoResponse:
        graph_id = "goal7-offline-demo"
        route = self.supervisor.plan(question)
        structured = self.structured_agent.run(question, user_id, graph_id)
        unstructured = self.rag_agent.run(question, user_id, graph_id)
        analytics = self.analytics_agent.run(question, user_id, graph_id)
        answer = self.supervisor.synthesize(question, structured, unstructured, analytics)
        return DemoResponse(
            question,
            answer,
            route,
            structured,
            unstructured,
            analytics,
        )

    def build_langgraph(self) -> Any:
        """Build the approved graph when the optional LangGraph dependency exists."""

        try:
            from langgraph.graph import END, START, StateGraph  # type: ignore[import-not-found]
        except ImportError as error:  # pragma: no cover - depends on optional runtime extra
            raise RuntimeError(
                "Goal 7 connected runtime requires the deployment environment to install "
                "LangGraph and opensearch-py; the offline contract runner remains dependency-free."
            ) from error

        graph = StateGraph(GraphState)

        def route(state: GraphState) -> GraphState:
            return {"route": self.supervisor.plan(state["question"])}

        def structured(state: GraphState) -> GraphState:
            return {
                "structured": self.structured_agent.run(
                    state["question"], state["user_id"], state["graph_id"]
                )
            }

        def unstructured(state: GraphState) -> GraphState:
            return {
                "unstructured": self.rag_agent.run(
                    state["question"], state["user_id"], state["graph_id"]
                )
            }

        def analytics(state: GraphState) -> GraphState:
            return {
                "analytics": self.analytics_agent.run(
                    state["question"], state["user_id"], state["graph_id"]
                )
            }

        def synthesize(state: GraphState) -> GraphState:
            return {
                "answer": self.supervisor.synthesize(
                    state["question"],
                    state["structured"],
                    state["unstructured"],
                    state["analytics"],
                )
            }

        graph.add_node("supervisor", route)
        graph.add_node("structured_data_agent", structured)
        graph.add_node("unstructured_rag_agent", unstructured)
        graph.add_node("analytics_agent", analytics)
        graph.add_node("supervisor_synthesis", synthesize)
        graph.add_edge(START, "supervisor")
        graph.add_edge("supervisor", "structured_data_agent")
        graph.add_edge("structured_data_agent", "unstructured_rag_agent")
        graph.add_edge("unstructured_rag_agent", "analytics_agent")
        graph.add_edge("analytics_agent", "supervisor_synthesis")
        graph.add_edge("supervisor_synthesis", END)
        return graph.compile()
