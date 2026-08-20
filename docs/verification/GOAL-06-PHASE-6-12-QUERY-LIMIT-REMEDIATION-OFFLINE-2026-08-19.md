# Goal 6 Phase 6-12 query-limit verifier remediation — offline

Date: `2026-08-19`

Status: `OFFLINE REMEDIATION COMPLETE — CONNECTED RETRY REQUIRED`

## Failure evidence

The separately approved, exactly-one Phase 6-12 task was task
`ceacc0d27ef348ff84f31af8736be2f6`, using verifier revision `14` and the
reviewed immutable image. It ran privately in
`subnet-0a1aad220d82ef879` at `10.42.36.73`, then stopped with exit code `1`.
The wrapper did not retry. CloudWatch returned:

```text
SHOW PROPERTY FOR 'doris_goal6_query' LIKE 'query_timeout'
ERROR 1105 (HY000) at line 1: errCode = 2, detailMessage = Access denied; you need (at least one of) the (GRANT) privilege(s) for this operation
{"goal":"goal-06","operation":"query-limit-verify","status":"query-timeout-property-mismatch"}
```

This is a verifier-contract failure, not evidence that the timeout is absent.
The query identity is intentionally not granted global `GRANT_PRIV` merely to
inspect another user's properties.

## Root cause and minimal correction

Apache Doris permits a user to inspect its own properties with
`SHOW PROPERTY LIKE`, while `SHOW PROPERTY FOR <user>` requires grant-level
visibility for another identity. The runner already authenticates as the
query identity, so the minimal correction is to replace only the property
inspection statement with:

```sql
SHOW PROPERTY LIKE 'query_timeout';
```

The bounded `SELECT SLEEP(31)` enforcement probe, 40-second outer bound,
duration guard, timeout/cancellation classifier, read-only secret boundary,
task wrapper, and no-retry behavior are unchanged.

## Changed files

- `docker/doris-verifier/doris-query-limit-verify`
- `scripts/validate_goal6.py`
- `tests/unit/test_goal6_static.py`
- `docs/runbooks/GOAL-06-DORIS.md`
- `docs/verification/GOAL-06-LATER-PHASE-VERIFIERS-OFFLINE-2026-08-18.md`

No Terraform, AWS, ECR, ECS, Databricks, SQL/job, or cloud mutation was run for
this remediation. No credentials, task-definition, image, or ignored tfvars
were changed.

## Offline validation required

- POSIX shell parse of the fixed runner;
- `scripts/validate_goal6.py`;
- focused Goal 6 unit tests, including the mocked query-timeout contract;
- repository diff/secret checks.

Connected evidence remains **UNVERIFIED** until a newly reviewed image/task
revision runs exactly once through the existing no-retry wrapper and proves
both the current-user property check and timeout/cancellation behavior.

Primary contract reference:
<https://doris.apache.org/docs/dev/sql-manual/sql-statements/account-management/SHOW-PROPERTY/>
