# Goal 6 Phase 6-13 fresh-ID audit — failed closed

Date: `2026-08-19`

Status: `FAIL — FRESH QUERY ID STILL NOT FOUND; NO RETRY`

## Approved execution

Exactly one private admin audit task was run from revision `15` with the fresh
result-contract query ID `2259b82920f9455a-a1845feae8876892`. The fail-closed
wrapper performed its task-definition, account, private-network, exit-code,
and CloudWatch checks and did not retry.

| Attribute | Result |
| --- | --- |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| Cluster / task definition | `ask-david-development-cluster` / admin-refresh `:15` |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/ff6cdedf3a7c43038568c5c03544d5e3` |
| Subnet / private IP | `subnet-034f5f1c9bca753f1` / `10.42.16.113` |
| Security group | `sg-07a0dd2e8af8aa178` |
| Task status / exit code | `STOPPED` / `1` |
| Stop reason | `Essential container in task exited` |
| CloudWatch stream | `admin/doris-admin/ff6cdedf3a7c43038568c5c03544d5e3` |
| Expected query ID | `2259b82920f9455a-a1845feae8876892` |
| Wrapper result | `admin operation failed; no retry` |

## Connected failure evidence

The CloudWatch stream contains the sanitized marker:

```json
{"goal":"goal-06","operation":"audit-verify","status":"audit-row-not-found"}
```

The same failure with a fresh query ID rejects the initial
retention/timing-only hypothesis. It still does not identify whether the
remaining issue is query-ID semantics, audit plugin/table behavior, target
statement matching, or another Doris configuration condition.

## Checkpoint

Phase 6-13 remains **UNVERIFIED**. No further connected task is authorized by
this evidence. A new offline source/design review is required before changing
the audit runner or broadening any privilege. No source, Terraform, ECR,
Databricks, or other AWS operation occurred after the failed task.
