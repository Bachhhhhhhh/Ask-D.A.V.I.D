# Platform Architecture

## 1. Overview

This document defines the target architecture for an Ask D.A.V.I.D.-inspired Data Platform on AWS.

The architecture adopts the logical multi-agent structure publicly presented for Ask D.A.V.I.D. while using:

- AWS.
- Databricks on AWS.
- Unity Catalog.
- Amazon S3.
- Apache Iceberg.
- Apache Doris.
- Amazon OpenSearch Serverless.
- LangGraph.

The platform is infrastructure-first.

Actual Green SM data is deferred until the platform passes synthetic end-to-end validation.

## 2. Architecture principles

1. Unity Catalog is the primary catalog and governance authority.
2. Amazon S3 and Apache Iceberg are the system of record.
3. Apache Doris is a rebuildable serving layer.
4. OpenSearch Serverless is the vector retrieval layer.
5. LangGraph orchestrates one Supervisor and exactly three specialized sub-agents.
6. Agents use controlled services instead of direct infrastructure access.
7. Deterministic policies override LLM instructions.
8. Security and authorization are enforced independently of prompts.
9. Every answer must be traceable to its queries, jobs, datasets, and documents.
10. The platform must support future Green SM onboarding without redesigning the core architecture.

## 3. High-level architecture

```text
┌────────────────────────────────────────────────────────────────────┐
│                         Experience Layer                           │
│                                                                    │
│  Web UI        REST API        Slack/Teams        Review Console   │
└───────────────────────────────┬────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                    Authentication and API Layer                    │
│                                                                    │
│  API Gateway / ALB   Identity Provider   IAM   Request Context     │
└───────────────────────────────┬────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                   LangGraph Agent Runtime                          │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Supervisor Agent                                             │  │
│  │ Planning · Routing · Parallel Execution · Result Merging     │  │
│  └───────────────┬────────────────┬────────────────┬────────────┘  │
│                  │                │                │               │
│                  ▼                ▼                ▼               │
│       Structured Data      Unstructured Data     Analytics         │
│           Agent               / RAG Agent          Agent           │
│                  │                │                │               │
│                  └────────────────┴────────────────┘               │
│                                  │                                 │
│                     Reflection and Guardrails                      │
│                                  │                                 │
│                     Human Feedback if Required                     │
│                                  │                                 │
│                       Final Response Generation                    │
└─────────────┬────────────────────┬───────────────────┬─────────────┘
              │                    │                   │
              ▼                    ▼                   ▼
      Query Service       Retrieval Service    Analytics Service
              │                    │                   │
       ┌──────┴──────┐             │             Databricks SQL
       │             │             │             or approved jobs
       ▼             ▼             ▼                   │
    Doris       Databricks SQL  OpenSearch             │
                  / Iceberg     Serverless             │
       │             │             │                   │
       └──────┬──────┘             │                   │
              ▼                    │                   │
       S3 + Apache Iceberg         │                   │
              ▲                    │                   │
              │                    │                   │
       Databricks pipelines ───────┴───────────────────┘
              │
       Unity Catalog governance
```

## 4. Experience layer

The experience layer provides:

- Web-based chat.
- REST API.
- Optional Slack or Teams integration.
- Human-review console.
- Conversation history.
- Structured table rendering.
- Visualization rendering.
- Citation display.
- Provenance display.
- Execution-status streaming.

The experience layer must not execute agent-generated code.

Only allowlisted visualization types may be rendered.

## 5. Authentication and access layer

The access layer is responsible for:

- User authentication.
- User-role resolution.
- Group membership.
- Request identity.
- Session context.
- Authorization-context propagation.
- Correlation-ID creation.

Every graph execution and tool invocation must carry user identity and roles.

## 6. LangGraph orchestration layer

LangGraph is responsible for:

- Stateful execution.
- Supervisor planning and routing.
- Specialized sub-agent invocation.
- Parallel and sequential execution.
- Bounded retries.
- Reflection.
- Human interruption.
- Durable resume.
- Conversation state.
- Execution tracing.

