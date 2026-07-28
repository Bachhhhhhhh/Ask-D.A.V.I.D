# Platform Roadmap

## Purpose

This roadmap defines the implementation sequence for the Ask D.A.V.I.D.-inspired Data Platform.

Each stage should be implemented as an independent goal with:

- A clear objective.
- Measurable outcomes.
- Explicit acceptance criteria.
- Validation commands.
- A stopping condition.
- A dedicated review.
- A dedicated commit or related commit set.

Do not submit the entire roadmap as one implementation goal.

## Execution workflow

For every goal:

```text
1. Read MASTER_GOAL.md.
2. Read ARCHITECTURE.md.
3. Read NON_GOALS.md.
4. Read all accepted ADRs.
5. Inspect the current repository.
6. Produce an implementation plan.
7. Review architecture impact.
8. Implement one goal.
9. Run validation.
10. Verify acceptance criteria independently.
11. Document remaining manual actions.
12. Commit the completed goal.
13. Continue only after approval.
```

## Goal 1 — Architecture contract

### Objective

Create and approve architecture documentation, ADRs, boundaries, component responsibilities, and fixed technology decisions.

### Measurable outcome

- All required documentation files exist.
- Decisions are consistent across files.
- Every major component has one declared responsibility.
- No architecture conflict exists.
- The platform contains exactly three specialized sub-agents.
- Source-of-truth and serving responsibilities are explicit.

### Completion gate

A new engineer can explain the data lifecycle, agent lifecycle, governance model, and tool-service boundary using only the documentation.

## Goal 2 — Repository and development foundation

### Objective

Create:

- Repository structure.
- Dependency management.
- Formatting.
- Linting.
- Type checking.
- Unit testing.
- Docker foundations.
- Local development commands.
- CI foundations.

### Measurable outcome

The following commands succeed on a clean environment:

```bash
make setup
make test
make local-up
```

No secrets are stored in the repository.

### Implementation status

Completed: repository structure, local development tooling, typed
configuration validation, quality gates, and non-deploying CI are in place.

## Goal 3 — AWS infrastructure foundation

### Objective

Create reusable Terraform infrastructure for:

- Networking.
- Application runtime.
- Storage.
- Durable state.
- Cache.
- Secrets.
- Encryption.
- Logging.
- Observability.

### Target components

- VPC.
- Private subnets.
- VPC endpoints.
- ECS Fargate.
- Application Load Balancer.
- ECR.
- RDS PostgreSQL.
- ElastiCache Redis.
- S3.
- KMS.
- Secrets Manager.
- CloudWatch.

### Measurable outcome

- Terraform formatting passes.
- Terraform validation passes.
- Static security scans pass.
- A development environment plan is generated.
- RDS and Redis are private.
- Encryption is enabled.
- Public S3 access is blocked.
- Workloads use IAM roles.

## Goal 4 — Databricks, Unity Catalog, and Iceberg

### Objective

Create the governed lakehouse foundation.

### Measurable outcome

- Unity Catalog is configured.
- Governed Iceberg tables exist in development.
- Synthetic data flows from Raw to Curated to Business.
- Permissions prevent unauthorized access.
- Lineage is visible.
- Table history and snapshots are testable.

## Goal 5 — Reusable ingestion framework

### Objective

Create reusable ingestion and transformation interfaces for future Green SM sources.

### Initial source types

- Relational-style batch source.
- File source.
- Streaming-style source.
- Document source.

### Measurable outcome

- Sources are onboarded through contracts and configuration.
- Runs are idempotent.
- Invalid records are quarantined.
- Incremental processing is supported.
- Provenance is preserved.
- Backfill and retry are documented and testable.

## Goal 6 — Apache Doris serving layer

### Objective

Deploy Doris as a low-latency serving layer over governed Iceberg-derived data.

### Measurable outcome

- Doris serving datasets originate from Iceberg.
- Doris data can be fully rebuilt from Iceberg.
- Agent access is read-only.
- Query limits and audit are enforced.
- Refresh lag is observable.
- Performance benchmark targets are met.

### Suggested benchmark

- At least 10 million synthetic rows.
- Simple filtered aggregation P95 below 2 seconds.
- At least 20 concurrent synthetic users.
- Failed or timed-out query rate below 1%.

## Goal 7 — OpenSearch Serverless knowledge layer

### Objective

Create the document ingestion, embedding, indexing, authorization, retrieval, and citation foundation.

### Measurable outcome

- Original documents remain on S3.
- OpenSearch stores derived chunks and embeddings.
- Restricted chunks are never returned to unauthorized users.
- Citation metadata is complete.
- Document updates replace stale indexed versions.
- Retrieval metrics are available.

