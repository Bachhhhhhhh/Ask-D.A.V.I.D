# ADR-005: Exactly Three Specialized Sub-Agents in the MVP

- **Status:** Accepted
- **Decision date:** Initial architecture baseline
- **Owners:** Platform Architecture and AI Platform teams

## Context

The publicly presented Ask D.A.V.I.D. architecture uses a Supervisor pattern with specialized capabilities for:

- Structured data.
- Unstructured data.
- Analytics.

A common implementation risk is to turn every node, function, tool, or policy into a separate autonomous agent.

Excessive agent count causes:

- More routing complexity.
- Higher cost.
- Increased latency.
- Harder evaluation.
- Larger attack surface.
- More difficult debugging.
- Unclear ownership.
- Increased probability of loops.
- Inconsistent behavior.

The MVP requires a minimal but extensible multi-agent design.

## Decision

The MVP contains exactly three specialized sub-agents:

1. Structured Data Agent.
2. Unstructured Data / RAG Agent.
3. Analytics Agent.

One Supervisor coordinates the three agents.

The Supervisor is an agent role but is not counted as a specialized sub-agent.

The following are supporting graph capabilities and must not be implemented as additional specialized agents:

- Planner.
- Router.
- Reflection.
- Guardrails.
- Personalization.
- Memory.
- Human feedback.
- Final response generation.
- Visualization.
- Metadata lookup.
- Data-quality validation.
- Security validation.
- Lineage lookup.
- Monitoring.
- Citation validation.

These capabilities should be implemented as:

- Graph nodes.
- Tools.
- Controlled services.
- Deterministic policies.
- Middleware.
- Internal subgraphs.
- Validation functions.

## Agent boundaries

### Structured Data Agent

Owns:

- Metric interpretation.
- Semantic-schema discovery.
- Query-path selection.
- Structured-query proposals.
- Structured-result interpretation.

Uses:

- Metadata Service.
- Query Service.

### Unstructured Data / RAG Agent

Owns:

- Retrieval-query formulation.
- Metadata-filter selection.
- Evidence evaluation.
- Citation packaging.

Uses:

- Retrieval Service.
- Metadata Service where needed.

### Analytics Agent

Owns:

- Calculation planning.
- Approved analytical-operation selection.
- Analytical-result interpretation.
- Safe visualization specifications.

Uses:

- Analytics Service.
- Query Service where approved.
- Metadata Service.

### Supervisor

Owns:

- User-intent understanding.
- Execution planning.
- Agent selection.
- Parallel or sequential scheduling.
- Result merging.
- Retry routing.
- Human-review routing.
- Final-response preparation.

## Consequences

### Positive

- Simple mental model.
- Lower routing complexity.
- Easier testing.
- Clear ownership.
- Better cost control.
- Better latency control.
- Easier observability.
- Easier security review.
- Direct alignment with the reference architecture.

### Negative

- Individual agents may contain internal subgraphs.
- Boundaries require discipline.
- Some future domains may require architecture review.
- The Supervisor may require sophisticated orchestration logic.
- Teams cannot create new agents merely to isolate every function.

## Rules for adding a future specialized agent

A new specialized agent requires a new ADR demonstrating that:

1. The capability cannot reasonably fit within an existing agent.
2. It requires independent planning and tool selection.
3. It has a distinct security boundary.
4. It has its own evaluation dataset.
5. It improves measurable outcomes.
6. Added latency and cost are acceptable.
7. It does not duplicate a tool or deterministic node.
8. A migration and rollback plan exists.

## Alternatives considered

### One general-purpose agent

Rejected because structured queries, document retrieval, and analytics have different tools, policies, and evaluation requirements.

### Many domain-specific agents

Rejected for the MVP because it increases complexity before the core platform has been validated.

### One agent per tool

Rejected because a tool is an action interface, not necessarily an autonomous reasoning unit.

## Validation

This decision is validated when:

- The implementation contains exactly three specialized sub-agent modules.
- Planner and Router remain Supervisor capabilities.
- Reflection remains a graph-validation stage.
- Visualization remains an Analytics Agent output.
- Metadata and security remain services or policies.
- No fourth specialized agent appears in runtime configuration.
- Evaluation reports routing among the three approved agents.
