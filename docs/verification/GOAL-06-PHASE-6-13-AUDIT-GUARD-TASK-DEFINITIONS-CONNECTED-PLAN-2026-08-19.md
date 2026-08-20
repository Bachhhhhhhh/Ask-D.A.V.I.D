# Goal 6 Phase 6-13 audit-guard task definitions — connected plan

Date: `2026-08-19`

Status: **PASS — SAVED PLAN REVIEWED; APPLY NOT APPROVED**

## Approved boundary

This checkpoint updated only the ignored development
`goal_6_verifier_image` input, ran offline preflight, and created one saved
connected development Terraform plan. The plan used read-only AWS,
Databricks, and remote-state refresh with `-lock=false`. No Terraform apply,
ECS task, Doris SQL, ECR push, Databricks mutation, or unrelated AWS mutation
occurred.

## Inputs and preflight

| Check | Result |
| --- | --- |
| AWS account / region | PASS — `736956442295` / `ap-southeast-1` |
| ECR image input | PASS — exact promoted digest `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |
| Development task gate | PASS — `goal_6_verifier_tasks_enabled = true` |
| Local infrastructure preflight | PASS — structurally valid state KMS ARN |
| Goal 6 static validator | PASS |
| Focused Goal 5/6 regression suite | PASS — `46 passed`; 2 non-failing cache-permission warnings |
| Terraform formatting | PASS — direct Terraform v1.15.8 `fmt -check -recursive` |
| `git diff --check` | PASS |

Only the ignored `goal_6_verifier_image` line changed locally. No tracked
source or configuration file was changed by the input update.

## Saved plan artifact

| Attribute | Value |
| --- | --- |
| Terraform root | `infrastructure/environments/development` |
| Plan path | `/tmp/goal-06-phase-6-13-audit-guard-task-definitions-20260819.tfplan` |
| Plan SHA-256 | `b27a1755b130020f09255a87a16239acefc2d929760459b7b734fb36bda84c77` |
| Plan size | `208,635` bytes |
| Terraform | `1.15.8` |
| Backend | Existing development S3 backend; `-lock=false` |
| Image digest | `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |
| Terraform summary | `2 to add, 0 to change, 2 to destroy` |

The saved plan is local and ignored. It was not regenerated after creation.

## Action review

The complete Terraform plan text contains exactly these two non-no-op managed
resources:

| Address | Actions | Replacement path |
| --- | --- | --- |
| `module.doris_verifier.aws_ecs_task_definition.admin[0]` | `delete,create` | `container_definitions` |
| `module.doris_verifier.aws_ecs_task_definition.verifier[0]` | `delete,create` | `container_definitions` |

For both resources, the only semantic change is the container image from the
revision-15 digest
`sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36`
to the exact promoted audit-guard digest above. There are zero other creates,
updates, replacements, or destroys. In particular, the plan contains no IAM,
KMS, network/security-group, EC2, EBS, ECR, S3, Secrets Manager, Databricks,
metastore, warehouse, public-exposure, production, or Goal 7+ action.

Terraform's `delete,create` representation is task-definition revision
registration/state replacement; it does not delete an ECS service, running
task, host, volume, or data resource.

## Post-plan inspection limitation

The saved plan was created successfully and its full textual action review
passed. A follow-up `terraform show -json` attempt against the unchanged saved
artifact could not reload the provider schemas because the installed provider
processes returned a remote-plugin handshake error in this environment. The
JSON machine-readable post-check is therefore **UNVERIFIED**; it did not alter,
regenerate, apply, or invalidate the saved plan. The exact action inventory
above is based on Terraform's successful plan output and summary.

## Apply boundary

Only the exact artifact and SHA-256 above may be applied after separate
approval. Before apply, revalidate the artifact hash, account, region, and
image digest. Do not create an implicit replacement plan. This checkpoint
authorizes no ECS task execution; the admin refresh and later audit task each
require independent approvals.
