# Goal 7 Databricks embedding-response offline remediation — 2026-08-21

## Approved boundary

This checkpoint was approved for source, regression-test, and documentation
changes plus offline validation only. No Databricks or AWS call, image
build/push, ignored Terraform-input update, Terraform plan/apply/destroy,
bundle operation, SQL/job execution, or ECS task retry was performed.

## Failure contract

The one approved private Goal 7 indexer revision-4 task stopped with exit code
`1` after entering `DatabricksSqlClient.query_embedding()`. Its bounded
CloudWatch output contained:

`RuntimeError: Databricks query embedding response was invalid`

The task did not persist the raw Statements API response before the exception,
so the exact live response body cannot be independently reconstructed from the
repository. The checked-in code expects one SQL row with an `embedding` value
that is a Python list. Databricks SQL Statements API `INLINE` results can
serialize SQL `ARRAY` values as JSON-array strings, which is the deterministic
offline contract mismatch addressed here. Other response shapes remain
fail-closed.

## Remediation implemented

`DatabricksSqlClient.statement()` now validates result/status/schema shapes and
emits bounded, non-secret diagnostics containing only HTTP status, statement
state, whitelisted error fields, row/column counts, and column names. It never
logs OAuth credentials, raw response bodies, SQL result contents, or vectors.

`query_embedding()` now:

1. requires exactly one result row;
2. decodes a JSON-array string when the SQL result serializes `ARRAY<FLOAT>` as
   text;
3. accepts a native list when the client already decoded the array;
4. converts numeric values to floats and rejects non-numeric values; and
5. applies the existing canonical `databricks-gte-large-en` 1024-dimension
   validation.

Invalid row counts, null/dict/prediction-shaped values, malformed JSON strings,
and dimension mismatches remain errors with bounded diagnostics.

## Offline verification

| Check | Result |
| --- | --- |
| Goal 7 static validator | PASS — `python3 scripts/validate_goal7.py` |
| Focused Goal 7 tests | PASS — 26 passed |
| Python compilation | PASS — `python3 -m compileall -q ...` |
| `git diff --check` | PASS |
| Ruff lint/format | UNVERIFIED — `ruff` is not installed in this environment |
| Full repository unit suite | UNVERIFIED — optional `pydantic` is not installed |
| Databricks/AWS connected operation | NOT RUN — prohibited at this boundary |

## Current checkpoint

Goal 7 remains **UNVERIFIED**. The response-shape remediation is offline
validated, but the exact live response body and corrected connected runtime
behavior remain unverified. A separate approval is required before building or
promoting an image, creating a digest-bound task-definition plan, or running
one no-retry private task.
