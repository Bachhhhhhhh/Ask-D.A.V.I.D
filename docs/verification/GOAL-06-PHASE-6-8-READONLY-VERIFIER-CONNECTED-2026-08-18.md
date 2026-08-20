# Goal 6 Phase 6-8 read-only verifier — connected evidence

Date: `2026-08-18`
Environment: development only
Status: **PASS — EXACTLY ONE READ-ONLY TASK**

## Approved execution

The approved task used:

- family/revision: `ask-david-development-doris-verifier:9`;
- image digest:
  `sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510`;
- ECS cluster: `ask-david-development-cluster`;
- allowed private application subnets:
  `subnet-034f5f1c9bca753f1`, `subnet-0a1aad220d82ef879`;
- verifier security group: `sg-04eb1ebf613ceeadc`;
- public IP assignment: `DISABLED`;
- FE endpoint: `10.42.64.238:9030` over TLS.

Read-only pre-run inspection confirmed AWS account `736956442295`, the
approved `ap-southeast-1` region, revision `9` ACTIVE, exact image digest,
Fargate `512` CPU/`1024` MiB with `awsvpc`, and no pre-existing RUNNING
verifier task.

## Task evidence

| Item | Result |
| --- | --- |
| ECS task | PASS — `dd97ba3989a24d40b19ee08df5c98b2a` |
| Task definition | PASS — `ask-david-development-doris-verifier:9` |
| Network | PASS — private subnet `subnet-034f5f1c9bca753f1`, private IP `10.42.28.73`, no public IP |
| Container result | PASS — exit code `0`, `EssentialContainerExited` after normal completion |
| Retry | PASS — none |
| Post-run task state | PASS — no RUNNING verifier task |
| CloudWatch stream | PASS — `verifier/doris-verifier/dd97ba3989a24d40b19ee08df5c98b2a` |

The Fargate attachment reported ENI `eni-0b7ea6c40c29060d9` with status
`DELETED` after stop. This is expected for an ephemeral `awsvpc` task; the ECS
attachment remains the durable private-network evidence.

## Completed result contract

The only `readonly-verify` CloudWatch record has `status: completed` and proves
all required fields without exposing the query secret:

```json
{
  "source_dataset": "ask_david_development.green_sm_business.goal5_structured_business_metrics",
  "query_result": {
    "metric_date": "2026-02-01",
    "category": "alpha",
    "event_count": 1,
    "metric_total": 10.5
  },
  "refresh_timestamp": "2026-08-18T09:57:32Z",
  "executed_query_id": "931a5b1976c644fb-b45ea15940521bfd",
  "row_count": 2,
  "execution_duration": 0
}
```

The full record also identifies the stored source-table provenance and source
transformation timestamp. The verifier connected through the dedicated
query-only Doris identity and performed no DDL, DML, refresh, Terraform, ECR,
Databricks, or AWS resource mutation. The authoritative lakehouse was not
modified.

## Acceptance impact

This task provides connected evidence for:

- private verification-path execution without Codex direct TCP access;
- successful TLS read-only serving query;
- read-only identity SELECT success;
- a neutral serving result with source provenance and refresh time;
- query ID, row count, and execution-duration result-contract fields;
- stopped ephemeral verification task.

It does **not** prove RBAC denials, query-timeout enforcement, audit-log
correlation, incremental refresh, or serving-copy rebuild. Each remains a
separate approved execution boundary.
