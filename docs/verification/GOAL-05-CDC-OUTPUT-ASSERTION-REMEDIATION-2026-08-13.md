# Goal 5 CDC output assertion remediation

Date: 2026-08-13  
Scope: approved offline-only correction after workflow run `149148676670509`.
No connected bundle validation/deployment, job/SQL execution, table/data
mutation, Terraform operation, AWS operation, or Databricks operation occurred
in this checkpoint.

## Failure evidence

The one approved corrected workflow retry reached `SUCCESS` for table creation
and all three ingestion tasks, including `ingest_cdc`. Its read-only output
verification task failed with:

```text
[USER_RAISED_EXCEPTION] CDC current state must reflect UPDATE and DELETE tombstone semantics
```

The source contract declares `payload.metric_value` as `DOUBLE`. The original
read-only assertion instead compared the JSON-extracted value to the literal
text `'120'`. Serializing a double as `120.0` is semantically equivalent but
causes that text comparison to fail.

## Correction

`05_verify_goal5_outputs.sql` now evaluates the current-state metric with:

```sql
TRY_CAST(get_json_object(payload_json, '$.metric_value') AS DOUBLE) = CAST(120 AS DOUBLE)
```

The assertion still requires exactly one non-deleted `entity-001` UPDATE
current state with metric value 120 and exactly one `entity-002` DELETE
tombstone. It changes only verification interpretation; it does not alter CDC
input, deduplication, ordering, merge logic, table definitions, data,
permissions, or infrastructure.

The static validator and regression test now fail closed if the numeric cast,
tombstone assertion, or protection against the brittle text comparison is
removed.

## Required offline validation

The approved full offline suite passed:

| Check | Result |
| --- | --- |
| Goal 4 static validation | PASS |
| Goal 5 static validation | PASS |
| Pytest | PASS — 124 tests, 97.15% coverage |
| Ruff check | PASS |
| Ruff format check | PASS |
| Mypy | PASS — 13 source files |
| Bandit | PASS |
| Detect-secrets baseline hook | PASS |
| `git diff --check` | PASS |

The repository's `uv` launcher was unavailable in the current shell. The
equivalent installed virtual-environment tools were invoked through
`/usr/bin/python3.12`, with tool caches and coverage output placed under
`/tmp`; no connected command substituted for an offline check.

The corrected shared bundle source aggregate (shared bundle YAML, both resource
manifests, and all 19 top-level Goal 4/Goal 5 SQL files, sorted by repository
relative path with NUL separators and raw bytes) is:

`e06e5e26ac83aa0ea30c93f12b747686cef67e3d80f9cb862998f931477dd507`

The corrected output-verification SQL hash is:

`594824b4b647de6451cf57fdd83bf927137a4122f4b0010aff09042b7596cb30`

## Next approval boundary

After offline validation and review pass, run exactly one fresh strict
connected bundle validation for the exact corrected source aggregate. Do not
deploy or run a workflow at that checkpoint. A separate approval is required
for redeployment and a subsequent single workflow retry.