PostgreSQL is the durable checkpoint store.

Redis is used for:

- Short-lived caching.
- Temporary tool results.
- Session acceleration.
- Rate-limiting state.

Redis must not be the only durable state store.

## 7. Ask D.A.V.I.D.-style graph

```text
START
  ↓
Load authenticated user context
  ↓
Load conversation and historical context
  ↓
Supervisor
  ├── Select Structured Data Agent
  ├── Select Unstructured Data Agent
  ├── Select Analytics Agent
  └── Select any valid combination of the three
  ↓
Execute selected agents
  ↓
Merge evidence and results
  ↓
Personalize response presentation
  ↓
Reflection
  ├── Pass
  ├── Retry selected agent
  └── Request human feedback
  ↓
Generate final response
  ↓
Update durable memory and audit
  ↓
END
```

The Supervisor may call zero, one, two, or all three specialized sub-agents.

It must not create additional specialized agents dynamically.

## 8. Specialized sub-agents

### 8.1 Structured Data Agent

The Structured Data Agent handles governed tabular data.

```text
User question
  ↓
Metric and dimension interpretation
  ↓
Metadata lookup
  ↓
Query-path selection
  ├── Doris
  └── Databricks SQL / Iceberg
  ↓
Query proposal
  ↓
Deterministic validation
  ↓
Authorization
  ↓
Execution
  ↓
Result validation
  ↓
Return result and provenance
```

Use Doris when:

- An approved semantic mart exists.
- Low latency is required.
- The query pattern is common.
- The data is fresh enough.
- The required metric is materialized.

Use Databricks SQL and Iceberg when:

- Full historical detail is required.
- The query is ad hoc.
- The dataset is not materialized in Doris.
- Large-scale processing is required.
- Iceberg snapshots or historical versions are required.

The Structured Data Agent cannot execute:

- `INSERT`
- `UPDATE`
- `DELETE`
- `MERGE`
- `DROP`
- `ALTER`
- `CREATE`
- `GRANT`
- `REVOKE`
- Administrative statements

### 8.2 Unstructured Data / RAG Agent

The Unstructured Data Agent handles documents and textual evidence.

```text
User question
  ↓
Query rewrite
  ↓
Metadata-filter selection
  ↓
User ACL filter
  ↓
Hybrid retrieval
  ↓
Optional reranking
  ↓
Evidence evaluation
  ↓
Citation package
```

Every evidence item must include:

- Document ID.
- Document version.
- Title.
- Source system.
- Page or section.
- Effective date.
- Retrieval score.
- Authorization decision.
- Source URI or document reference.

Unauthorized chunks must be removed before results reach the agent.

### 8.3 Analytics Agent

The Analytics Agent handles:

- Calculations.
- Comparative analysis.
- Statistical operations.
- Approved analytical models.
- Visualization specifications.

```text
User analytical request
  ↓
Calculation planning
  ↓
Approved operation selection
  ├── Databricks SQL
  └── Parameterized Databricks job
  ↓
Execution through Analytics Service
  ↓
Result validation
  ↓
Insight generation
  ↓
Visualization specification
```

The Analytics Agent must not:

- Execute arbitrary shell commands.
- Execute arbitrary Python inside the agent container.
- Submit unrestricted notebooks.
- Generate executable JavaScript.
- Access production credentials.
- Modify authoritative data.

## 9. Controlled tool-service boundary

### 9.1 Query Service

The Query Service provides controlled access to Doris and Databricks SQL.

It must enforce:

- Read-only SQL.
- SQL parsing.
- Table allowlists.
- Column restrictions.
- Row limits.
- Timeouts.
- Resource limits.
- User authorization.
- Audit logging.
- Query provenance.
- Typed errors.

### 9.2 Retrieval Service

The Retrieval Service provides controlled access to OpenSearch Serverless.

It must enforce:

