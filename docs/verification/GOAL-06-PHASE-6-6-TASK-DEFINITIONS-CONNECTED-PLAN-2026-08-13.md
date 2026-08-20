# Goal 6 private verifier task definitions — connected saved plan

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Phase: saved-plan review; no apply or task run

## Prerequisites

| Check | Result |
| --- | --- |
| Ignored task gate | PASS — `goal_6_verifier_tasks_enabled=true` only after immutable scanned image exists. |
| Image input | PASS — private ECR `@sha256:167912392ef3276123ec32b021083bd1b7dec02e12af12730cd702ad7143bea6`. |
| Offline preflight | PASS — structural state KMS key input present. |
| Goal 6 static validation | PASS. |
| AWS identity/region | PASS — account `736956442295`, `ap-southeast-1`. |
| Databricks identity | PASS — `bachvxuan@gmail.com`, development profile. |

## Saved plan

Ignored local artifact:

```text
infrastructure/environments/development/goal-06-verifier-task-definitions-20260813.tfplan
```

SHA-256:

```text
982ad219cbb0810b248550c1be00a825cc5b5d58bf9505d69a3ddb58deaccc0b
```

Terraform JSON review reports exactly two non-no-op actions:

| Terraform address | Action | Reviewed effect |
| --- | --- | --- |
| `module.doris_verifier.aws_ecs_task_definition.admin[0]` | create | One Fargate admin-refresh definition, digest-pinned image, existing private runtime cluster/roles/security group/log group, and exact secret references; it does not run a task. |
| `module.doris_verifier.aws_ecs_task_definition.verifier[0]` | create | One Fargate read-only verifier definition, same digest-pinned image and existing private verifier identity/network/logging; it does not run a task. |

Plan summary: `2 to add, 0 to change, 0 to destroy`. There are no
Databricks actions, ECR, IAM, KMS, network, security-group, S3/source-data,
metastore, warehouse, production, public-exposure, replacement, or destroy
actions. Outputs add only the two task-definition ARNs.

The task definitions require Fargate resources only while a separately
approved one-off task is running. They create no ECS service, no public IP, no
cluster, and no new persistent compute.

## Required next approval

Apply only the hash-bound artifact above after re-verifying account and region.
It may register exactly these two task definitions and nothing else. Do not run
either task as part of the apply. If apply fails, stop for read-only inventory;
do not retry or make ad-hoc repairs.
