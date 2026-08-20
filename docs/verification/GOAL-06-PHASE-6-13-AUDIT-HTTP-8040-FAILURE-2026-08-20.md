# Goal 6 Phase 6-13 audit after HTTP/8040 remediation — failed closed

Date: `2026-08-20`

Status: **UNVERIFIED — ONE AUDIT EXECUTION FAILED CLOSED**

## Approved execution

The approved audit wrapper was run exactly once after the TCP/8040 SG rules
were applied. It used the previously approved fresh result-contract query ID
and did not retry after failure.

| Check | Result |
| --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| Cluster | `ask-david-development-cluster` |
| Task definition | `ask-david-development-doris-admin-refresh:16` |
| Image digest | `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |
| Expected query ID | `3688ae5f35c2439d-85b020ada4249d3e` |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/3b4c907bf41f45a39868728e7c5f4ef4` |
| Private subnet / IP | `subnet-034f5f1c9bca753f1` / `10.42.30.72` |
| Final state / exit code | `STOPPED` / `1` |
| Stop reason | `Essential container in task exited` |

## CloudWatch evidence

The single task log stream was:

`/ask-david-development/doris :: admin/doris-admin/3b4c907bf41f45a39868728e7c5f4ef4`

It emitted exactly:

```json
{"goal":"goal-06","operation":"audit-verify","status":"audit-log-empty"}
```

The wrapper therefore failed closed before asserting an audit row. The exact
query-ID contract remains unproven. No retry, SQL mutation, Terraform,
Databricks, ECR, or unrelated AWS operation occurred.

## Checkpoint

The TCP/8040 SG remediation was applied successfully, but this single audit
execution still produced an empty `internal.__internal_schema.audit_log`.
Phase 6-13 remains **UNVERIFIED**. Further remediation requires a new offline
root-cause analysis and separate approvals; this failure does not authorize an
implicit retry.
