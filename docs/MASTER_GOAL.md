# Master Goal

## Project name

Ask D.A.V.I.D.-Inspired Data Platform for Green SM

## Purpose

Build an infrastructure-first, production-oriented AI data platform inspired by the publicly presented architecture of JPMorgan Ask D.A.V.I.D.

The platform is intended to support future data and AI use cases related to Green SM within the Vingroup ecosystem.

The current phase focuses on:

- Cloud infrastructure.
- Data platform foundations.
- Governance and security.
- Agent orchestration.
- Controlled tool interfaces.
- Observability.
- Testing and evaluation.
- Deployment automation.
- Future Green SM onboarding contracts.

Actual Green SM production data and production business logic are outside the current infrastructure phase.

Neutral synthetic datasets and synthetic documents must be used to validate all platform capabilities.

## Reference architecture

The platform must preserve the logical structure of Ask D.A.V.I.D.:

```text
User
  ↓
Supervisor Agent
  ├── Structured Data Agent
  ├── Unstructured Data / RAG Agent
  └── Analytics Agent
  ↓
Reflection
  ↓
Final Answer
```

Supporting capabilities include:

- Planning.
- Routing.
- Memory.
- Historical questions.
- Historical answers.
- Human feedback.
- Personalization.
- Reflection.
- Guardrails.
- Final response generation.
- Visualization.

These supporting capabilities are not additional specialized sub-agents.

The platform may use a different technology stack from JPMorgan. The logical multi-agent design is the reference, not JPMorgan's internal implementation technologies.

## Approved technology stack

| Capability | Approved technology |
|---|---|
| Cloud infrastructure | AWS |
| Data engineering and analytics | Databricks on AWS |
| Primary governance and metadata catalog | Unity Catalog |
| System-of-record storage | Amazon S3 |
| System-of-record table format | Apache Iceberg |
| Low-latency OLAP serving | Apache Doris |
| Vector and document retrieval | Amazon OpenSearch Serverless |
| Agent orchestration | LangGraph |
| Durable graph state | PostgreSQL |
| Short-lived cache and session state | Redis |
| Model access | Amazon Bedrock or approved external LLM through a model gateway |
| Infrastructure as code | Terraform |
| Initial application runtime | ECS Fargate |
| API framework | FastAPI |
| Observability | CloudWatch and OpenTelemetry-compatible tracing |

## Fixed architecture decisions

### Unity Catalog

Unity Catalog is the primary authority for:

- Catalogs and schemas.
- Table registration.
- Data discovery.
- Permissions.
- Ownership.
- Lineage.
- Audit integration.
- Data classification.
- Service-principal access.

AWS Glue must not become a competing primary catalog for the same governed tables.

### Amazon S3 and Apache Iceberg

Amazon S3 and Apache Iceberg form the system of record.

Authoritative structured data must remain reproducible from governed Iceberg tables stored on S3.

### Apache Doris

Apache Doris is a serving and query-acceleration layer.

Doris is not a source of truth.

Every Doris table or materialized dataset must be rebuildable from governed Iceberg data.

### OpenSearch Serverless

Amazon OpenSearch Serverless is the approved vector and document retrieval platform.

Original documents remain stored on Amazon S3.

OpenSearch contains derived retrieval assets such as:

- Document chunks.
- Embeddings.
- Searchable text.
- ACL metadata.
- Document-version metadata.
- Citation metadata.

### Agent architecture

The MVP contains exactly three specialized sub-agents:

1. Structured Data Agent.
2. Unstructured Data / RAG Agent.
3. Analytics Agent.

The following are not separate specialized sub-agents:

- Supervisor.
- Planner.
- Router.
- Reflection.
- Guardrails.
- Memory.
- Personalization.
- Human feedback.
- Final response generation.
- Visualization renderer.
- Metadata lookup.
- Data-quality validation.
- Security validation.
- Lineage lookup.
- Monitoring.

These capabilities must be implemented as graph nodes, tools, policies, middleware, controlled services, or internal subgraphs.

## Agent responsibilities

### Supervisor Agent

The Supervisor is responsible for:

- Understanding the user request.
- Loading user and session context.
- Creating an execution plan.
- Selecting one or more specialized sub-agents.
- Running agents sequentially or in parallel.
- Merging results.
- Tracking execution state.
- Routing failed results for bounded retry.
- Routing high-risk or low-confidence results to human review.
- Preparing the final response.

Planning and routing are Supervisor capabilities. They are not a fourth specialized sub-agent.

### Structured Data Agent

The Structured Data Agent is responsible for:

- Understanding requested metrics and dimensions.
- Discovering approved semantic metadata.
- Selecting Doris or Databricks SQL as the query path.
- Querying Doris for low-latency semantic marts.
- Querying Databricks SQL and Iceberg for historical, detailed, ad hoc, or non-materialized data.
- Returning structured results with query provenance.
- Never executing DDL or DML.
- Never directly accessing database credentials.

### Unstructured Data / RAG Agent

The Unstructured Data Agent is responsible for:

