# Goal 5 CDC SQL remediation

Date: 2026-08-13  
Scope: offline source, validator, regression-test, and documentation change
after workflow run `616649104578361`. No connected bundle validation/deploy,
SQL/job run, Terraform operation, AWS operation, retry, or Databricks mutation
was performed in this remediation checkpoint.

## Failure evidence

The approved one-time Goal 5 workflow used job `382877731318442` and run
`616649104578361` on Serverless SQL Warehouse `757e0335c6efb51e`. The
structured and document tasks succeeded; `ingest_cdc` failed with:

`[TABLE_OR_VIEW_NOT_FOUND] The table or view unique_events cannot be found`

The output and idempotency tasks were skipped upstream. The failure was caused
by a SQL scope error: the `unique_events` CTE was visible only to the first
`MERGE` statement in `04_ingest_cdc.sql`, but later independent `MERGE`
statements referenced it as though it were a persistent relation.

## Offline remediation

`04_ingest_cdc.sql` now creates the session-scoped temp view
`goal5_cdc_unique_events` from the existing deterministic source/read,
deduplication, ordering, and duplicate-count logic. All three downstream
`MERGE` statements read that view. No table schema, source path, IAM scope,
authorization model, or CDC semantics were changed.

The static validator requires the temp-view marker and its shared use. A
regression test asserts that all three independent reads use the materialized
view and that the original CTE name remains only inside its defining view.

## Validation contract

The required offline checks are:

- Goal 5 static validator;
- focused Goal 5 unit tests;
- Ruff lint and format check;
- mypy;
- Bandit and detect-secrets;
- `git diff --check`.

Terraform validation, connected bundle validation/deployment, SQL execution,
workflow retry, and any AWS/Databricks mutation remain out of scope. A fresh
strict connected bundle validation and a separately approved workflow retry
are required after offline validation passes.

## Offline validation result

| Check | Result |
| --- | --- |
| Goal 4 static validator | PASS |
| Goal 5 static validator | PASS |
| Full repository pytest suite | PASS — 123 tests |
| Ruff check | PASS |
| Ruff format check | PASS |
| Mypy | PASS — 13 source files |
| Bandit | PASS |
| Detect-secrets baseline hook | PASS |
| `git diff --check` | PASS |

The repository's `uv` launcher was unavailable in this environment; equivalent
installed virtual-environment binaries were invoked through the available
Python interpreter with cache paths outside the repository. No connected
command was substituted for an offline check.

The corrected local bundle source set (shared bundle YAML, both Goal 4/Goal 5
resource manifests, and the 19 top-level Goal 4/Goal 5 SQL files; sorted
repository-relative path, NUL separators, raw bytes) has aggregate SHA-256:

`bd4cd49ee07147f9f240a10b936c78dad76b9dca62622b10f0fb62f6318eb3cd`

The corrected CDC SQL byte hash is
`9ce80b73ec48bf0a7568fad81faf791f286dbfbae4c66ca0a9af84fe013f66fd`.

## Current result

This report intentionally does not claim Goal 5 verification. The connected
CDC flow, output assertions, idempotency behavior, provenance, quality results,
and authoritative Tables API evidence remain unverified until the approved
post-remediation checkpoints complete.

## Next approval boundary

Run exactly one strict connected bundle validation for the corrected source
aggregate above, target `development`, profile `ask-david-development`, with
the reviewed Terraform-derived variables and no `workspace_host`. Do not
deploy, run SQL/jobs, mutate tables, create compute, or perform Terraform/AWS
operations. Stop immediately on any warning or error. A separate approval is
required for redeployment and then for a single CDC workflow retry.
