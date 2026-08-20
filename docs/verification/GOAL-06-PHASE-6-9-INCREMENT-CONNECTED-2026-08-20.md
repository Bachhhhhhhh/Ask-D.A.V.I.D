# Goal 6 Phase 6-9 controlled increment — connected evidence

Evidence review date: `2026-08-20`

Status: `PASS — OBSERVED CONNECTED DEPLOYMENT AND ONE SUCCESSFUL RUN`

## Evidence boundary

The deployment and run below were already present in the approved development
workspace before this read-only review. This turn did not deploy the bundle,
start a job, execute SQL, or mutate Databricks/AWS. The evidence is recorded
from read-only Databricks CLI inspection and is not attributed as a new
execution by this review.

## Bundle and job

| Check | Result |
| --- | --- |
| Workspace/profile | PASS — workspace `7474644358733471`, profile `ask-david-development` |
| Job | PASS — `ask-david-development-goal6-controlled-increment`, ID `227623174725080` |
| Run-as | PASS — workflow service principal `b2bdec62-62db-432d-bc6f-1f92b78053b0` |
| Warehouse | PASS — existing Serverless Small/PRO warehouse `757e0335c6efb51e`, auto-stop 10 minutes |
| Tasks | PASS — exactly `apply_controlled_increment` and `verify_controlled_increment` |
| Concurrency | PASS — `max_concurrent_runs=1`, queue disabled |
| Additional compute | PASS — no cluster specification; both SQL tasks bind the existing warehouse |

The job's workspace paths are:

```text
/Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development/files/sql/goal_06/01_apply_controlled_increment.sql
/Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development/files/sql/goal_06/02_verify_controlled_increment.sql
```

Read-only workspace export matched both deployed files byte-for-byte with the
reviewed repository source:

| Source | SHA-256 |
| --- | --- |
| `01_apply_controlled_increment.sql` | `4ac96983c0070172ce5286d021729d4e08baf804b92d667904f293eda204ad0d` |
| `02_verify_controlled_increment.sql` | `42a06c10d5829ecdccfd163f47c49675e1b49d0685244db2952f47f0d2deefff` |

## One-shot run

Read-only `jobs list-runs` returned exactly one run for the job:

| Check | Result |
| --- | --- |
| Run ID | `438156863255366` |
| Trigger | `ONE_TIME` |
| Lifecycle/result | `TERMINATED / SUCCESS` |
| Repair history | `null` — no repair/retry |
| Apply task | `114162201930272`, `TERMINATED / SUCCESS` |
| Verify task | `971139018313326`, `TERMINATED / SUCCESS` |
| Run interval | `2026-08-19T15:24:55Z` → `2026-08-19T15:25:29Z` |

The verification SQL contains the deterministic assertions audited in the
offline contract report: exactly one record at Raw, exactly one quality-PASS
record at Curated, and one Business aggregate with total `42.0`. Its task
finished successfully. The SQL source contains no Doris endpoint, secret,
DDL/DML outside the governed Goal 5 layer, or refresh operation; Doris refresh
remains a separately approved step after this authoritative increment.

## Conclusion and boundary

Phase 6-9 controlled increment acceptance is **PASS**: the reviewed source was
validated and the existing deployment/run provide one successful, idempotent,
governed Raw → Curated → Business increment with no retry or new compute.

This does not claim Goal 6 complete. A separately approved Doris refresh and
comparison, the Phase 6-10 disposable serving-copy rebuild if required, and
Phase 6-14 zero-drift/cleanup evidence remain outstanding.
