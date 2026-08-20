# Goal 6 post-rebuild read-only result comparison — 2026-08-20

## Approval and execution boundary

The user approved exactly one private, no-retry read-only verifier task after
the Phase 6-10 disposable serving-copy rebuild and the post-rebuild admin
refresh. The repository wrapper validated the account, task definition,
digest-pinned image, private subnets, verifier security group, and FE target
before launch. No retry, write/DDL, Terraform, ECR, Databricks, or unrelated
AWS operation was performed.

| Check | Result |
| --- | --- |
| AWS account / region | PASS — `736956442295` / `ap-southeast-1` |
| Cluster | `ask-david-development-cluster` |
| Task definition | `ask-david-development-doris-verifier:16` |
| Image | `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |
| Command | `/app/doris-readonly-verify` |
| Private subnet / task address | `subnet-0a1aad220d82ef879` / `10.42.42.187` |
| Security group | `sg-04eb1ebf613ceeadc` |
| Task ARN suffix | `a6bf93c1a8f74340915646413d8fcd16` |
| Final status / exit code | `STOPPED` / `0` |
| CloudWatch stream | `verifier/doris-verifier/a6bf93c1a8f74340915646413d8fcd16` |

## Result contract

The single CloudWatch stream emitted the following completed contract:

```json
{
  "source_dataset": "ask_david_development.green_sm_business.goal5_structured_business_metrics",
  "refresh_timestamp": "2026-08-20T07:05:13Z",
  "executed_query_id": "cdeff0f1ea78492e-867402ae1eb1156d",
  "row_count": 3,
  "execution_duration": 0,
  "query_result": {
    "metric_date": "2026-02-01",
    "category": "alpha",
    "event_count": 1,
    "metric_total": 10.5,
    "source_table": "ask_david_development.green_sm_business.goal5_structured_business_metrics",
    "source_transformed_at": "2026-08-13T04:24:56Z",
    "refreshed_at": "2026-08-20T07:05:13Z"
  }
}
```

## Post-rebuild comparison

The post-rebuild admin refresh executed the version-controlled
`doris/migrations/02_refresh_from_unity_catalog.sql.tmpl` path. That migration
reads only the allowlisted Unity Catalog source and directly projects its
`metric_date`, `category`, `event_count`, `metric_total`, and `transformed_at`
columns into the disposable Doris serving table; it also records the same
source dataset and refresh state. The verifier then read the rebuilt serving
copy and observed:

| Comparison | Result |
| --- | --- |
| Authoritative source dataset | **PASS** — exact allowlisted Goal 5 table |
| Representative date/category | **PASS** — `2026-02-01` / `alpha` |
| Representative event count/metric total | **PASS** — `1` / `10.5` |
| Rebuilt serving row count | **PASS** — `3` |
| Source transformation timestamp | **PASS** — `2026-08-13T04:24:56Z` carried from source |
| Refresh/freshness timestamp | **PASS** — `2026-08-20T07:05:13Z`, after rebuild refresh |
| Source write-back | **PASS** — refresh path is source-to-serving only |

The observed values are the direct projection of the authoritative source
through the approved refresh migration, not a Doris-to-lakehouse write-back.
The task emitted no secret or credential values and no Goal 7+ behavior.

## Acceptance conclusion

**PASS — post-rebuild read-only result contract and controlled source/result
comparison.** Phase 6-10 now has execution, refresh, rebuild, and result
evidence. A new final connected Phase 6-14 zero-drift/cleanup plan is still a
separate approval boundary and has not been created or run.
