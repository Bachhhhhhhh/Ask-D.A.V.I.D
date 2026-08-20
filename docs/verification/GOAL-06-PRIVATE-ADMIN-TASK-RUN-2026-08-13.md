# Goal 6 private admin-refresh task run — blocked at startup

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Task definition: `ask-david-development-doris-admin-refresh:2`
Image: `sha256:41095093cb0cc820eb8b15afedacf97333ba443de8216de9dc40b950becee57d`

## Approved execution

One task was launched with the approved private execution parameters:

- cluster: `ask-david-development-cluster`;
- subnet: `subnet-034f5f1c9bca753f1` (private application subnet);
- security group: `sg-07a0dd2e8af8aa178` (Goal 6 admin task);
- `assignPublicIp=DISABLED`;
- no second launch or retry.

The host has no PowerShell runtime, so the repository PowerShell wrapper could
not be invoked directly. Its account, region, task-definition revision/digest,
Fargate shape, private subnet/security-group, and no-retry guards were
reproduced by read-only checks before issuing the single approved ECS control-
plane request. This execution limitation is recorded explicitly; it is not
treated as a successful wrapper execution.

Task ARN:
`arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/9b65be0a69354aa2b602b46b6696da0c`

## Result

The task reached `STOPPED` with `stopCode=TaskFailedToStart` and did not start
the container:

```text
ResourceInitializationError: unable to pull secrets or registry auth:
unable to retrieve secret from asm: There is a connection issue between the
task and AWS Secrets Manager ... context deadline exceeded
```

The ECS attachment confirms the private subnet and private IPv4 address
`10.42.18.195`; no container exit code exists because initialization failed.
CloudWatch log-stream metadata for the task returned an empty list, consistent
with the container never starting. No secret value or log content was
retrieved.

## Stop condition and likely declarative blocker

Per the Goal 6 failure policy, no retry, task run, Terraform apply, network
mutation, or ad-hoc repair was performed. The current Terraform source shows
the shared AWS interface-endpoint security group allows HTTPS ingress only from
the Goal 3B smoke and workload security groups, while the Goal 6 admin task
uses a dedicated security group. This is a likely explanation for the
Secrets Manager timeout, but it is not claimed as a connected root-cause proof
without a separately approved read-only inspection.

## Read-only root-cause inspection

The approved inspection found:

- Secrets Manager endpoint `vpce-06d9bb6fa72d0d334` is `available`, has private
  DNS enabled, and is present in both approved application subnets.
- Endpoint security group `sg-09df4c29eba7991fa` allows TCP/443 only from
  workload `sg-0a22126b47d3a5aea` and Goal 3B smoke `sg-0ef6cd84adeccf1b7`.
  It does not allow the Goal 6 admin task security group
  `sg-07a0dd2e8af8aa178`.
- The task subnet route table has an active NAT route, S3 gateway route, and
  the default allow NACL; no route/NACL blocker was found.
- ECS execution role `ask-david-development-ecs-execution` has only the
  AWS-managed `AmazonECSTaskExecutionRolePolicy`, whose inspected actions are
  ECR pull and CloudWatch Logs write. It has no
  `secretsmanager:GetSecretValue` or `kms:Decrypt`. The admin task-role exact
  secret policy cannot authorize ECS agent secret injection, which uses the
  execution role.

This proves two declarative prerequisites for the next remediation plan:

1. allow only the Goal 6 admin task SG to TCP/443 on the existing interface
   endpoint SG; and
2. grant the shared ECS execution role least-privilege `GetSecretValue` for the
   three Goal 6 secret ARNs plus `kms:Decrypt` on the secrets KMS key, without
   broadening unrelated task access.

No Terraform source, AWS resource, IAM policy, security group, or task was
changed during this inspection. Do not retry this task until a new offline
remediation, saved Terraform plan, review, and approval are complete.

## Approved post-remediation retry

A separate approval allowed exactly one retry after the endpoint security-group
and ECS execution-role remediation. The repository PowerShell wrapper could
not run because this host has no PowerShell runtime, so its fail-closed checks
were reproduced before one equivalent ECS control-plane request. No second
launch was made.

Task ARN:
`arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/2bc021ad5b834f8fa8abfbca432a32a5`

The task used revision 2, the approved immutable image digest, private
application subnet `subnet-034f5f1c9bca753f1`, Goal 6 admin security group
`sg-07a0dd2e8af8aa178`, and `assignPublicIp=DISABLED`. The ENI private address
was `10.42.30.171`.

It reached `STOPPED` with `stopCode=EssentialContainerExited` and container
exit code `7`. Redacted CloudWatch inspection reported:

```text
mysql: Deprecated program name. It will be removed in a future release, use '/usr/bin/mariadb' instead
mysql: unknown variable 'ssl-mode=REQUIRED'
```

The container therefore failed before the admin refresh operation and did not
emit the required completed marker. This is a deterministic client-option
compatibility defect in the verifier image (`alpine:3.21` plus
`mariadb-client`), not evidence of a Doris, Unity Catalog, S3, or network
result. Per the Goal 6 failure policy, no retry or ad-hoc image/task mutation
was performed.
