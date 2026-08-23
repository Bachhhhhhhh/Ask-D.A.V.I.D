# Goal 7 AOSS vector upsert offline remediation — 2026-08-21

## Boundary

This checkpoint was approved for offline source, test, and documentation
remediation only. It did not build or push an image, update ignored Terraform
inputs, create a connected Terraform plan, call AWS or Databricks, deploy a
bundle, or run/retry an ECS task.

## Failure evidence

The one approved private indexer revision-3 task stopped with exit code `1` in
`bulk_upsert()` and reported only `RuntimeError: AOSS vector upsert failed`.
The task did not produce an AOSS response status/body before exiting, so this
report does not claim a task-level HTTP status. Evidence is recorded in
`GOAL-07-INDEXER-TASK-FAILURE-R5-2026-08-21.md`.

## Offline root-cause determination

The deployed implementation used an OpenSearch bulk `update` action with a
caller-supplied deterministic `_id` and `doc_as_upsert=true`. That write shape
is not supported by Amazon OpenSearch Serverless `VECTORSEARCH` collections;
the service contract permits vector document creation with generated IDs and
does not provide the SEARCH-collection custom-ID/upsert behavior used by the
old implementation. The relevant AWS documentation is:

- <https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-overview.html>
- <https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-genref.html>

The deterministic application key remains `chunk_id`; it is not used as the
AOSS document `_id`.

## Remediation implemented

`AossClient.bulk_upsert()` now performs a bounded per-chunk flow:

1. Search by the exact deterministic `chunk_id` in `_source`.
2. If no document exists, create through `POST /{index}/_doc`, allowing AOSS
   to assign the document ID.
3. If a document exists, update its discovered generated `_id` through the
   bulk document-ID update path without `doc_as_upsert`.

The implementation also records bounded non-secret error details from AOSS
responses and bulk item failures. Final verification matches the deterministic
`chunk_id` in `_source`, not the generated AOSS `_id`.

## Offline verification

| Check | Result |
| --- | --- |
| Goal 7 static validator | PASS |
| Goal 7 focused unit tests | PASS — 20 passed |
| Full repository unit suite | UNVERIFIED — collection stopped because optional `pydantic` is not installed in this environment |
| Python compilation | PASS |
| Ruff lint | PASS |
| Ruff format check | PASS |
| `git diff --check` | PASS |
| Infrastructure preflight | PASS — structurally valid state KMS ARN |
| AWS/Databricks mutation or connected plan | NOT RUN — prohibited at this boundary |
| Corrected image/task runtime behavior | UNVERIFIED — requires separate approval |

## Current checkpoint

Goal 7 remains **UNVERIFIED**. The source remediation is offline-validated,
but no claim is made that the corrected image has been built, promoted,
deployed, or exercised against the live AOSS collection. The next checkpoint
requires separate approval for image build/push and digest inspection, then a
separate digest-only task-definition plan/apply and one no-retry private task.
