# Goal 6 Phase 6-6 private verifier health — failed start and diagnosis

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **BLOCKED BEFORE CONTAINER START — NO RETRY**

## Approved execution

The project owner approved read-only preflight, exactly one Fargate task, and
immediate read-only ECS/ENI/CloudWatch inspection. The approved task used a
bounded, non-mutating MariaDB health ping; it did not authorize a retry,
serving query, admin refresh, SQL mutation, Terraform operation, ECR push, or
Databricks operation.

Preflight proved:

- AWS account `736956442295`, region `ap-southeast-1`;
- cluster `ask-david-development-cluster`;
- task definition
  `arn:aws:ecs:ap-southeast-1:736956442295:task-definition/ask-david-development-doris-verifier:7`,
  `ACTIVE`, Fargate `awsvpc`, `512` CPU / `1024` MiB;
- immutable image digest
  `sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6`;
- no verifier task was already running;
- both approved application subnets were available and had
  `MapPublicIpOnLaunch=false`;
- verifier SG `sg-04eb1ebf613ceeadc` was in the approved VPC;
- FE `i-0d7b971ba56dc2395` remained `ok/ok` with exactly one
  `doris-port-ready` marker on `9030`.

One `RunTask` call used fixed client token
`goal6-phase6-6-health-20260817-v1`. ECS returned exactly one task and no
launch-time failure:

```text
arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/f22d6afa1898454fa35ba670f9629253
```

The command override was limited to `/bin/sh -c` plus a 15-second
`mysqladmin --ssl --protocol=TCP` health ping to `DORIS_FE_HOST:9030` with a
five-second connection timeout.

## Private placement

The task ENI was `eni-0543caf7d0e865cb4`:

- subnet: `subnet-034f5f1c9bca753f1`;
- private IPv4: `10.42.22.243`;
- security group: `sg-04eb1ebf613ceeadc`;
- public association: none;
- requester-managed ECS ENI: true.

This proves the approved private placement and no-public-IP controls. It does
not prove FE reachability because the container never started.

## Terminal result

The single task reached:

```text
lastStatus=STOPPED
stopCode=TaskFailedToStart
container exit code=null
```

The sanitized stopped reason was a `ResourceInitializationError`: the ECS agent
timed out retrieving the exact Doris query secret from AWS Secrets Manager.
The task never reached `RUNNING`; the health-ping command did not execute. No
CloudWatch container stream exists, which is consistent with failure before
container start.

No retry or second task was launched.

## Deterministic read-only diagnosis

The Secrets Manager interface endpoint `vpce-06d9bb6fa72d0d334` is `available`,
has private DNS enabled, is present in both approved application subnets, and
uses endpoint SG `sg-09df4c29eba7991fa`.

The ECS execution role already has the required permissions:

- `secretsmanager:GetSecretValue` on exactly the three Goal 6 secret ARNs;
- `kms:Decrypt` on secrets KMS key
  `08669b8b-6cd9-49b3-a7d8-7e3b4c079752`.

The verifier SG has TCP `443` egress and private TCP `9030` egress to the FE
SG. The endpoint SG has TCP `443` ingress from the Goal 6 admin task SG,
workload SG, and Goal 3 smoke SG, but **not** from verifier SG
`sg-04eb1ebf613ceeadc`.

The missing verifier-SG-to-interface-endpoint-SG ingress is therefore the
deterministic network-policy blocker. The failure is not evidence of a Doris
listener regression, invalid secret, missing IAM permission, SQL failure, or
public-network requirement.

## Required remediation boundary

The minimum declarative remediation is one Terraform-managed TCP `443` ingress
rule on the existing AWS interface-endpoint SG, referencing only the existing
Goal 6 verifier SG. It must mirror the already-managed admin-task endpoint
rule; it must not add a CIDR, alter IAM/KMS/secrets, open Doris publicly, or
change task definitions.

Offline source/tests/docs remediation requires explicit approval. Any connected
plan, apply, or one-time task retry requires its own later approvals. Phase 6-6
remains unverified.

## Approved offline remediation

The project owner approved the minimum offline remediation on `2026-08-17`.
The repository now declares exactly one additional Terraform-managed rule:

- endpoint security group: existing AWS interface-endpoint SG only;
- source: existing Goal 6 verifier security group only;
- protocol and port: TCP `443` only;
- no CIDR ingress, no public exposure, and no IAM, KMS, secret, task-definition,
  ECS, Databricks, or AWS mutation.

Static validation and regression coverage must pass before a new saved
connected development plan is requested. The failed task is not retried by this
offline change; Phase 6-6 remains unverified until the reviewed plan is applied
and exactly one subsequently approved private verifier health task exits `0`.

The completed offline evidence is
[`GOAL-06-PRIVATE-VERIFIER-ENDPOINT-OFFLINE-2026-08-17.md`](GOAL-06-PRIVATE-VERIFIER-ENDPOINT-OFFLINE-2026-08-17.md).
