# Goal 5 MVP Phase 5-0 preflight

## Scope and safety boundary

This report records the Goal 5 MVP project rehydration and read-only preflight
performed on 2026-08-12. No Databricks object, SQL job, table, AWS resource,
S3 object, Terraform configuration, bundle, or permission was mutated.

The requested scope is the reduced synthetic-only MVP for structured CSV,
text/Markdown documents, and deterministic CDC batches. Production source
connectors, streaming infrastructure, document extraction, embeddings,
OpenSearch indexing, Doris, agents, and Goal 6+ work remain deferred.

## Preflight result

| Check | Result | Evidence |
| --- | --- | --- |
| Goal 4 foundation remains verified | PASS | `docs/PROJECT_STATUS.md` records Goal 4 as verified under the approved project Iceberg-compatibility profile, with evidence commit `a778cfdfceaf6c704f98d83752c54c73a7d9208f` and status checkpoint `6cdd660`. |
| Databricks CLI and profile | PASS | Databricks CLI `1.11.0`; profile `ask-david-development`; active development workspace and principal were resolved without printing credentials. |
| Approved workspace and account | PASS | Workspace `7474644358733471`, AWS account `736956442295`, AWS region `ap-southeast-1`; authenticated principal is the approved development administrator. |
| Unity Catalog metastore | PASS | Metastore `3a7f7e7a-680b-4bd6-907a-6d5e77b43178` is attached to workspace `7474644358733471`; no duplicate metastore was created. |
| Catalog isolation | PASS | Project catalog `ask_david_development` exists. Existing `workspace`, `ml_model_store`, `samples`, and `system` catalogs were not repurposed or modified. |
| Project schemas | PASS | `green_sm_raw`, `green_sm_curated`, `green_sm_business`, `green_sm_ai`, `green_sm_platform`, and `green_sm_sandbox` exist under the project catalog. |
| Storage credential | PASS | `ask-david-development-managed-iceberg` uses the Terraform-created IAM role `ask-david-development-unity-catalog-storage`; no static key was used. |
| External locations | PASS | Seven project locations use only approved Goal 3 development S3 prefixes and the project storage credential. |
| Approved S3 storage | PASS | Read-only AWS inspection confirmed the raw, documents, and artifacts buckets exist in `ap-southeast-1` and have all four public-access-block settings enabled. |
| Existing compute reuse | PASS | Warehouse `757e0335c6efb51e` (`Serverless Starter Warehouse`) is `PRO`, `Small`, serverless-enabled, auto-stop 10 minutes, `STOPPED`, with zero active sessions and zero clusters. No new warehouse or persistent cluster is required by this preflight. |
| Goal 4 table inventory | PASS WITH DISCLOSURE | Tables API returned exactly seven project tables, all `MANAGED`, with `data_source_format = DELTA`, `delta.universalFormat.enabledFormats = iceberg`, and `_iceberg/metadata` paths in approved S3. These are `DELTA_UNIFORM_ICEBERG` under the Goal 5 policy, not native `ICEBERG`. |
| Architecture boundaries | PASS | No Doris, OpenSearch indexing, LangGraph/agent, AWS Glue catalog, real Green SM data, or Goal 6+ implementation was found in the current repository. |

## Authoritative table-format observations

The read-only Databricks Tables API inventory was:

| Table | Type | Tables API format | UniForm / metadata evidence |
| --- | --- | --- | --- |
| `ask_david_development.green_sm_raw.synthetic_events` | `MANAGED` | `DELTA` | `delta.universalFormat.enabledFormats=iceberg`; Iceberg metadata path present |
| `ask_david_development.green_sm_curated.synthetic_events` | `MANAGED` | `DELTA` | `delta.universalFormat.enabledFormats=iceberg`; Iceberg metadata path present |
| `ask_david_development.green_sm_curated.synthetic_entities` | `MANAGED` | `DELTA` | `delta.universalFormat.enabledFormats=iceberg`; Iceberg metadata path present |
| `ask_david_development.green_sm_business.synthetic_metrics` | `MANAGED` | `DELTA` | `delta.universalFormat.enabledFormats=iceberg`; Iceberg metadata path present |
| `ask_david_development.green_sm_ai.synthetic_document_metadata` | `MANAGED` | `DELTA` | `delta.universalFormat.enabledFormats=iceberg`; Iceberg metadata path present |
| `ask_david_development.green_sm_platform.synthetic_agent_execution_audit` | `MANAGED` | `DELTA` | `delta.universalFormat.enabledFormats=iceberg`; Iceberg metadata path present |
| `ask_david_development.green_sm_platform.synthetic_data_quality_results` | `MANAGED` | `DELTA` | `delta.universalFormat.enabledFormats=iceberg`; Iceberg metadata path present |

Goal 5 must preserve this disclosure. New governed tables must be validated
against the accepted policy as either native `ICEBERG` or managed Delta with
verified UniForm interoperability. Plain Delta without interoperability is
not acceptable. Existing Goal 4 tables must not be dropped or recreated merely
to force native format.

The strict wording in ADR-002 remains unchanged. The current project profile
already approved the managed Delta UniForm representation as the development
implementation of Iceberg interoperability; no ADR is modified by Goal 5.
Any future requirement that cannot be satisfied by this profile must stop for
a separately approved architecture decision.

## Reusable assets and intended boundaries

Goal 5 can reuse:

- the existing Unity Catalog project catalog and six schemas;
- the existing project storage credential and seven external locations;
- the raw, curated, business, document, and audit S3 prefixes;
- the existing Serverless SQL warehouse;
- the existing bundle validation and offline quality gates;
- the existing Goal 4 quality/audit patterns, without mutating Goal 4 table
  identities or introducing Goal 4 remediation SQL.

The Phase 5-1 design must add only the minimal repository-managed contract,
adapter, validation, fixture, and workflow abstractions required for the
three synthetic MVP patterns. It must not create duplicate infrastructure or
extend into Doris, OpenSearch, agents, or production connectors.

## Blockers and unverified items

No Phase 5-0 foundation blocker was found. The following are intentionally not
yet verified because implementation has not started:

- Goal 5 machine-readable contracts and adapter interfaces;
- structured, document, and CDC execution outputs;
- Goal 5 governed tables and document objects;
- idempotency and safe-failure behavior;
- connected bundle deployment and synthetic validation.

These are Phase 5-1 onward acceptance items, not evidence of a broken Goal 4
foundation.

## Stopping condition

Phase 5-0 is complete. Stop before implementation until the minimal Goal 5
design is reviewed. No connected deployment, SQL/job run, Terraform operation,
AWS mutation, or additional compute creation is authorized by this report.
