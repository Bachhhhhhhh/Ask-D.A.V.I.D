# Goal 6 admin global-grant remediation — task-definition connected plan

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **AWAITING APPLY APPROVAL**

## Revalidation

Before planning, read-only checks confirmed AWS account `736956442295` and
the authenticated Databricks development governance administrator. Terraform
initialized the configured S3 backend in an isolated temporary `TF_DATA_DIR`;
the backend was used only for state refresh and plan creation.

The sole ignored local-input change is
`goal_6_verifier_image`, from the prior pinned digest to:

```text
736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier@sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad
```

All Goal 6 enablement, private subnet/address, and rebuild-state inputs remain
unchanged.

## Saved plan

| Property | Value |
| --- | --- |
| Artifact | `infrastructure/environments/development/goal-06-admin-priv-task-definitions-20260817.tfplan` |
| SHA-256 | `1f4b654bce71c95beed62d2ca3dc39a08a8c6dbca7fdaeee6798450a65ce68ad` |
| Size | `214,979` bytes |
| Git handling | ignored by existing `*.tfplan` rule |
| Action summary | `2 to add, 0 to change, 2 to destroy` |

Filtered plan JSON reports 255 no-op resources and exactly two Terraform state
replacements, both forced solely by `container_definitions`:

| Address | Terraform action | Effective change |
| --- | --- | --- |
| `module.doris_verifier.aws_ecs_task_definition.admin[0]` | delete/create replacement | register new admin-refresh revision with corrected image digest |
| `module.doris_verifier.aws_ecs_task_definition.verifier[0]` | delete/create replacement | register new read-only verifier revision with corrected image digest |

Both retain their names, commands, and no task-definition entrypoint override:

| Task | Command | Before/after difference |
| --- | --- | --- |
| `doris-admin` | `/app/doris-admin-refresh` | image digest only |
| `doris-verifier` | `/app/doris-readonly-verify` | image digest only |

There are zero planned AWS/Databricks IAM, KMS, secret, network, security-group,
ECR, S3, EC2/EBS, metastore, workspace-assignment, cluster/warehouse,
production, public-exposure, source-data, SQL, task-run, or Goal 7+ actions.
No ECS task runs as part of registering a task-definition revision.

## Required approval

Applying this exact saved plan will register the two replacement task-definition
revisions and remove Terraform state ownership of revision 7 for those two
families. It must not run an ECS task. Any later admin-refresh execution is a
separate approval boundary.
