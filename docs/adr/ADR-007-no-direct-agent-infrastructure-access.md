# ADR-007: Agents Must Not Directly Access Data Infrastructure

- Status: Accepted
- Decision date: Initial architecture baseline
- Owners: Platform Architecture, AI Platform, and Security teams

## Context

LLM-driven agents are probabilistic components.

Allowing agents to directly connect to data infrastructure would expose:

- Credentials.
- Unrestricted query capability.
- Authorization bypass risk.
- Prompt-injection risk.
- Weak auditability.
- Uncontrolled resource consumption.
- Accidental destructive operations.
- Tight coupling between agents and infrastructure.

The agent reasoning layer must be separated from infrastructure execution.

## Decision

Agents must not directly access data infrastructure.

Agents must not directly connect to:

- Apache Doris.
- Databricks SQL.
- Databricks jobs APIs.
- Amazon OpenSearch Serverless.
- Amazon S3.
- Unity Catalog.
- Operational databases.
- AWS administrative APIs.
- Secrets Manager.
- Infrastructure control planes.

Agent runtimes must not contain reusable data-store credentials.

Agents may request operations only through approved controlled tool services.

## Consequences

### Positive

- Smaller security boundary.
- Centralized authorization.
- Better auditability.
- Easier credential management.
- Deterministic enforcement.
- Reduced prompt-injection impact.
- Easier infrastructure replacement.

### Negative

- Additional service layer is required.
- Tool APIs must be maintained.
- Some operations may have additional latency.
- Tool schemas require versioning.

## Implementation constraints

- Agent packages must not include direct database clients for production access.
- Agent containers must not contain Doris, Databricks, OpenSearch, or S3
  credentials.
- Infrastructure connections must exist only inside approved services.
- Network policies should prevent agent runtimes from reaching data endpoints
  directly where technically possible.
- Authorization must be enforced outside the LLM.
- Every attempted direct-access violation must be logged.

## Alternatives considered

### Direct database tools inside each agent

Rejected because this distributes credentials and security logic across
probabilistic components.

### Shared database credentials in the Supervisor

Rejected because the Supervisor must not become a privileged infrastructure
gateway.

## Validation

This decision is validated when:

- Agent runtime security groups cannot directly reach protected data endpoints.
- Agent containers contain no reusable data-store credentials.
- All successful data operations can be traced to an approved tool service.
- Direct-access integration tests fail as expected.
