# Goal 5 MVP Phase 5-2 offline implementation

## Status

**IMPLEMENTED OFFLINE — CONNECTED VALIDATION NOT RUN.**

This report records the repository-only implementation of the reduced Goal 5
MVP for neutral structured CSV, text/Markdown documents, and deterministic CDC
JSONL. No Terraform plan, Terraform apply/destroy, AWS API operation, S3
mutation, Databricks bundle operation, SQL/job run, table mutation, or compute
creation occurred during this checkpoint.

The connected approval boundary begins only after this report: read-only
revalidation, an optional saved Terraform plan for three source objects,
strict bundle validation, bundle deployment, and separately approved workflow
execution.

## Implemented scope

### Offline domain package

`packages/ingestion-framework` is a standard-library-only typed package with:

- JSON contract parsing and fail-closed validation for the approved development
  catalog, schemas, logical source keys, sensitivity, quality rules, and
  accepted Iceberg/UniForm policy;
- immutable `IngestionRun`, `Provenance`, `QuarantinedRecord`, and
  `AdapterResult` models;
- a typed `SourceAdapter` protocol;
- `FileSourceAdapter` for CSV headers/types, quarantine, deterministic primary
  key selection, and provenance;
- `DocumentSourceAdapter` for only text/plain and text/markdown, stable
  document identity/version, metadata, and provenance;
- `CDCSourceAdapter` for INSERT/UPDATE/DELETE, event validation, deterministic
  ordering, event-ID deduplication, raw-history statistics, and current-state
  tombstones;
- deterministic required/not-null and uniqueness quality results and stable
  record hashes.

No adapter accesses AWS, Databricks, S3, credentials, agents, or arbitrary
generated code.

### Neutral fixtures and contracts

The tracked fixtures contain only synthetic technical values:

- `synthetic_data/goal_05/structured/synthetic_events.csv`: three valid rows,
  one duplicate primary key, and one invalid metric value;
- `synthetic_data/goal_05/documents/neutral_technical_guide.md`: neutral
  Markdown source;
- `synthetic_data/goal_05/cdc/synthetic_changes.jsonl`: INSERT, UPDATE,
  INSERT, DELETE, and one duplicate event ID;
- one versioned machine-readable contract for each source pattern.

### Databricks declarative assets

The existing bundle root now includes one additive Goal 5 job using the
existing `${var.warehouse_id}`. It declares no cluster or warehouse. The SQL
files create nine Unity Catalog managed tables without `LOCATION`, read the
approved parameterized source paths, preserve provenance and validation
status/reason, quarantine invalid structured rows, build Raw → Curated →
Business structured outputs, record document metadata, preserve CDC history,
and materialize CDC DELETE tombstones. Verification SQL is read-only. Source
path assertions are restricted to the three approved development Goal 5
prefixes.

The bundle source is additive to Goal 4. The Goal 4 validator was updated only
to permit the additive top-level `sql/goal_05/*.sql` include while continuing
to require the Goal 4 top-level include and remediation exclusion.

### Terraform boundary

`infrastructure/environments/development/goal5.tf` declares exactly three
SSE-KMS `aws_s3_object` source fixtures in existing raw/documents buckets. All
three are gated by `goal_5_source_objects_enabled`, whose default is `false`.
No bucket, IAM, KMS, external-location, metastore, catalog, schema, warehouse,
or persistent cluster is added. The connected plan must explicitly enable the
flag and must be reviewed as exactly three creates with no replacement,
destroy, or unrelated action.

## Offline validation evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Goal 5 static repository validator | PASS | `python scripts/validate_goal5.py` |
| Goal 4 static validator and regression suite | PASS | Goal 4 static tests: 32 passed; additive Goal 5 sync include accepted without weakening remediation exclusion |
| Goal 5 unit/static/table-format tests | PASS | 63 passed; package branch coverage 97.20% with `--cov-fail-under=90` |
| Full repository tests | PASS | 118 passed; combined foundation/ingestion branch coverage 97.15% with report redirected to `/tmp/goal5-full.xml` |
| Ruff format/lint | PASS | `ruff format --check .`; `ruff check .` |
| Strict mypy | PASS | 13 source files, no issues |
| Bandit | PASS | Offline scan of `packages` and `scripts` |
| detect-secrets | PASS | Existing baseline hook run over tracked and current untracked candidates; no new finding |
| `git diff --check` | PASS | No whitespace errors |
| Terraform formatting/validate/tests | UNVERIFIED | Terraform binary is not installed in this environment; no initialization, backend access, plan, apply, or AWS call was attempted |
| TFLint/Trivy | UNVERIFIED | Binaries are not installed in this environment |
| Databricks bundle validation | UNVERIFIED | Deliberately deferred to connected approval boundary |
| SQL/job execution and live tables | UNVERIFIED | Deliberately not run |

The repository's existing `coverage.xml` and `.pytest_cache` contain files
owned by another environment user. Full tests were therefore executed with
cache/report output redirected to `/tmp`; this did not modify tracked files.

## Requirements covered offline

The offline implementation and tests cover valid/invalid contracts, source
adapter boundaries, provenance, schema-invalid quarantine, deterministic
structured deduplication, required/uniqueness quality rules, Markdown and
unsupported-document behavior, document ID/version, CDC INSERT/UPDATE/DELETE,
event deduplication/order, tombstones, invalid-event safe failure, accepted
table-format policy, plain-Delta rejection, and static scope/security checks.

## Not yet verified

The following require connected evidence and remain **UNVERIFIED**:

- Goal 4 foundation remains healthy in the target workspace;
- source objects exist in the approved S3 prefixes and retain SSE-KMS;
- `read_files` and parameterized source paths work in the current Serverless
  SQL engine;
- the nine live tables are Unity Catalog managed and classify as native
  `ICEBERG` or `DELTA_UNIFORM_ICEBERG` through the authoritative Tables API;
- structured, document, and CDC workflows execute successfully;
- original document object preservation and governed metadata are queryable;
- connected quality, audit, lineage, and provenance evidence;
- idempotency rerun for all three patterns;
- connected safe-failure behavior;
- no unnecessary compute remains running after execution;
- final zero-drift/scope audit and durable Goal 5 acceptance report.

The existing Goal 4 seven-table Delta UniForm representation remains accepted
and explicitly disclosed. No Goal 4 table is changed by this implementation.

## Deferred scope

Relational connectors, production CDC, Debezium, Kafka/MSK/Kinesis, REST
extraction, streaming, PDF/OCR, chunking, embeddings, OpenSearch, Doris,
LangGraph/agents, generalized replay/backfill, advanced schema evolution and
watermarks, and production scheduling remain deferred and are not Goal 5
failures.

## Next checkpoint

Goal 5 Phase 5-4 connected deployment review. The exact approval sequence is
documented in `docs/plans/GOAL-05-MVP-INGESTION-PLAN.md` and
`docs/runbooks/GOAL-05-INGESTION.md`. No connected operation is authorized by
this report.