### Suggested benchmark

- At least 10,000 synthetic chunks.
- Retrieval P95 below 1.5 seconds.
- Citation metadata completeness of 100%.
- Unauthorized retrieval count of zero.
- Synthetic Recall@5 of at least 0.80.

## Goal 8 — Controlled tool services

### Objective

Build:

- Query Service.
- Retrieval Service.
- Analytics Service.
- Metadata Service.

### Measurable outcome

- Agents contain no direct data-store credentials.
- DDL and DML are rejected deterministically.
- Every call includes user identity and graph identity.
- All results contain provenance.
- Services return typed errors.
- Authorization is independently enforced.

## Goal 9 — LangGraph multi-agent runtime

### Objective

Implement one Supervisor and exactly three specialized sub-agents.

### Target graph

```text
START
  ↓
Load context
  ↓
Supervisor
  ├── Structured Data Agent
  ├── Unstructured Data Agent
  └── Analytics Agent
  ↓
Merge results
  ↓
Reflection
  ↓
Final response
  ↓
END
```

### Measurable outcome

- Exactly three specialized sub-agents exist.
- Routing decisions use structured schemas.
- Selected agents may run in parallel.
- Retries are bounded.
- Graph execution is durable.
- Tool access occurs only through approved services.
- Execution is traceable.

### Suggested benchmark

- Agent-selection accuracy of at least 95%.
- Graph completion rate of at least 98%.
- Unsupported tool-execution attempts of zero.
- Unbounded executions of zero.

## Goal 10 — Memory, reflection, and human feedback

### Objective

Implement:

- Durable checkpoints.
- Historical context.
- Deterministic validation.
- Semantic review.
- Bounded retry.
- Human interruption.
- Graph resume.

### Measurable outcome

- Active runs survive service restart.
- Human review resumes the exact graph state.
- Numeric inconsistencies are detected.
- Missing required citations block delivery.
- Human decisions are audited.
- Redis loss does not destroy durable state.

## Goal 11 — Experience and visualization layer

### Objective

Create:

- Authenticated API.
- Chat interface.
- Review interface.
- Structured-result display.
- Citation viewer.
- Chart renderer.
- Execution-status stream.

### Measurable outcome

A synthetic response displays:

- Narrative.
- Structured table.
- Allowlisted chart.
- Citation.
- Data freshness.
- Query provenance.
- Agent status.
- Human-review state where applicable.

## Goal 12 — Security, governance, and observability

### Objective

Implement cross-cutting controls and full request tracing.

### Measurable outcome

- Every answer is traceable to queries, jobs, and documents.
- Unauthorized requests fail before execution.
- Secrets do not appear in logs.
- Alerts exist for failures, stale data, and high error rates.
- Cost is attributable by environment and service.
- Synthetic-data lineage is available.

## Goal 13 — Synthetic evaluation and release gates

### Objective

Create:

- Evaluation datasets.
- Attack scenarios.
- Failure injection.
- Performance benchmarks.
- CI release gates.

### Required release gates

| Metric | Minimum target |
|---|---:|
| Supervisor routing accuracy | 95% |
| Graph completion rate | 98% |
| SQL execution success | 95% |
| Structured answer correctness | 90% |
| Citation precision | 95% |
| Synthetic Recall@5 | 80% |
| Unauthorized data exposure | 0 |
| Agent-executed DDL or DML | 0 |
| Chart-to-result consistency | 100% |
| Unbounded graph executions | 0 |
| Critical security tests passed | 100% |

Deployment must fail when a critical authorization, security, provenance, or consistency test fails.

## Goal 14 — Green SM onboarding contract

### Objective

Prepare contract-driven onboarding for future Green SM sources without using actual Green SM production data.

### Required templates

- Source registration.
- Dataset contract.
- Business glossary.
- Metric definition.
- Identity mapping.
- Sensitivity classification.
- Refresh SLA.
- Quality rules.
- Doris serving decision.
- OpenSearch indexing decision.
- Access-control matrix.
- Evaluation questions.

### Measurable outcome

A mock Green SM-style source can be onboarded without changing:

- The source-of-truth architecture.
- The catalog decision.
- The serving-layer decision.
- The retrieval-layer decision.
- The three-agent architecture.
- The controlled tool-service boundary.

## Roadmap completion condition

The infrastructure roadmap is complete when:

- The synthetic end-to-end acceptance scenario succeeds.
- All critical evaluation gates pass.
- Security and authorization tests pass.
- Every response has traceable provenance.
- The platform is ready for contract-driven Green SM data onboarding.
