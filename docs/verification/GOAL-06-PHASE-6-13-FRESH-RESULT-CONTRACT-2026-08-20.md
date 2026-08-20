# Goal 6 Phase 6-13 fresh result contract — connected

Date: `2026-08-20`

Status: **PASS — ONE PRIVATE READ-ONLY RESULT CONTRACT; AUDIT TASK NOT RUN**

## Approved execution

Exactly one no-retry read-only verifier task ran from the applied revision `16`
using the audit-guard image. It performed the representative read-only Doris
query and emitted the complete result contract. No write, DDL, refresh,
Terraform, ECR, Databricks, or follow-on task occurred.

| Check | Result |
| --- | --- |
| AWS account / region | PASS — `736956442295` / `ap-southeast-1` |
| Cluster | `ask-david-development-cluster` |
| Task definition | `ask-david-development-doris-verifier:16` |
| Image | Exact ECR digest `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |
| Command | `/app/doris-readonly-verify` |
| Subnet / private IP | `subnet-0a1aad220d82ef879` / `10.42.33.239` |
| Security group | `sg-04eb1ebf613ceeadc` |
| Task ARN suffix | `c1f8d389320a4c55b7586d3f5cc78508` |
| Final status / exit code | `STOPPED` / `0` |

## Result contract

```json
{
  "source_dataset": "ask_david_development.green_sm_business.goal5_structured_business_metrics",
  "refresh_timestamp": "2026-08-19T17:05:08Z",
  "executed_query_id": "3688ae5f35c2439d-85b020ada4249d3e",
  "row_count": 3,
  "execution_duration": 0
}
```

The representative result included metric date `2026-02-01`, category `alpha`,
event count `1`, metric total `10.5`, and the same authoritative source table.
The task's completion marker was read from its single private CloudWatch log
stream and reported `operation=readonly-verify,status=completed`.

## Next boundary

The query ID above is the only ID authorized for the next audit correlation.
Phase 6-13 remains **UNVERIFIED** pending one separately approved private
admin audit task using exactly this query ID. No retry or audit task was run in
this checkpoint.
