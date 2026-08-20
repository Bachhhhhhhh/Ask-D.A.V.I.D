# Goal 6 SMALLINT probe remediation task-definition plan — 2026-08-19

## Scope and boundary

The separately approved checkpoint updated only the ignored development
`goal_6_verifier_image` input, ran offline validation, and created one saved
connected Terraform plan. No Terraform apply/destroy, ECS task run, ECR push,
Doris SQL, Databricks operation, or unrelated AWS mutation occurred.

## Inputs and preflight

| Check | Result |
| --- | --- |
| AWS account / region | PASS — `736956442295` / `ap-southeast-1` |
| AWS identity | PASS — `arn:aws:iam::736956442295:user/bach_dev_admin_david` |
| ECR image | PASS — exact digest exists under immutable tag `goal6-smallint-probe-6fa3d0c9` |
| Development task gate | PASS — `goal_6_verifier_tasks_enabled = true` |
| Development image input | PASS — digest-pinned to `sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88` |
| Infrastructure preflight | PASS — structurally valid state KMS ARN |
| Goal 6 static validator | PASS |
| Focused Goal 5/6 regression suite | PASS — 45 tests |
| `git diff --check` | PASS |

The ignored file changed only its Goal 6 verifier image digest. No tracked
source or configuration file was changed by this checkpoint.

## Saved plan

| Attribute | Value |
| --- | --- |
| Plan artifact | `/tmp/goal-06-rbac-nonempty-delete-probe-smallint-task-definitions-20260819.tfplan` |
| Plan SHA-256 | `79b640a313fc65fb3408d481e1c9833c36ac29ae777e47f0f198b813e5d3f2ff` |
| Terraform | `1.15.8` |
| Backend | Existing development S3 backend; plan used `-lock=false` |
| Plan mode | `-refresh=true -input=false`; no apply |

The plan JSON was inspected locally with `terraform show -json`.

## Exact action inventory

| Action set | Count |
| --- | ---: |
| `delete,create` replacement | 2 |
| `no-op` | 257 |
| In-place update | 0 |
| Create-only | 0 |
| Destroy-only | 0 |

The only non-no-op addresses are:

1. `module.doris_verifier.aws_ecs_task_definition.admin[0]`;
2. `module.doris_verifier.aws_ecs_task_definition.verifier[0]`.

Both replacements change only the container image from the deployed revision-
13 digest `sha256:b2a4629e1e207fa9b2d06cdca5956472f6e4f94e4f40723a5bc45f1a18b17a73`
to the exact promoted SMALLINT-remediation digest
`sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88`.
Terraform's `delete,create` representation is task-definition revision
registration/state replacement; it does not delete an ECS service, running
task, EC2 instance, EBS volume, IAM role, network, ECR repository, or data.

No IAM, KMS, security-group, network, ECR, EC2/EBS, S3, Databricks, metastore,
warehouse, public-exposure, production, or Goal 7+ action is present.

## Apply boundary

Only the exact artifact and SHA-256 above may be applied after separate approval.
Before apply, revalidate account, region, image digest, and artifact hash. Do
not generate an implicit replacement plan. This checkpoint authorizes no ECS
task execution; the one-shot admin refresh and later RBAC verifier retry each
require independent approval.