- User ACLs.
- Metadata filters.
- Index allowlists.
- Result limits.
- Citation metadata.
- Retrieval audit.
- Document-version handling.

### 9.3 Analytics Service

The Analytics Service provides controlled access to approved analytical operations.

It must enforce:

- Operation allowlists.
- Parameter schemas.
- Resource limits.
- Timeouts.
- Result-size limits.
- User authorization.
- Execution provenance.
- Safe visualization schemas.

### 9.4 Metadata Service

The Metadata Service exposes governed metadata from Unity Catalog and platform metadata stores.

It should provide:

- Catalogs and schemas.
- Approved tables and views.
- Column descriptions.
- Metric definitions.
- Dimensions.
- Sensitivity classifications.
- Freshness.
- Owners.
- Lineage references.
- Allowed query paths.

## 10. Data architecture

### 10.1 System of record

Amazon S3 stores:

- Iceberg data files.
- Iceberg metadata files.
- Original documents.
- Pipeline artifacts.
- Audit exports.
- Generated analytical artifacts where required.

Apache Iceberg provides:

- Table schemas.
- Partition metadata.
- Snapshots.
- Atomic table operations.
- Schema evolution.
- Time travel.
- Engine interoperability.

### 10.2 Medallion architecture

```text
Raw / Bronze
  - Source-faithful records
  - Minimal transformation
  - Source metadata
  - Ingestion metadata

Curated / Silver
  - Validated schemas
  - Deduplication
  - Standardization
  - Conformed identifiers
  - Quality checks

Business / Gold
  - Governed business entities
  - Approved metrics
  - Semantic views
  - Agent-consumable datasets
```

Agents should query Gold tables or approved semantic views by default.

Direct agent access to Raw and Curated layers is prohibited unless explicitly approved for a controlled diagnostic workflow.

## 11. Unity Catalog

Unity Catalog is responsible for:

- Catalog hierarchy.
- Schema ownership.
- Table permissions.
- View permissions.
- Data discovery.
- Classification.
- Lineage.
- Audit integration.
- Service-principal access.
- Environment separation.

Unity Catalog is the primary metadata authority.

AWS Glue must not independently own or mutate metadata for the same governed tables.

## 12. Apache Doris

Doris provides:

- Low-latency analytical queries.
- Semantic marts.
- Frequently requested aggregates.
- High-concurrency analytical access.
- Query acceleration.

Doris data originates from Iceberg:

```text
Iceberg Gold
  ↓
Controlled refresh or ingestion
  ↓
Doris serving tables
```

Doris must be rebuildable:

```text
Delete Doris serving table
  ↓
Run approved rebuild process
  ↓
Restore from Iceberg Gold
  ↓
Validate counts and checksums
```

No authoritative workflow may depend on Doris as the only data copy.

## 13. OpenSearch Serverless

OpenSearch Serverless stores:

- Document chunks.
- Embeddings.
- Searchable text.
- Citation metadata.
- Document versions.
- ACL metadata.
- Source metadata.

Original documents remain stored on S3.

The OpenSearch index is derived data and must be rebuildable.

## 14. Document pipeline

```text
Document source
  ↓
Original object stored on S3
  ↓
File and security validation
  ↓
Text extraction
  ↓
Normalization
  ↓
Chunking
  ↓
Metadata enrichment
  ↓
ACL enrichment
  ↓
Embedding generation
  ↓
OpenSearch Serverless indexing
```

Document updates must:

- Create a new version.
- Replace or deactivate previous chunks.
- Preserve required document history.
- Prevent stale versions from being returned unintentionally.

## 15. Memory architecture

### Durable memory

PostgreSQL stores:

- LangGraph checkpoints.
- Conversation-thread state.
- Historical questions.
- Historical answers.
- Human-review decisions.
- Execution metadata.
- Feedback.
- Selected entities and context where permitted.

### Short-lived memory

Redis stores:

- Session acceleration.
- Temporary tool results.
- Response caching.
- Rate-limit state.
- Ephemeral conversation context.

