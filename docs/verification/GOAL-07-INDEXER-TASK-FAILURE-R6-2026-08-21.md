# Goal 7 private indexer task failure R6 — 2026-08-21

## Approved boundary

Exactly one private ECS task was approved from
`ask-david-development-goal7-indexer:4`, with no retry. After failure, only
immediate read-only ECS, ENI, and CloudWatch inspection was performed. No new
task, Terraform operation, ECR operation, Databricks operation, or deliberate
AOSS inspection was performed after the failure.

## Task and network evidence

| Attribute | Result |
| --- | --- |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/fba432d4fafe4a3b900b1f01adf92e57` |
| Task definition | `ask-david-development-goal7-indexer:4` |
| Image digest | `sha256:bd3b9f2afd102cf165ee6b303fd973b228233d72406967d81c3b616e2f350b5e` |
| Cluster | `ask-david-development-cluster` |
| Subnet / private IP | `subnet-034f5f1c9bca753f1` / `10.42.17.247` |
| ENI / SG | `eni-05c966e4494822350` / `sg-0ff2bcb1d5175c931` |
| Public IP | Disabled; subnet does not map public IPs |
| Started / stopped | `2026-08-21T10:00:32.660000+07:00` / `2026-08-21T10:01:09.910000+07:00` |
| Container exit | `1`, `EssentialContainerExited` |
| Running/retried tasks | `[]` |

The task ENI was deleted by ECS after stop; a read-only lookup returned
`InvalidNetworkInterfaceID.NotFound`.

## Failure evidence

CloudWatch stream:
`goal7-indexer/goal7-indexer/fba432d4fafe4a3b900b1f01adf92e57`

The bounded log contains:

`RuntimeError: Databricks query embedding response was invalid`

The failure occurred in `DatabricksSqlClient.query_embedding()` after the
statement response failed the current contract (`exactly one row` whose
`embedding` value is a list). It is not evidence of an AOSS HTTP rejection.

## Important mutation boundary

The checked-in `main()` sequence calls `aoss.ensure_index()` and
`aoss.bulk_upsert()` before `sql.query_embedding()`. Therefore this task may
have created/updated the synthetic AOSS index before the embedding-response
failure. The failure log does not prove the AOSS write result, and no
post-failure AOSS inspection was run under the approved stop condition. AOSS
index/write/search acceptance remains UNVERIFIED.

## Current checkpoint

Goal 7 remains **UNVERIFIED / STOPPED FOR OFFLINE DATABRICKS EMBEDDING-RESPONSE
ANALYSIS**. No retry is authorized. The next step requires offline analysis of
the Databricks SQL Statements API result shape and a reviewed source/test/
documentation remediation before any new image, task-definition plan, or
connected task execution.
