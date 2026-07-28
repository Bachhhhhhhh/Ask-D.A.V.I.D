# ADR-008: Controlled Tool Services as the Only Agent Data Access Path

- Status: Accepted
- Decision date: Initial architecture baseline
- Owners: Platform Architecture, AI Platform, Data Platform, and Security teams

## Context

Agents require access to structured data, documents, metadata, and analytical
operations.

These operations require deterministic authorization, policy enforcement,
resource limits, typed interfaces, and complete provenance.

Embedding this logic directly inside prompts or individual agents would create
inconsistent and difficult-to-audit behavior.

## Decision

All agent data access must pass through controlled tool services.

The approved services are:

### Query Service

Provides controlled access to:

- Apache Doris.
- Databricks SQL.
- Approved Iceberg semantic datasets.

Enforces:

- Read-only SQL.
- SQL parsing.
- Table allowlists.
- Column restrictions.
- Mandatory row limits.
- Query timeouts.
- Resource limits.
- User authorization.
- Query provenance.

### Retrieval Service

Provides controlled access to:

- Amazon OpenSearch Serverless.

Enforces:

- Document ACLs.
- Metadata filtering.
- Index allowlists.
- Result limits.
- Citation metadata.
- Document-version rules.
- Retrieval audit.

### Analytics Service

Provides controlled access to:

- Approved Databricks SQL operations.
- Parameterized Databricks jobs.

Enforces:

- Operation allowlists.
- Parameter schemas.
- Runtime limits.
- Resource limits.
- Result-size limits.
- Execution provenance.
- Safe chart schemas.

### Metadata Service

Provides controlled access to:

- Unity Catalog metadata.
- Metric definitions.
- Dataset descriptions.
- Sensitivity classifications.
- Freshness.
- Ownership.
- Lineage references.
- Approved query paths.

## Required request context

Every tool request must include:

- User identity.
- User roles or groups.
- Conversation or thread ID.
- Graph execution ID.
- Calling agent.
- Requested operation.
- Request timestamp.
- Correlation ID.

Every tool response must include:

- Authorization result.
- Execution status.
- Data provenance.
- Source identifiers.
- Freshness metadata.
- Execution duration.
- Typed errors where applicable.

## Consequences

### Positive

- Consistent security enforcement.
- Centralized observability.
- Stable agent interfaces.
- Infrastructure abstraction.
- Easier testing.
- Easier policy updates.
- Complete provenance.

### Negative

- Additional services must be operated.
- Service schemas must be versioned.
- Availability of tool services becomes important.
- Additional network hops may increase latency.

## Implementation constraints

- Tool APIs must use typed, versioned request and response schemas.
- Tools must reject missing identity context.
- Tools must enforce authorization independently of agent instructions.
- Raw infrastructure errors must not be returned directly to agents.
- Tool operations must be idempotent where appropriate.
- Every tool call must be auditable.
- Agents must not bypass the services.

## Alternatives considered

### Direct SDK access from agents

Rejected because it bypasses deterministic policy and central auditing.

### One generic unrestricted execution service

Rejected because different data paths require distinct policies and security
controls.

## Validation

This decision is validated when:

- All agent integration tests use controlled service APIs.
- DDL and DML are rejected before reaching a database.
- Unauthorized retrieval returns zero protected chunks.
- Every result contains provenance and correlation identifiers.
- No approved agent workflow requires direct infrastructure credentials.
