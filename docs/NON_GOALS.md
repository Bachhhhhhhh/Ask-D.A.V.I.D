# Non-Goals

This document defines what must not be implemented during the initial platform and MVP phases.

A non-goal may only be changed through an approved Architecture Decision Record.

## 1. No real Green SM production data

The initial platform must not ingest, store, expose, or claim to represent real Green SM production data.

Use neutral synthetic:

- Entities.
- Events.
- Metrics.
- Transactions.
- Documents.
- Historical records.
- Analytical results.

The infrastructure phase validates platform behavior, not Green SM business accuracy.

## 2. No more than three specialized sub-agents

The MVP contains exactly:

1. Structured Data Agent.
2. Unstructured Data / RAG Agent.
3. Analytics Agent.

Do not add:

- Data Quality Agent.
- Governance Agent.
- Metadata Agent.
- Visualization Agent.
- Security Agent.
- Monitoring Agent.
- Lineage Agent.
- Action Agent.
- Report Agent.
- A separate SQL Agent.
- Dynamically generated autonomous agents.

These capabilities must remain tools, services, policies, nodes, middleware, or internal subgraphs unless a future ADR approves a change.

## 3. No Doris source-of-truth role

Apache Doris must not:

- Become the authoritative business-data store.
- Be the only copy of a dataset.
- Be used to rebuild Iceberg.
- Own canonical historical truth.
- Receive authoritative updates that bypass the governed Iceberg lifecycle.

Doris data must be rebuildable from Iceberg.

## 4. No competing primary catalog

AWS Glue must not become a competing primary metadata authority for the same governed Iceberg tables.

Unity Catalog remains the primary catalog.

Do not create split ownership where multiple catalogs independently mutate the same table metadata.

## 5. No Delta Lake as the system of record

Delta Lake must not replace Apache Iceberg as the system-of-record table format.

A future integration may use Delta for a narrowly scoped capability only after an approved ADR.

Authoritative structured business data must remain in Iceberg.

## 6. No direct agent access to infrastructure

Agents must not directly connect to:

- Doris.
- Databricks SQL.
- OpenSearch Serverless.
- Amazon S3.
- Unity Catalog.
- Operational databases.
- AWS administrative APIs.

Agents must use controlled tool services.

## 7. No database credentials in agent processes

Agent containers must not contain reusable production credentials for data stores.

Use workload identity, IAM roles, and controlled service boundaries.

## 8. No DDL or DML from agents

Agents must not execute:

- `CREATE`
- `ALTER`
- `DROP`
- `TRUNCATE`
- `INSERT`
- `UPDATE`
- `DELETE`
- `MERGE`
- `GRANT`
- `REVOKE`
- Administrative procedures

The MVP is read-only from the user and agent perspective.

## 9. No arbitrary code execution

The Analytics Agent must not execute arbitrary:

- Python.
- Shell commands.
- Notebook code.
- User-provided code.
- LLM-generated scripts.

Analytics must use approved SQL operations or parameterized jobs with explicit schemas and resource limits.

## 10. No arbitrary frontend code generation

The LLM must not generate or execute:

- JavaScript.
- HTML.
- CSS.
- React components.
- Browser scripts.
- Embedded third-party content.

Visualization must use an allowlisted structured schema.

## 11. No autonomous business actions

The MVP must not autonomously:

- Send customer communications.
- Modify business records.
- Create financial transactions.
- Change operational configurations.
- Approve business decisions.
- Trigger irreversible workflows.
- Delete data.

Future action capabilities require a separate ADR and mandatory human approval.

## 12. No security decisions from prompts

Prompts and LLM responses must not determine:

- User authorization.
- Row-level access.
- Document ACLs.
- IAM permissions.
- Secret access.
- Data sensitivity.
- Network access.

Security decisions must be deterministic and independently enforced.

## 13. No unrestricted Raw or Silver queries

Agents must not query Raw or Curated layers directly by default.

They must use:

- Gold tables.
- Approved semantic views.
- Approved diagnostics exposed through controlled tools.

## 14. No unsupported document claims

The system must not present document-based claims without source metadata when citations are required.

Required citation fields include:

- Document ID.
- Document version.
- Page or section.
- Source system.
- Retrieval provenance.

## 15. No hidden or unbounded retry loops

LangGraph execution must not:

- Retry indefinitely.
- Recursively create agents.
- Continue without a termination condition.
- Retry failed external calls without limits.
- Execute expensive analytics repeatedly without controls.

## 16. No production deployment during documentation goals

Documentation goals must not automatically:

- Apply Terraform.
- Deploy AWS resources.
- Create production Databricks resources.
- Modify production catalogs.
- Create production Doris clusters.
- Create production OpenSearch collections.

Deployment requires an explicit implementation goal and environment approval.

## 17. No claim that synthetic data represents Green SM

Synthetic datasets are test assets only.

Reports and interfaces must not label synthetic metrics as actual Green SM business results.

## 18. No architecture drift without an ADR

The following decisions cannot change silently:

- Unity Catalog as primary catalog.
- S3 and Iceberg as system of record.
- Doris as serving layer.
- OpenSearch Serverless as retrieval layer.
- Exactly three specialized sub-agents.
- Controlled tool-service access.

A change requires:

1. A new ADR.
2. Explicit approval.
3. Migration implications.
4. Security review.
5. Updated architecture documentation.
