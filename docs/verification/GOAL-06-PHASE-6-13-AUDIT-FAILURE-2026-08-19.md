# Goal 6 Phase 6-13 audit verification — failed closed

Date: `2026-08-19`

Status: `FAIL — AUDIT ROW NOT FOUND; NO RETRY`

## Approved execution boundary

Exactly one private admin audit task was approved and launched from
`ask-david-development-doris-admin-refresh:15` with the exact prior result
query ID `5f3d5b10fd5b4a08-a24906b966376c6b`. The task was intended to read the
internal Doris audit log only. The fail-closed wrapper did not retry after the
task failed.

| Attribute | Result |
| --- | --- |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| Cluster / task definition | `ask-david-development-cluster` / admin-refresh `:15` |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/732ef6a88ea046388810c15f8f77244e` |
| Subnet / private IP | `subnet-0a1aad220d82ef879` / `10.42.38.69` |
| Security group | `sg-07a0dd2e8af8aa178` |
| Task status / exit code | `STOPPED` / `1` |
| Stop reason | `Essential container in task exited` |
| CloudWatch stream | `admin/doris-admin/732ef6a88ea046388810c15f8f77244e` |
| Wrapper result | `admin operation failed; no retry` |

## Connected failure evidence

The CloudWatch stream contains the expected MariaDB client deprecation and TLS
warnings, followed by the sanitized fail-closed marker:

```json
{"goal":"goal-06","operation":"audit-verify","status":"audit-row-not-found"}
```

The task therefore did not produce a valid audit correlation. This does not
prove that the query identity, target, state, duration, or workload-group
contract is present in the audit table. Phase 6-13 acceptance item 38 remains
**UNVERIFIED**.

## Root-cause boundary

The repository evidence proves only that the exact query ID was not found by
the audit runner's bounded lookup. It does not yet distinguish among audit-log
retention/timing, query-ID correlation semantics, or another Doris audit-table
condition. No connected diagnostic query, source change, or second task was
performed after the failure.

## Next checkpoint

Goal 6 remains **NOT VERIFIED**. Any remediation must first be reviewed offline
and then receive a separate approval before a new connected audit operation.
The failed task must not be retried implicitly.
