# Goal 6 private verifier task definitions — connected apply

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Saved-plan SHA-256: `982ad219cbb0810b248550c1be00a825cc5b5d58bf9505d69a3ddb58deaccc0b`

## Applied result

The separately approved saved plan applied successfully as `2 added, 0 changed,
0 destroyed`. It registered only these revision-1 task definitions:

| Family | ARN | Result |
| --- | --- | --- |
| `ask-david-development-doris-admin-refresh` | `arn:aws:ecs:ap-southeast-1:736956442295:task-definition/ask-david-development-doris-admin-refresh:1` | PASS |
| `ask-david-development-doris-verifier` | `arn:aws:ecs:ap-southeast-1:736956442295:task-definition/ask-david-development-doris-verifier:1` | PASS |

## Immediate read-only inspection

Both definitions are Fargate `awsvpc`, `512` CPU / `1024` MiB, use the approved
immutable verifier digest, retain their distinct existing task roles, and emit
only to the existing KMS-protected Doris CloudWatch log group. The admin
definition references only its three approved secret names; the read-only
definition references only its query-secret name. No secret values were read.

`aws ecs list-tasks` found no running Doris task. Terraform apply did not
launch a task, create an ECS service, expose a public endpoint, or change IAM,
KMS, network, security groups, ECR, S3, Databricks, or production resources.

## Pre-run blocker

Before task launch, source review found the admin runner would construct an
invalid double-scheme workspace URL: Terraform injects
`DATABRICKS_WORKSPACE_HOST=https://…`, while the runner prefixes both OAuth
and Iceberg REST URLs with another `https://`. This would form
`https://https://…` and fail OAuth before governed Doris validation.

No task was launched. The required next action is an offline, source/test/doc
remediation that normalizes the workspace origin and fails closed on an invalid
origin. It requires a new scanned image digest, saved task-definition plan, and
separate approvals before a replacement definition or task run.