- Rewriting retrieval queries.
- Selecting retrieval filters.
- Applying user authorization and document ACL constraints.
- Calling the controlled Retrieval Service.
- Searching OpenSearch Serverless.
- Evaluating retrieved chunks.
- Returning evidence with citations.
- Never bypassing document access controls.

### Analytics Agent

The Analytics Agent is responsible for:

- Planning required calculations.
- Selecting approved analytical operations.
- Calling Databricks SQL or parameterized Databricks jobs.
- Validating analytical results.
- Producing narrative insights.
- Producing safe structured visualization specifications.
- Never executing arbitrary code in the agent runtime.
- Never generating executable frontend JavaScript or arbitrary HTML.

## Controlled access principle

Agents must not directly access:

- Doris credentials.
- Databricks credentials.
- OpenSearch credentials.
- S3 credentials.
- Unity Catalog credentials.
- Operational database credentials.
- AWS administrative APIs.

All access must pass through controlled services:

```text
Structured Data Agent
  → Query Service
  → Doris or Databricks SQL

Unstructured Data Agent
  → Retrieval Service
  → OpenSearch Serverless

Analytics Agent
  → Analytics Service
  → Approved Databricks SQL operation or parameterized job

All agents
  → Metadata Service
  → Unity Catalog and governed metadata
```

Every tool invocation must include:

- User identity.
- User roles.
- Conversation or thread ID.
- Graph execution ID.
- Agent identity.
- Requested operation.
- Authorization decision.
- Execution duration.
- Result status.
- Data provenance.

## Data lifecycle

Structured data follows this lifecycle:

```text
Source systems
  ↓
Raw / Bronze Iceberg
  ↓
Curated / Silver Iceberg
  ↓
Business / Gold Iceberg
  ├── Doris serving marts
  ├── Databricks analytics
  └── Agent query tools
```

Documents follow this lifecycle:

```text
Source document
  ↓
Original file on S3
  ↓
Parsing and normalization
  ↓
Chunking
  ↓
Metadata and ACL enrichment
  ↓
Embedding
  ↓
OpenSearch Serverless
  ↓
RAG retrieval with citations
```

## Infrastructure-first requirement

Before actual Green SM data is onboarded, the platform must demonstrate:

- Repeatable infrastructure provisioning.
- Environment isolation.
- Security controls.
- Governed Iceberg tables.
- Unity Catalog permissions.
- Doris rebuildability from Iceberg.
- OpenSearch ACL filtering.
- Controlled tool-service boundaries.
- Durable LangGraph execution.
- Bounded reflection and retry.
- Human review and graph resume.
- End-to-end provenance.
- Synthetic evaluation.
- Automated release gates.

## Green SM data boundary

The initial implementation must not claim to represent actual Green SM operations.

Synthetic datasets must use neutral:

- Entities.
- Metrics.
- Events.
- Transactions.
- Documents.
- Analytical scenarios.

Future Green SM onboarding must use:

- Source registration.
- Data contracts.
- Business glossary definitions.
- Metric definitions.
- Access-control mappings.
- Data-quality rules.
- Doris serving decisions.
- OpenSearch indexing decisions.
- Evaluation datasets.

Adding Green SM data must not require redesigning the core three-agent architecture.

## Final acceptance scenario

The platform is accepted when a synthetic user request requiring structured data, analytics, and document evidence completes this flow:

1. The user authenticates.
2. The request enters LangGraph.
3. The Supervisor creates a plan.
4. The Supervisor selects all three specialized sub-agents.
5. The Structured Data Agent retrieves an authorized metric from Doris or Databricks SQL.
6. The Unstructured Data Agent retrieves authorized evidence from OpenSearch Serverless.
7. The Analytics Agent runs an approved Databricks operation.
8. The results are merged.
9. Reflection validates numbers, citations, freshness, authorization, provenance, and visualization consistency.
10. Human review is requested when configured conditions require it.
11. The final response includes narrative, structured data, visualization, citations, freshness, and provenance.
12. The full execution can be reconstructed using one correlation ID.
13. No real Green SM data is required for this acceptance test.

## Success principles

The best result is not the largest number of agents.

The best result is a platform that is:

- Governed.
- Reproducible.
- Observable.
- Testable.
- Secure.
- Explainable.
- Rebuildable.
- Extensible.
- Controlled by deterministic policies.
- Ready for future Green SM onboarding.

## Related documents

- [Platform Architecture](ARCHITECTURE.md)
- [Non-Goals](NON_GOALS.md)
- [Roadmap](ROADMAP.md)
- [ADR-001: Unity Catalog](adr/ADR-001-unity-catalog.md)
- [ADR-002: Iceberg Source of Truth](adr/ADR-002-iceberg-source-of-truth.md)
- [ADR-003: Doris Serving Layer](adr/ADR-003-doris-serving-layer.md)
- [ADR-004: OpenSearch Serverless](adr/ADR-004-opensearch-serverless.md)
- [ADR-005: Three Sub-Agents](adr/ADR-005-three-sub-agents.md)
