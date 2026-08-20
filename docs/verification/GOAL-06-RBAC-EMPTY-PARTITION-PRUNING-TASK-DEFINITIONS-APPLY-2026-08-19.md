# Goal 6 RBAC empty-partition pruning — task-definition apply

Date: `2026-08-19`

Status: **PASS — EXACT SAVED PLAN APPLIED; NO TASK EXECUTED**

## Approved saved plan

| Attribute | Value |
| --- | --- |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| AWS principal | `arn:aws:iam::736956442295:user/bach_dev_admin_david` |
| Saved plan | `/tmp/goal-06-rbac-empty-partition-pruning-task-definitions-retry-20260819.tfplan` |
| Approved SHA-256 | `8e6e62d931eb86fe5b65e335cb996122fdb7c05f121fcc85a3cd50f81582f9d0` |
| Image digest | `sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9` |

Immediately before apply, the artifact hash matched the approved value,
machine-readable plan metadata remained `applyable=true`, `complete=true`,
and `errored=false`, and STS/configuration returned the approved account and
Region. Terraform applied the saved artifact directly with `-input=false`; it
did not generate an implicit plan.

## Apply result

Terraform reported:

```text
Apply complete! Resources: 2 added, 0 changed, 2 destroyed.
```

The replacement semantics correspond exactly to:

1. `module.doris_verifier.aws_ecs_task_definition.admin[0]`;
2. `module.doris_verifier.aws_ecs_task_definition.verifier[0]`.

For an ECS task definition, Terraform represents registration of a new
revision and deregistration of the prior state-owned revision as replacement.
No ECS service, running task, host, volume, network resource, or data was
destroyed.

## Immediate read-only inspection

| Family | Revision | Status | Launch/network | CPU/memory | Image |
| --- | ---: | --- | --- | --- | --- |
| `ask-david-development-doris-admin-refresh` | 12 | ACTIVE | Fargate / `awsvpc` | `512` / `1024` | exact approved digest |
| `ask-david-development-doris-verifier` | 12 | ACTIVE | Fargate / `awsvpc` | `512` / `1024` | exact approved digest |

The admin task uses execution role
`ask-david-development-ecs-execution` and task role
`ask-david-development-doris-admin-task`. The verifier uses the same execution
role and task role `ask-david-development-doris-verifier-task`. Each family
has only revision 12 ACTIVE. `list-tasks` returned zero RUNNING tasks for both
families, so neither apply nor inspection launched a task.

## Scope and next boundary

No IAM, KMS, network/security-group, ECR, EC2/EBS, S3, Secrets Manager,
Databricks, metastore, warehouse, public, production, or Goal 7+ resource
changed. No Doris SQL or application/data operation ran.

The remediated image is deployed but its runtime RBAC behavior remains
unverified. Exactly one private, no-retry revision-12 RBAC verifier task
requires separate approval. It must use the approved private application
subnets, verifier security group, `assignPublicIp=DISABLED`, FE
`10.42.64.238`, and the exact revision/image above. Any non-zero exit,
precondition failure, wrong rejection layer, or unexpectedly allowed probe
must stop further work for review.
