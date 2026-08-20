# Goal 6 Phase 6-13 fresh result contract — connected

Date: `2026-08-19`

Status: `PASS — FRESH QUERY ID CAPTURED; AUDIT CORRELATION PENDING`

## Approved execution

Exactly one fresh private read-only result-contract task ran from verifier
revision `15` using the approved immutable image. The fail-closed wrapper
performed the task-definition, account, private-network, exit-code, and
CloudWatch checks and did not retry.

| Attribute | Result |
| --- | --- |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| Cluster / task definition | `ask-david-development-cluster` / verifier `:15` |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/84dec5db995f4e61811b57df5e180f20` |
| Subnet / private IP | `subnet-0a1aad220d82ef879` / `10.42.32.225` |
| Security group | `sg-04eb1ebf613ceeadc` |
| Task status / exit code | `STOPPED` / `0` |
| CloudWatch stream | `verifier/doris-verifier/84dec5db995f4e61811b57df5e180f20` |

## Result contract

| Field | Value |
| --- | --- |
| Source dataset | `ask_david_development.green_sm_business.goal5_structured_business_metrics` |
| Executed query ID | `2259b82920f9455a-a1845feae8876892` |
| Refresh timestamp | `2026-08-19T15:34:37Z` |
| Row count | `3` |
| Execution duration | `0` |
| Representative result | `2026-02-01`, `alpha`, event count `1`, metric total `10.5` |

The task was read-only and did not perform DDL, DML, refresh, rebuild, or
source write-back. This fresh query ID is the only ID approved for the next
audit correlation attempt; the earlier stale ID must not be reused.

## Checkpoint

The fresh result contract is **PASS**, but Phase 6-13 remains **UNVERIFIED**
until a separately approved private admin audit task correlates query ID
`2259b82920f9455a-a1845feae8876892` with identity, target, successful state,
duration, and `goal6_readonly` workload evidence.
