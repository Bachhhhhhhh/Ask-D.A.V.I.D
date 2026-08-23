# Goal 7 LangGraph agent runtime

The minimal runtime has exactly four reasoning components: one Supervisor and
the three accepted specialized agents (Structured Data, Unstructured Data /
RAG, and Analytics). Each specialized agent is service-bound and cannot reach
Doris, Databricks, OpenSearch, S3, Unity Catalog, or AWS directly.

Separate concise prompts are under `agents/prompts/`. `ask-david-goal7` builds
the LangGraph when the deployment environment supplies LangGraph and provides
a deterministic offline runner for contract tests. No arbitrary generated code,
DDL/DML, reflection, memory, or extra agent is implemented.
