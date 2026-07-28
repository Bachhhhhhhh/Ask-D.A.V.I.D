# ADR-009: Generated Code Must Not Execute Inside the Agent Runtime

- Status: Accepted
- Decision date: Initial architecture baseline
- Owners: Platform Architecture, AI Platform, and Security teams

## Context

The Analytics Agent may need calculations that are more complex than a single
retrieval or query.

Allowing LLM-generated code to execute directly inside the agent runtime would
create risks including:

- Arbitrary code execution.
- Data exfiltration.
- Secret exposure.
- Host compromise.
- Unbounded resource usage.
- Uncontrolled network access.
- Non-reproducible analytics.
- Weak auditability.

The reasoning environment must remain isolated from the analytical execution
environment.

## Decision

LLM-generated or user-provided code must not execute inside the agent runtime.

The Analytics Agent may only request:

- Approved Databricks SQL operations.
- Parameterized Databricks jobs.
- Versioned analytical templates.
- Allowlisted calculation functions.
- Safe visualization specifications.

Any future code-generation capability must execute in a separately isolated,
restricted, auditable environment and requires a new ADR.

## Consequences

### Positive

- Reduced remote-code-execution risk.
- Smaller agent-runtime attack surface.
- Reproducible analytics.
- Better resource control.
- Easier audit and approval.
- Clear separation between reasoning and execution.

### Negative

- Reduced flexibility for novel calculations.
- Approved templates must be created.
- Some analytics requests may require human escalation.
- Additional analytical-service development is required.

## Implementation constraints

The agent runtime must not expose:

- Python execution.
- Shell execution.
- Notebook execution.
- Dynamic package installation.
- Arbitrary SQL scripts.
- Arbitrary network calls.
- User-provided executable code.

Analytics Service must enforce:

- Allowlisted operation identifiers.
- Typed parameters.
- Resource limits.
- Timeouts.
- Output-size limits.
- Execution identity.
- Full provenance.

Visualization output must be declarative data, not executable code.

## Alternatives considered

### Execute generated Python inside the agent container

Rejected due to security, reproducibility, and operational risk.

### Unrestricted remote notebook submission

Rejected because it allows arbitrary execution beyond approved analytical
boundaries.

### Fully isolated code sandbox

Deferred. It may be evaluated later through a separate ADR.

## Validation

This decision is validated when:

- Agent containers contain no code-execution endpoint.
- Attempts to submit arbitrary Python or shell commands are rejected.
- Analytics operations require approved operation identifiers.
- Every analytical result maps to a versioned operation or job.
- Frontend visualization accepts only declarative chart specifications.
