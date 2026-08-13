# Goal 5 MVP ingestion runbook

Goal 5 is a development-only, synthetic-data MVP for three reusable source
patterns: structured CSV, text/Markdown documents, and a deterministic CDC
JSONL batch. It reuses the Goal 4 Unity Catalog catalog, schemas, IAM storage
credential, external locations, approved S3 buckets, KMS key, and existing
Small Serverless SQL Warehouse.

This runbook does not authorize AWS or Databricks mutation. Each connected
checkpoint below requires a separate explicit approval and a fresh review of
the exact source or saved plan. Never place credentials, tokens, state, or
saved plans in the repository.

## Repository assets

- `packages/ingestion-framework/`: typed contracts, run/provenance models,
  quality results, and the three credential-free source adapters;
- `synthetic_data/goal_05/`: machine-readable contracts and neutral fixtures;
- `databricks/sql/goal_05/`: managed-table creation, three ingestion paths,
  output assertions, and read-only idempotency assertions;
- `databricks/bundles/goal_05_ingestion/resources.yml`: one sequential SQL
  workflow using the existing warehouse;
- `scripts/validate_goal5.py`: offline repository/scope validator;
- `scripts/verify_goal5_table_inventory.py`: offline validator for sanitized
  Tables API evidence;
- `infrastructure/environments/development/goal5.tf`: three optional,
  Terraform-owned SSE-KMS source objects in existing buckets.

## Offline validation

Run from the repository root without credentials or cloud access:

```bash
make format-check
make lint
make typecheck
make test
make databricks-static
make goal5-static
make security
git diff --check
```

If Terraform source objects are included in a reviewed change, also run the
existing offline Terraform formatting, validation, mock tests, TFLint, and
Trivy gates. Do not run a connected plan during the offline phase.

## Data and table policy

The three source objects, when explicitly approved, are:

| Pattern | Existing bucket/prefix | Fixture |
| --- | --- | --- |
| Structured CSV | Goal 3 raw bucket `/unity-catalog/development/goal5/structured/` | `synthetic_events.csv` |
| Document | Goal 3 documents bucket `/unity-catalog/development/goal5/documents/` | `neutral_technical_guide.md` |
| CDC JSONL | Goal 3 raw bucket `/unity-catalog/development/goal5/cdc/` | `synthetic_changes.jsonl` |

The objects use the existing SSE-KMS key. No bucket, IAM, KMS, external
location, metastore, catalog, schema, warehouse, or persistent cluster is
created by Goal 5.

All nine Goal 5 tables are Unity Catalog managed tables with no explicit
`LOCATION`. The accepted source-of-truth format is either native `ICEBERG` or
managed `DELTA_UNIFORM_ICEBERG`. A plain `DELTA` table without explicit
UniForm/Iceberg properties fails acceptance. When the Tables API reports
`DELTA` with `delta.enableIcebergCompatV2=true`,
`delta.universalFormat.enabledFormats=iceberg`, and an Iceberg metadata path,
the report must say exactly:

> Unity Catalog managed Delta with UniForm Iceberg interoperability.

It must not say native Apache Iceberg.

## Connected approval sequence

1. Reverify the approved Databricks profile, workspace, account, region,
   metastore, catalog, storage credential, locations, and existing warehouse.
2. Create a saved development Terraform plan only if the three source objects
   are still required. Expected managed actions are exactly three object
   creates, no replacement, no destroy, and no unrelated resource action.
3. Apply only that exact saved plan after separate approval. If the plan
   differs, stop.
4. Run one strict connected bundle validation for the reviewed Goal 5 source
   set. The corrected CDC source set passed this checkpoint on `2026-08-13`;
   see `docs/verification/GOAL-05-CDC-BUNDLE-VALIDATION-2026-08-13.md`. Do not
   run jobs or SQL at this checkpoint.
5. Deploy the reviewed bundle only after separate approval. The corrected
   source deployment passed on `2026-08-13`; see
   `docs/verification/GOAL-05-CDC-BUNDLE-DEPLOYMENT-2026-08-13.md`. Inspect
   the job, task files, run-as principal, warehouse ID, and permissions
   read-only.
6. Before billable execution, report warehouse ID `757e0335c6efb51e`, current
   state, size, serverless status, and auto-stop behavior. Run the workflow
   once only after separate approval.
7. Inspect task/run results immediately. A failed task stops the sequence; do
   not retry, redeploy, or mutate tables without a new review.
   The approved Goal 5 source paths require two isolated, read-only external
   locations and workflow-principal-only `READ FILES`. If an initial run shows
   a source-file permission denial, create a separate saved Terraform plan for
   that declarative remediation; expected actions are one IAM inline-policy
   update plus two source locations, bindings, and scoped grants. No KMS,
   storage-credential, catalog, schema, warehouse, or table action is expected.
8. If a deterministic SQL or acceptance failure is found, perform only an offline
   declarative correction, static/regression validation, and a fresh strict
   bundle validation before requesting a retry. The resolved CDC scope failure
   (`unique_events` referenced outside its defining CTE statement) is recorded
   in `docs/verification/GOAL-05-CDC-SQL-REMEDIATION-2026-08-13.md`. The current
   offline-only remediation makes the CDC output assertion numeric rather than
   dependent on JSON serialization spelling; see
   `docs/verification/GOAL-05-CDC-OUTPUT-ASSERTION-REMEDIATION-2026-08-13.md`.
   Its fresh strict connected bundle validation passed; see
   `docs/verification/GOAL-05-CDC-OUTPUT-ASSERTION-BUNDLE-VALIDATION-2026-08-13.md`.
   Its separately approved deployment also passed; see
   `docs/verification/GOAL-05-CDC-OUTPUT-ASSERTION-BUNDLE-DEPLOYMENT-2026-08-13.md`.
9. Run the exact same source versions again only under a separate idempotency
   approval. Verify trusted output does not duplicate while a new audit run is
   recorded.
10. Perform read-only Tables API, S3-object, provenance, quality, and
   authorization checks. Save sanitized evidence only.

## Failure and delete semantics

Invalid contracts, invalid CSV rows, unsupported document types, and invalid
CDC events fail closed or enter an explicit quarantine with provenance. CDC
`DELETE` is represented as a governed current-state tombstone with
`is_deleted = true` and a null payload; the raw unique event remains in CDC
history. Duplicate event IDs are recorded once with an occurrence count and
are not applied twice.

## Explicitly deferred

Goal 5 does not implement relational connectors, production CDC, Debezium,
Kafka/MSK/Kinesis, REST extraction, streaming, PDF/OCR, chunking, embeddings,
OpenSearch, Doris, agents/LangGraph, generalized replay/backfill, advanced
schema evolution, or production scheduling. These remain later roadmap work.

## Stop conditions

Stop and request review if a new metastore/catalog/schema/credential/location/
warehouse/cluster is proposed, if a plain Delta table is observed, if a
production scope or real Green SM data appears, if an accepted ADR would need
to change, if a plan includes replacement/destroy/unrelated resources, or if
any connected job/task fails.
