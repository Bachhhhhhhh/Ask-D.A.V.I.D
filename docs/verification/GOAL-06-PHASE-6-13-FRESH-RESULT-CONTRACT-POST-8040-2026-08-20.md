# Goal 6 Phase 6-13 post-8040 fresh result contract — connected

Date: `2026-08-20`

Status: **PASS — ONE FRESH PRIVATE RESULT CONTRACT; AUDIT CORRELATION PENDING**

## Execution

Exactly one fresh private read-only verifier task ran after the TCP/8040
remediation. The wrapper validated the approved task definition/image/network
contract and did not retry.

| Check | Result |
| --- | --- |
| AWS account / region | PASS — `736956442295` / `ap-southeast-1` |
| Cluster | `ask-david-development-cluster` |
| Task definition | `ask-david-development-doris-verifier:16` |
| Image | `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |
| Subnet / private IP | `subnet-034f5f1c9bca753f1` / `10.42.31.36` |
| Security group | `sg-04eb1ebf613ceeadc` |
| Task ARN suffix | `1e11364f52704152b4d3df1d596bfbd3` |
| Started at | `2026-08-20T05:04:20Z` |
| Final status / exit code | `STOPPED` / `0` |

## Result contract

```json
{
  "source_dataset": "ask_david_development.green_sm_business.goal5_structured_business_metrics",
  "refresh_timestamp": "2026-08-19T17:05:08Z",
  "executed_query_id": "71e250e78c514a31-8551296f735d0a9a",
  "row_count": 3,
  "execution_duration": 0
}
```

CloudWatch emitted `operation=readonly-verify,status=completed` on exactly one
private verifier stream. The fresh query ID was created after the 8040 rules
were applied, unlike the stale ID used by the earlier failed audit attempt.

## Checkpoint

The post-remediation result-contract prerequisite is PASS. Phase 6-13 remains
**UNVERIFIED** until a separately approved, exactly one-shot admin audit task
correlates this new query ID. No audit task, retry, SQL mutation, Terraform,
Databricks, ECR, or unrelated AWS operation occurred in this checkpoint.
