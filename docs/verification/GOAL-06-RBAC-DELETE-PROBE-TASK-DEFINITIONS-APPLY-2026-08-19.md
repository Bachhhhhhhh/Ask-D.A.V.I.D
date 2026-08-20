# Goal 6 RBAC DELETE-probe remediation — task-definition apply

Date: `2026-08-19`

Status: **PASS — EXACT SAVED PLAN APPLIED; NO TASK EXECUTED**

## Approved saved plan

| Attribute | Value |
| --- | --- |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| Saved plan | `/tmp/goal-06-rbac-delete-probe-task-definitions-20260819.tfplan` |
| Approved SHA-256 | `decb5329e0c7b7d811525da23d1a607ee8527c4b1a197e6adcea9cfdc88a4dcf` |
| Image digest | `sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e` |

Immediately before apply, the local artifact hash matched the approved value,
the isolated Terraform data directory retained the reviewed S3 backend
configuration, and STS returned the approved account. Terraform applied the
saved artifact directly with `-input=false`; it did not generate an implicit
or replacement plan.

## Apply result

Terraform reported:

```text
Apply complete! Resources: 2 added, 0 changed, 2 destroyed.
```

The two replacement semantics correspond exactly to the reviewed ECS task-
definition resources:

1. `module.doris_verifier.aws_ecs_task_definition.admin[0]`;
2. `module.doris_verifier.aws_ecs_task_definition.verifier[0]`.

No other resource action appeared. Registering a new ECS task-definition
revision and deregistering the prior state-owned revision is represented by
Terraform as replacement; no ECS service, running task, data, host, volume, or
network resource was destroyed.

## Immediate read-only inspection

| Family | Revision | Status | Launch/network | CPU/memory | Image |
| --- | ---: | --- | --- | --- | --- |
| `ask-david-development-doris-admin-refresh` | 11 | ACTIVE | Fargate / `awsvpc` | `512` / `1024` | exact approved digest |
| `ask-david-development-doris-verifier` | 11 | ACTIVE | Fargate / `awsvpc` | `512` / `1024` | exact approved digest |

Both revision-10 definitions are now INACTIVE. `list-tasks` returned zero
RUNNING tasks for each family. No task was launched by apply or inspection.

## Scope and next boundary

No IAM, KMS, network/security-group, ECR, EC2/EBS, S3, Databricks, metastore,
warehouse, public, production, or Goal 7+ resource changed. No Doris SQL or
application/data operation ran.

The source correction is now deployable but not yet verified in runtime.
Exactly one private, no-retry revision-11 RBAC verifier task requires separate
approval. It must use the approved private application subnets, verifier
security group, `assignPublicIp=DISABLED`, FE `10.42.64.238`, and the exact
revision/image above. Any non-zero exit, precondition failure, wrong rejection
layer, or unexpectedly allowed probe must stop further work for review.

## Subsequent runtime result

The separately approved one-shot revision-11 run stopped with exit `1` at the
DELETE probe after INSERT and UPDATE produced authorization-layer denials. No
retry occurred. The reserved-key precondition prevented a data mutation, but
the live disposable table was entirely empty and Doris pruned that partition
to an empty relation before its `LOAD_PRIV` check. This task-definition apply
remains correctly scoped, but its image does not satisfy the full Phase 6-11
RBAC evidence contract. See
`docs/verification/GOAL-06-RBAC-REVISION-11-EMPTY-PARTITION-FAILURE-2026-08-19.md`.
