# ADR-010: Green SM Data Is Out of Scope Until Infrastructure Validation

- Status: Accepted
- Decision date: Initial architecture baseline
- Owners: Platform Architecture, Product, Data Platform, and Security teams

## Context

The platform is intended to support future Green SM data and AI use cases.

However, introducing real domain data before the infrastructure, security,
governance, access controls, evaluation framework, and agent boundaries are
validated would create unnecessary risk.

The platform must first prove that its technical architecture works safely and
reproducibly.

## Decision

Actual Green SM production data and production business logic are out of scope
until the infrastructure platform passes its synthetic acceptance criteria.

The initial implementation must use neutral synthetic:

- Entities.
- Events.
- Metrics.
- Transactions.
- Documents.
- Analytical scenarios.
- Access-control scenarios.
- Failure scenarios.

Synthetic assets must not be represented as actual Green SM business data.

## Infrastructure validation requirements

Before real Green SM onboarding, the platform must demonstrate:

- Repeatable infrastructure provisioning.
- Environment isolation.
- Unity Catalog governance.
- Governed Iceberg lifecycle.
- Doris rebuildability.
- OpenSearch document ACL enforcement.
- Controlled tool-service boundaries.
- Durable LangGraph execution.
- Bounded reflection retries.
- Human interruption and resume.
- End-to-end provenance.
- Security evaluation.
- Synthetic release gates.

## Green SM onboarding requirements

Future Green SM data onboarding requires:

- Source registration.
- Data-owner approval.
- Data contract.
- Business glossary.
- Metric definitions.
- Sensitivity classification.
- Access-control matrix.
- Quality rules.
- Freshness SLA.
- Doris serving decision.
- OpenSearch indexing decision.
- Evaluation questions.
- Security review.

## Consequences

### Positive

- Lower initial security risk.
- Faster infrastructure iteration.
- Clear separation between platform and domain logic.
- Easier synthetic testing.
- Reduced risk of exposing sensitive business information.
- Better onboarding discipline.

### Negative

- Initial demonstrations do not provide real Green SM business insights.
- Some domain-specific requirements may appear later.
- Synthetic performance may not represent every production workload.
- Domain SMEs are still required before production onboarding.

## Implementation constraints

- Do not use real Green SM production records.
- Do not copy Green SM schemas without approved onboarding.
- Do not label synthetic dashboards as real Green SM reports.
- Do not hard-code Green SM-specific business logic into platform services.
- Platform interfaces must remain domain-neutral.
- Domain onboarding must not require a fourth specialized sub-agent.

## Alternatives considered

### Start immediately with real Green SM data

Rejected because platform controls and governance have not yet been validated.

### Build Green SM-specific architecture first

Rejected because the target is a reusable data and agent platform.

## Validation

This decision is validated when:

- Synthetic end-to-end acceptance tests pass.
- No real Green SM data exists in initial environments.
- Synthetic assets are clearly labeled.
- A mock domain source can be onboarded through the documented contract.
- Core architecture requires no redesign for future Green SM onboarding.
