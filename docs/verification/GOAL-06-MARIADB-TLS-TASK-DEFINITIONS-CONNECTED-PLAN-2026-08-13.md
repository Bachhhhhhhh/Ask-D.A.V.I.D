# Goal 6 MariaDB TLS task definitions — saved connected plan

Date: 2026-08-13
AWS account: `736956442295`
AWS region: `ap-southeast-1`
Plan artifact: `infrastructure/environments/development/goal-06-mariadb-tls-task-definitions-20260813.tfplan`

## Plan identity

SHA-256:

`7f4de065ecae0de13d97954bc97314306af7a09b50831c2cf85048ea00b39aa0`

The plan was created after updating only the ignored development verifier image
input to the approved ECR digest:

`sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6`

## Reviewed resource actions

The JSON plan inspection found exactly two non-no-op resource changes:

| Resource | Actions | Replacement path | Effect |
| --- | --- | --- | --- |
| `module.doris_verifier.aws_ecs_task_definition.admin[0]` | delete/create | `container_definitions` | Register the admin-refresh revision with the new immutable image. |
| `module.doris_verifier.aws_ecs_task_definition.verifier[0]` | delete/create | `container_definitions` | Register the read-only verifier revision with the new immutable image. |

Terraform's human-readable summary is `2 to add, 0 to change, 2 to destroy`;
these delete/create actions are the expected ECS task-definition revision
replacement semantics, not infrastructure replacement of the ECS cluster,
network, IAM, secrets, Doris nodes, or any data resource.

All other managed resources are no-op. The only output changes are the two
task-definition ARN revisions. No public exposure, production change, ECS
task run, ECR push, Databricks operation, SQL run, S3 data mutation, or
unrelated AWS action is present.

## Approval boundary

This is a saved plan only. Applying it requires separate explicit approval.
At the later approval boundary, this exact plan was applied successfully:

`Apply complete! Resources: 2 added, 0 changed, 2 destroyed.`

Read-only inspection confirmed active revision `3` for both task-definition
families, each using the approved ECR digest
`sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6`,
with Fargate/`awsvpc` configuration. No Goal 6 task is running. No task retry
or other resource mutation occurred in this checkpoint.
