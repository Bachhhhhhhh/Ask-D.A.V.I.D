# Goal 5 numeric CDC assertion workflow success

Date: 2026-08-13
Scope: one approved workflow run after deployment of the numeric CDC output
assertion, with immediate read-only inspection. No implicit retry, redeploy,
second workflow, Terraform operation, AWS operation, or ad-hoc SQL execution
occurred in this checkpoint.

## Pre-run

- Job: `382877731318442` (`ask-david-development-goal5-synthetic-ingestion`).
- Existing warehouse: `757e0335c6efb51e`, Serverless Starter Warehouse,
  Small/PRO, serverless enabled, auto-stop 10 minutes, STOPPED before this run.
- Active Goal 5 runs: none.
- Deployed output-verification file hash:
  `594824b4b647de6451cf57fdd83bf927137a4122f4b0010aff09042b7596cb30`.

## Single approved run

Exactly one `run-now` request created workflow run `172279846311777`.

| Task | Task run | Result |
| --- | --- | --- |
| `create_goal5_tables` | `337153321465780` | SUCCESS |
| `ingest_structured_csv` | `820950727263544` | SUCCESS |
| `ingest_document` | `1114333960416571` | SUCCESS |
| `ingest_cdc` | `669350528848432` | SUCCESS |
| `verify_goal5_outputs` | `474038466056854` | SUCCESS |
| `verify_goal5_idempotency` | `203226640368614` | SUCCESS |

The parent workflow terminated `SUCCESS`, with no task retry or cancellation.

## What the successful SQL tasks prove

`verify_goal5_outputs` completed its read-only assertions against the live
Unity Catalog tables. It verifies the structured valid-row/quarantine/
deduplication/Business reconciliation path; accepted document metadata and its
approved S3 source URI; CDC Raw history with duplicate occurrence count and
validation status; CDC UPDATE current-state value and DELETE tombstone; three
auditable ingestion paths; and queryable passing quality results.

`verify_goal5_idempotency` completed its read-only assertions after the same
source versions were re-executed. It verifies unique structured source keys,
unique document identity/version, at-most-once CDC event IDs, and at least six
auditable source-pattern runs. This is connected evidence that the three MVP
paths preserve trusted data deterministically across re-execution while
recording audit runs.

## Boundary

No additional workflow is needed or authorized by this checkpoint. Remaining
Goal 5 finalization consists of read-only Table API/S3/health/drift evidence,
durable acceptance mapping, and the separately approved final zero-drift
Terraform plan required because Goal 5 created declarative source/access
resources.
