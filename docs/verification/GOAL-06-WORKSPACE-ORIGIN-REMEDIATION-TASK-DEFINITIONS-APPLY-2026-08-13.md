# Goal 6 workspace-origin remediation task definitions — connected apply

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Saved-plan SHA-256: `ffca04bb20e5fa81d34704b57e2b33ea16dec61241d4a9b615df330109967f13`

## Approved change and result

After explicit hash-bound approval, Terraform applied the reviewed saved plan
as `2 added, 0 changed, 2 destroyed`. The two delete/create actions are the
Terraform state representation of registering immutable ECS task-definition
revisions; they did not run an ECS task and did not delete infrastructure.

| Family | New active revision | Immutable image digest | Result |
| --- | --- | --- | --- |
| `ask-david-development-doris-admin-refresh` | `:2` | `sha256:41095093cb0cc820eb8b15afedacf97333ba443de8216de9dc40b950becee57d` | PASS |
| `ask-david-development-doris-verifier` | `:2` | `sha256:41095093cb0cc820eb8b15afedacf97333ba443de8216de9dc40b950becee57d` | PASS |

No other planned target existed. No IAM, KMS, VPC, security-group, ECR, S3,
Databricks, production, service, or compute-resource change was applied.

## Immediate read-only inspection

Both revision-2 definitions are `ACTIVE`, use Fargate with `awsvpc` network
mode and `512` CPU / `1024` MiB, and reference the exact ECR immutable digest
above. `aws ecs list-tasks --cluster ask-david-development-cluster
--desired-status RUNNING` returned an empty list.

## Boundaries and next checkpoint

No ECS task was started. The remediated admin runner has not yet been executed
against Databricks or Doris, so workspace-origin, Unity Catalog, and serving
validation remain unverified. The existing repository wrapper is explicitly
limited to the three Goal 3B smoke definitions; no dedicated Goal 6 RunTask
wrapper exists yet. An offline, source/test/documentation-only wrapper
implementation must be reviewed and validated before a separately approved
private admin-refresh task run can occur.