Redis loss must not destroy durable graph state.

## 16. Reflection architecture

Reflection uses deterministic checks first.

Deterministic checks include:

- Numeric consistency.
- Citation existence.
- Query provenance.
- Data freshness.
- Authorization status.
- Visualization-data consistency.
- Required result fields.
- Unsupported-action detection.

LLM-based semantic review may check:

- Whether the answer addresses the question.
- Whether narrative claims are supported.
- Whether the response suits the user role.
- Whether sources appear contradictory.

Reflection must use bounded retries.

The default maximum retry count is two.

## 17. Human feedback

Human review may be triggered by:

- Low confidence.
- Conflicting evidence.
- Missing required citations.
- Sensitive data.
- Expensive analytical execution.
- Policy uncertainty.
- Future write operations.
- Explicit user request.

Supported decisions:

- Approve.
- Edit.
- Reject.
- Request additional evidence.

The exact graph state must be resumable after a human decision.

## 18. Visualization architecture

Visualization is a capability of the Analytics Agent and presentation layer.

It is not a separate specialized agent.

Example visualization schema:

```json
{
  "chart_type": "line",
  "title": "Synthetic metric by period",
  "x_field": "period",
  "series": [
    {
      "name": "Metric",
      "field": "metric_value",
      "unit": "count"
    }
  ],
  "data": [],
  "source_result_ids": []
}
```

Allowlisted visualization types:

- Table.
- KPI card.
- Line chart.
- Bar chart.
- Pie chart when part-to-whole semantics are valid.
- Scatter chart.

Users must be able to inspect the structured data behind each chart.

## 19. Security model

Security controls include:

- Least-privilege IAM.
- Private networking.
- KMS encryption.
- Secrets Manager.
- Service-to-service authentication.
- User-identity propagation.
- Unity Catalog permissions.
- Doris read-only service users.
- OpenSearch ACL filtering.
- SQL policy enforcement.
- Prompt-injection defenses.
- PII-safe logging.
- Audit trails.

LLM output must never be treated as an authorization decision.

## 20. Observability

A single correlation ID must link:

```text
API request
  ↓
LangGraph execution
  ↓
Supervisor decision
  ↓
Sub-agent calls
  ↓
Tool-service calls
  ↓
SQL queries
  ↓
OpenSearch retrieval
  ↓
Databricks jobs
  ↓
Reflection
  ↓
Human feedback
  ↓
Final response
```

Required measurements include:

- End-to-end latency.
- Node latency.
- Tool latency.
- Token consumption.
- Query duration.
- Retrieval duration.
- Job duration.
- Error rate.
- Retry rate.
- Human-escalation rate.
- Data freshness.
- Doris refresh lag.
- Cost by environment and service.

## 21. Environment model

At minimum, support:

- Development.
- Staging.
- Production.

Each environment must isolate:

- AWS resources.
- Databricks configuration.
- Unity Catalog namespaces or catalogs.
- Doris schemas or clusters.
- OpenSearch collections or indexes.
- Secrets.
- Graph state.
- Audit data.

Synthetic data is used for initial development and staging validation.

## 22. Target end-to-end request

```text
User:
Compare the latest synthetic metric with the previous period,
identify the main contributor, and provide supporting document evidence.

Supervisor:
Select Structured Data Agent, Analytics Agent,
and Unstructured Data Agent.

Structured Data Agent:
Retrieve metric data through Query Service.

Analytics Agent:
Run an approved comparison and generate a visualization specification.

Unstructured Data Agent:
Retrieve authorized evidence and citations through Retrieval Service.

Supervisor:
Merge results.

Reflection:
Validate values, sources, authorization, freshness, and chart consistency.

Final response:
Return narrative, table, chart, citations, freshness, and provenance.
```

## Related documents

- [Master Goal](MASTER_GOAL.md)
- [Non-Goals](NON_GOALS.md)
- [Roadmap](ROADMAP.md)
