# Goal 6 SMALLINT probe remediation task-definition apply — 2026-08-19

## Scope

The exact separately approved saved Terraform plan was applied after
revalidating its SHA-256, AWS account/region, and ECR image digest. No ECS task
was run and no Doris SQL, Databricks operation, ECR push, or unrelated AWS
resource mutation occurred.

## Approval-bound artifact

| Attribute | Value |
| --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| Saved plan | `/tmp/goal-06-rbac-nonempty-delete-probe-smallint-task-definitions-20260819.tfplan` |
| Plan SHA-256 | `79b640a313fc65fb3408d481e1c9833c36ac29ae777e47f0f198b813e5d3f2ff` |
| Image digest | `sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88` |
| Terraform result | `2 added, 0 changed, 2 destroyed` |

The `delete,create` operations are the expected ECS task-definition revision
replacement representation. They did not delete an ECS service, running task,
EC2 instance, EBS volume, IAM role, network, ECR repository, or data resource.

## Post-apply read-only inspection

| Resource | Result |
| --- | --- |
| `ask-david-development-doris-admin-refresh:14` | PASS — `ACTIVE`, Fargate, `awsvpc`, `512` CPU / `1024` MiB |
| `ask-david-development-doris-verifier:14` | PASS — `ACTIVE`, Fargate, `awsvpc`, `512` CPU / `1024` MiB |
| Admin image | PASS — exact approved digest `sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88` |
| Verifier image | PASS — exact approved digest `sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88` |
| Admin command | PASS — `/app/doris-admin-refresh` |
| Verifier command | PASS — `/app/doris-readonly-verify` |
| Running Goal 6 ECS tasks | PASS — none (`list-tasks --desired-status RUNNING` returned `[]`) |

## Current checkpoint

The two Terraform-created task definitions now point at the SMALLINT probe
remediation image. No admin refresh or verifier retry has run. The next
operation requires separate approval for one private admin-refresh task; its
result must be inspected before any RBAC verifier task approval.
