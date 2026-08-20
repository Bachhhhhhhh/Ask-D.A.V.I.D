# Goal 6 Phase 6-13 audit-guard task definitions — apply

Date: `2026-08-20`

Status: **PASS — EXACT SAVED PLAN APPLIED; NO TASK EXECUTED**

## Approved boundary

The approved saved plan was applied after revalidating the AWS account, region,
and exact plan SHA-256. The apply was limited to the two reviewed Goal 6 ECS
task-definition replacements. No new plan was generated, no ECS task was
launched, and no Doris SQL, ECR, Databricks, or unrelated AWS operation ran.

## Apply binding and result

| Attribute | Value |
| --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| Saved plan | `/tmp/goal-06-phase-6-13-audit-guard-task-definitions-20260819.tfplan` |
| Plan SHA-256 | `b27a1755b130020f09255a87a16239acefc2d929760459b7b734fb36bda84c77` |
| Terraform result | `2 added, 0 changed, 2 destroyed` |
| Approved image digest | `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |

The `delete,create` entries represent registering new ECS task-definition
revisions and removing the prior state-owned revision. No ECS service, host,
volume, IAM, KMS, network, or data resource was deleted.

## Immediate read-only inspection

AWS ECS inspection confirmed:

| Family | Revision | Status | Runtime | Container/image |
| --- | ---: | --- | --- | --- |
| `ask-david-development-doris-admin-refresh` | `16` | `ACTIVE` | Fargate / `awsvpc` | `doris-admin` / exact approved digest |
| `ask-david-development-doris-verifier` | `16` | `ACTIVE` | Fargate / `awsvpc` | `doris-verifier` / exact approved digest |

`list-tasks` returned zero RUNNING tasks for both families. The first local
inspection invocation had a heredoc/stdin usage error; the corrected
read-only inspection passed and performed no mutation.

## Next approval boundary

Phase 6-13 remains unverified. A separate approval is required to run exactly
one private admin-refresh task from revision `16`, then separately one fresh
result-contract task and one audit verification task according to the Goal 6
no-retry contracts. This report authorizes no task execution.
