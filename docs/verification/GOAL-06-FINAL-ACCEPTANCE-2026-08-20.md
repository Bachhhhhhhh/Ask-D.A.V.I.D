# Goal 6 final acceptance evidence — 2026-08-20

## Scope and evidence boundary

This report closes the connected Goal 6 verification sequence for the approved
development environment. It does not apply or destroy infrastructure, run an
ECS task, run Doris SQL, mutate Databricks, or push an image.

Final connected zero-drift plan:

```text
TF_DATA_DIR=/tmp/goal6-connected-tfdata \
terraform -chdir=infrastructure/environments/development plan \
  -input=false -detailed-exitcode \
  -out=/tmp/goal6-final-post-rebuild-zero-drift-20260820.tfplan
```

| Evidence | Result |
| --- | --- |
| AWS account / region | PASS — `736956442295` / `ap-southeast-1` |
| Terraform version | `1.15.8` |
| Saved plan SHA-256 | `e520bdd87b083fc95aa5f97555f1b8825497926df3b387c5d62495a79e3e1497` |
| Plan resource changes | `261` total; all `no-op` |
| Creates / updates / replacements / destroys | `0 / 0 / 0 / 0` |
| Running ECS tasks after verification | `[]` |
| Project report | `GOAL-06-PHASE-6-10-READONLY-POST-REBUILD-2026-08-20.md` |

## Final acceptance matrix

| # | Criterion | Result | Durable evidence |
|---:|---|---|---|
| 1 | Goal 5 foundation remains healthy | PASS | Phase 6-9 increment evidence; final zero-drift plan |
| 2 | Approved AWS development account | PASS | STS identity and saved plan |
| 3 | AWS region is `ap-southeast-1` | PASS | STS/plan and all connected reports |
| 4 | Doris development deployment exists and is healthy | PASS | private readiness markers; successful verifier tasks |
| 5 | Deployment mode documented | PASS | Goal 6 plan and Doris runbook |
| 6 | Doris version documented | PASS | Goal 6 plan/runbook: pinned Doris `4.0.1` |
| 7 | No unintended public database/admin exposure | PASS | private SG/task evidence and Terraform plan |
| 8 | Valid private connected-verification path | PASS | private verifier task `a6bf93c1a8f74340915646413d8fcd16` |
| 9 | Verification does not depend on sandbox access to private Doris endpoints | PASS | repository ECS verifier wrapper |
| 10 | Verification infrastructure follows least privilege | PASS | verifier/admin SG, IAM, secret, and RBAC evidence |
| 11 | Doris connects to governed lakehouse integration | PASS | connected source refresh and verifier result |
| 12 | Unity Catalog remains governance authority | PASS | Phase 6-0 metastore preflight and Terraform state |
| 13 | No Glue/HMS competing authority | PASS | Goal 6 design and infrastructure inspection |
| 14 | Doris discovers only approved source objects | PASS | allowlist guard and refresh migration |
| 15 | Doris reads an approved source table | PASS | post-rebuild result contract |
| 16 | DELTA_UNIFORM_ICEBERG interoperability demonstrated | PASS | connected Doris query against approved Goal 5 source |
| 17 | Plain DELTA is not misreported as Iceberg-compatible | PASS | Goal 6 source-format preflight and static guards |
| 18 | Doris external-source identity is read-only | PASS | Terraform grants and Phase 6-11 RBAC evidence |
| 19 | No static AWS credential in Doris configuration | PASS | IAM/Secrets Manager design and source scan |
| 20 | No Doris write-back to authoritative lakehouse | PASS | source-to-serving-only refresh migration and task evidence |
| 21 | Neutral serving mart exists | PASS | `serving_metric_daily` and result contract |
| 22 | Representative result matches authoritative source | PASS | direct allowlisted source projection plus post-rebuild result comparison |
| 23 | Source provenance available | PASS | `source_dataset`/`source_table` fields in result contract |
| 24 | Doris refresh timestamp available | PASS | `refresh_timestamp` and `refreshed_at` fields |
| 25 | Full/initial refresh succeeds | PASS | post-rebuild admin refresh task `eb63cf05deb14c89bf3f84a855602994` |
| 26 | Minimal incremental refresh succeeds | PASS | Phase 6-9 controlled increment report |
| 27 | Incremental refresh does not duplicate data | PASS | Phase 6-9 deterministic verification |
| 28 | Refresh lag is observable | PASS | serving refresh state/freshness view and timestamps |
| 29 | Serving copy can be deleted and rebuilt | PASS | Phase 6-10 rebuild task `2551e7c4b51949b695bb23b0ee3dd1c5` |
| 30 | Rebuilt result matches expected authoritative result | PASS | post-rebuild comparison report |
| 31 | No pipeline uses Doris as rebuild source | PASS | version-controlled migration direction |
| 32 | Future Query Service Doris identity exists read-only | PASS | Terraform identity and grants |
| 33 | SELECT succeeds with read-only identity | PASS | Phase 6-11 positive SELECT |
| 34 | DML is rejected | PASS | Phase 6-11 INSERT/UPDATE/DELETE denials |
| 35 | DDL is rejected | PASS | Phase 6-11 CREATE/ALTER/DROP denials |
| 36 | Query/workload protection configured | PASS | `query_timeout=30` |
| 37 | Safe query-limit enforcement verified | PASS | Phase 6-12 bounded `SLEEP(31)` timeout |
| 38 | Query audit evidence exists | PASS | Phase 6-13 exact-ID audit after TCP/8040 remediation |
| 39 | Result contract contains all required fields | PASS | post-rebuild verifier JSON |
| 40 | Goal 8 Query Service not implemented | PASS | repository scope/static inspection |
| 41 | S3 + Iceberg-compatible lakehouse remain authoritative | PASS | Goal 5/6 source and refresh design |
| 42 | Doris remains disposable/rebuildable | PASS | Phase 6-10 controlled rebuild |
| 43 | No real Green SM data introduced | PASS | synthetic-source and scope guards |
| 44 | No Green SM-specific business logic introduced | PASS | neutral serving schema and scope review |
| 45 | No Goal 7+ implementation introduced | PASS | repository scope/static inspection |
| 46 | Accepted ADRs unchanged | PASS | no `docs/adr` diff |
| 47 | No secret/token/static credential/state/plan tracked | PASS | tracked-file scan; saved plan is `/tmp` only |
| 48 | Terraform has no unexpected drift | PASS | final plan SHA above; 261 no-op, zero actions |
| 49 | Ephemeral verification tasks stopped | PASS | ECS RUNNING list `[]` |
| 50 | Persistent/cost-bearing resources documented | PASS | Phase 6-14 inventory |
| 51 | `PROJECT_STATUS.md` reflects actual state | PASS | current snapshot and linked reports |
| 52 | Verification report exists and matches evidence | PASS | this report plus linked connected reports |

## Explicitly deferred

The optional 10-million-row benchmark, 20-user concurrency test, P95 release
gate, and production load testing remain **DEFERRED** and are not Goal 6
failures.

## Repository status note

The technical acceptance evidence is complete. This report is intentionally
commit-scoped separately from the status checkpoint; the status file will
reference its immutable evidence commit after that commit is created.
