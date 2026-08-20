# Goal 6 RBAC empty-partition pruning — task-definition connected plan

Date: `2026-08-19`

Status: **PASS — COMPLETE SAVED PLAN REVIEWED AND APPLIED**

## Approved scope

After interactive Databricks reauthentication, the approved checkpoint was
limited to read-only Databricks/AWS identity validation and one new saved
connected development plan. It did not authorize apply, an ECS task, ECR push,
Doris SQL, Databricks mutation, destroy outside task-definition registration
semantics, or another infrastructure mutation.

The prior artifact at
`/tmp/goal-06-rbac-empty-partition-pruning-task-definitions-20260819.tfplan`
remains `applyable=false`, `complete=false`, and `errored=true`. It was
preserved and never reused.

## Connected preflight

| Check | Result |
| --- | --- |
| AWS account / Region | PASS — `736956442295` / `ap-southeast-1` |
| AWS principal | `arn:aws:iam::736956442295:user/bach_dev_admin_david` |
| Databricks account | `e7e97bc6-a872-4312-9a43-c0eb305b1b2e` |
| Workspace | PASS — `7474644358733471`, `RUNNING` |
| Workspace Region | PASS — `ap-southeast-1` |
| Workspace tier/compute mode | `PREMIUM` / `SERVERLESS` |
| Workspace principal | PASS — active `bachvxuan@gmail.com`, governance-admin/admin membership present |
| Backend context | PASS — existing S3 backend in `ap-southeast-1` via isolated Terraform data directory |
| New artifact path | PASS — absent before plan |

Both profiles passed real API calls before planning. The workspace profile
returned the current active principal, and the account profile returned the
approved running workspace. No token or credential value was printed or
persisted in the repository.

## Saved artifact

| Attribute | Value |
| --- | --- |
| Saved plan | `/tmp/goal-06-rbac-empty-partition-pruning-task-definitions-retry-20260819.tfplan` |
| SHA-256 | `8e6e62d931eb86fe5b65e335cb996122fdb7c05f121fcc85a3cd50f81582f9d0` |
| Size | `208,643` bytes |
| Terraform / plan format | `1.15.8` / `1.2` |
| `applyable` | `true` |
| `complete` | `true` |
| `errored` | `false` |

The plan used `-lock=false`, read current remote/provider state, and wrote only
the local saved-plan artifact. It did not create an external lock object.

## Machine-readable action review

| Actions | Count |
| --- | ---: |
| `delete,create` replacement | 2 |
| `no-op` | 257 |
| In-place update | 0 |
| Create-only | 0 |
| Destroy-only | 0 |

The only changed managed resources are:

1. `module.doris_verifier.aws_ecs_task_definition.admin[0]`;
2. `module.doris_verifier.aws_ecs_task_definition.verifier[0]`.

For each resource:

- type is `aws_ecs_task_definition`;
- actions are exactly `delete,create`;
- the only replacement path is `container_definitions`;
- prior image digest is
  `sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e`;
- new image digest is
  `sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9`.

Only the corresponding admin/verifier task-definition ARN outputs update.
There is no IAM, KMS, network/security-group, ECR, EC2/EBS, S3, Secrets
Manager, RDS, Redis, OpenSearch, Databricks, metastore, workspace, warehouse,
public-exposure, production, or Goal 7+ managed-resource action.

Terraform represents registering a new task-definition revision and removing
the prior revision from state as replacement. This does not delete an ECS
service, running task, host, volume, or data resource, and no task is launched
by apply.

## Apply result

The separately approved apply reverified the artifact SHA-256, AWS
account/Region, and `applyable=true`, `complete=true`, `errored=false` flags,
then applied this exact saved artifact directly without creating another plan.
Terraform reported `2 added, 0 changed, 2 destroyed`, representing only new
revision registration and prior state-owned revision deregistration for the
two reviewed ECS task-definition resources. Revision 12 is ACTIVE for both
families on the exact approved image digest, and read-only inspection found
zero RUNNING tasks. No ECS task was executed. See
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-TASK-DEFINITIONS-APPLY-2026-08-19.md`.

A one-shot revision-12 RBAC runtime retry remains a later independent approval
boundary.
