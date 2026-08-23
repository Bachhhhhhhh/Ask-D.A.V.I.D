# Goal 7 indexer task failure — 2026-08-21

## Status

**TASK FAILED TO START — NO RETRY**

After the Databricks profile was reauthenticated, the approved read-only
readiness checks passed and exactly one private indexer task was submitted.
The task failed before its container started while ECS tried to fetch the
workflow OAuth secret from Secrets Manager.

## Task evidence

- cluster: `ask-david-development-cluster`
- task definition: `ask-david-development-goal7-indexer:1`
- task ARN:
  `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/3f3d764bc5d94ec29e4e3f5d945d6112`
- network: private application subnets, workload SG
  `sg-0a22126b47d3a5aea`, `assignPublicIp=DISABLED`
- final status: `STOPPED`
- stop code: `TaskFailedToStart`
- container started: **NO** (`StartedAt` was null)
- exit code: **NONE**
- log stream: **NONE**

The recorded stop reason was:

```text
ResourceInitializationError: unable to pull secrets or registry auth:
unable to retrieve secret from Secrets Manager: connection issue between the
task and AWS Secrets Manager ... context deadline exceeded
```

No task retry, AOSS index mutation, Databricks SQL execution, Terraform
operation, or additional AWS mutation was performed.

## Connected network evidence

- Secrets Manager interface endpoint `vpce-06d9bb6fa72d0d334`: `available`,
  private DNS enabled, in both application subnets.
- Endpoint SG `sg-09df4c29eba7991fa`: TCP/443 ingress from workload SG exists
  (`sgr-0a6582981c3911ad6`).
- Workload SG `sg-0a22126b47d3a5aea`: `IpPermissionsEgress=[]`.

Therefore the direct, deterministic blocker is the missing workload-to-endpoint
TCP/443 egress rule. The endpoint-side ingress alone cannot permit the task's
Secrets Manager connection.

## Minimal remediation proposal

Add one Terraform-managed TCP/443 egress rule from the existing Goal 7
workload SG to the existing AWS interface-endpoint SG. Keep the rule
security-group scoped; do not use a public CIDR, do not broaden endpoint
ingress, and do not rerun the task until a new saved development plan is
reviewed and separately approved.

The source/tests/docs change and its offline validation require a separate
approval. The failed task approval is exhausted and must not be reused for a
retry.
