# Goal 7 integrated demo retry R2 — Doris connectivity failure — 2026-08-22

## Approved boundary

Exactly one private integrated-demo task was run from task definition revision
2, with no command override and no retry. After it stopped, only ECS/ENI and
CloudWatch read-only inspection was performed. No Terraform, ECR, Databricks,
SQL, AOSS, or other AWS mutation was performed.

## Task evidence

| Field | Result |
| --- | --- |
| Account / region | `736956442295` / `ap-southeast-1` |
| Task ARN suffix | `112cf69010874141a6ea07f2a066b8e5` |
| Task definition | `ask-david-development-goal7-integrated-demo:2` |
| Subnet / ENI / private IP | `subnet-034f5f1c9bca753f1` / `eni-0b68d91905d62b17b` / `10.42.20.44` |
| Public IP | Disabled |
| Container exit code | `1` |
| Failure stage | `structured_data_agent` / Doris Query Service |

## Failure evidence

CloudWatch reported:

`pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on '10.42.64.238' (timed out)")`

The integrated graph stopped before the RAG and Analytics agents. This is a
Doris FE TCP/9030 reachability failure, not evidence of a Databricks or AOSS
failure for this run.

## Current checkpoint

The dedicated indexer path is PASS, but integrated Goal 7 remains UNVERIFIED.
The Terraform source contains paired Goal 7 TCP/9030 SG ingress and egress
rules; live network/listener state must be inspected read-only before proposing
any remediation. Do not retry the integrated task until that review is
complete.
