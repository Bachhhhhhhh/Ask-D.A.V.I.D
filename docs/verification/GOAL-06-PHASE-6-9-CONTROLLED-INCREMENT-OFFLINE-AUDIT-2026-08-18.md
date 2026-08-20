# Goal 6 Phase 6-9 controlled increment — offline contract audit

Date: `2026-08-18`

Status: `OFFLINE VALIDATED — BUNDLE NOT VALIDATED/DEPLOYED OR RUN`

## Audited flow

```text
one neutral CSV record
  -> governed Goal 5 Raw MERGE
  -> governed Goal 5 Curated MERGE
  -> governed Goal 5 Business MERGE
  -> separate future Doris admin refresh
```

The Databricks SQL never connects to Doris. The authoritative lakehouse changes
first; Doris can change only in a later, separately approved refresh task.

## Deterministic/idempotent contract

| Layer | Merge identity | Expected result |
| --- | --- | --- |
| Raw | dataset ID + SHA-256 record hash | exactly one accepted record |
| Curated | dataset ID + event ID | exactly one quality-PASS record |
| Business | dataset ID + metric date + category | exactly one aggregate with total `42.0` |

All three MERGEs use matched-update plus not-matched-insert semantics. Repeating
the same fixture therefore updates the same logical records instead of adding
duplicates. The verification task asserts a count of one at each layer and the
exact Business aggregate.

The fixture remains exactly one neutral technical record:

```text
goal6-event-001,goal6-entity-001,2026-08-13T12:00:00Z,synthetic-serving-increment,42.0
```

## Bundle boundary

The bundle job:

- inherits the existing workflow service principal;
- reuses the approved existing Serverless SQL Warehouse;
- creates no cluster or warehouse;
- sets `max_concurrent_runs: 1` and disables queueing;
- runs verification only after the apply task succeeds;
- reads only the Terraform-derived approved Goal 5 S3 fixture URI;
- contains no Doris command, endpoint, secret, DDL, or refresh operation.

## Offline validation

| Check | Result |
| --- | --- |
| Goal 6 static validator | PASS |
| Focused Goal 6 plus Goal 5 regression suite | PASS — 38 tests |
| Exact three-layer MERGE count and identities | PASS |
| Existing warehouse/no-new-compute contract | PASS |
| No executable Doris reference | PASS |
| Exact single-record fixture | PASS |
| `git diff --check` | PASS |

Two pytest cache warnings remain non-failing because the existing cache
directory is not writable.

## Reviewed hashes

- Goal 6 bundle resource:
  `b88d73b70b84a8b9044eeeb9a6341b0f55cd5ab449f2f4b5b3b5caf8c9ff9e70`;
- apply SQL:
  `4ac96983c0070172ce5286d021729d4e08baf804b92d667904f293eda204ad0d`;
- verify SQL:
  `42a06c10d5829ecdccfd163f47c49675e1b49d0685244db2952f47f0d2deefff`;
- fixture:
  `0aa72eb52cca111a326ffde8b838d63c3e690977c6bade5e0034babfa3960af1`;
- static validator:
  `4dc6b5f864790c00cd44ee19a5a622a603f6453f5ca84ee0e4bb2aea21840ee5`;
- static tests:
  `9218e33d841a1f655c4277645e0e1ff5e1e218cb57e29fa4e758b394b93b99cd`.

## Boundary

No connected bundle validation/deploy, Databricks job/SQL, table/data mutation,
Doris refresh, Terraform operation, AWS operation, or ECS task occurred.
Connected bundle validation, deployment, and the job run each require their
own later approval. The immediate next boundary remains the task-definition
saved Terraform plan.
