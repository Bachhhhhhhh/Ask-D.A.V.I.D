# Goal 6 Phase 6-12 query-limit task definitions — connected plan

Date: `2026-08-19`

Status: `PASS — SAVED PLAN REVIEWED; APPLY NOT APPROVED`

## Approved boundary

The approved operation was limited to updating the ignored development image
input to the already scanned and ECR-promoted immutable digest, running offline
preflight, and creating and reviewing one saved connected development
Terraform plan. No Terraform apply, ECS task, Doris SQL, ECR push, Databricks
operation, or unrelated AWS mutation was performed.

## Exact plan artifact

| Attribute | Result |
| --- | --- |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| Terraform root | `infrastructure/environments/development` |
| Plan file | `goal-06-query-limit-task-definitions-20260819.tfplan` |
| Plan SHA-256 | `c24205563e73adcda4345a1d3707c27807c21a3c701eac3b8469e93f2b982ae1` |
| Plan size | `207,916` bytes |
| Terraform version | `1.15.8` |
| Image digest | `sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36` |
| Saved-plan summary | `2 to add, 0 to change, 2 to destroy` |

The plan was saved locally and is ignored by the repository. Its SHA-256 is the
approval binding; it must not be regenerated implicitly for an apply.

## Machine-readable action review

Terraform JSON inspection found exactly two non-no-op resource changes:

| Address | Actions | Replacement path |
| --- | --- | --- |
| `module.doris_verifier.aws_ecs_task_definition.admin[0]` | `delete,create` | `container_definitions` |
| `module.doris_verifier.aws_ecs_task_definition.verifier[0]` | `delete,create` | `container_definitions` |

The only reviewed content change is the container image digest, from the
previous verifier image to
`sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36`.
There are zero other creates, updates, replacements, or destroys. In
particular, the plan contains no IAM, KMS, networking, security-group, EC2,
EBS, ECR, S3, Databricks, production, public-exposure, or Goal 7+ action.

## Offline preflight evidence

- `python3 scripts/validate_goal6.py` — PASS.
- `sh -n docker/doris-verifier/doris-query-limit-verify` — PASS.
- `pytest -q -o addopts='' tests/unit/test_goal5_static_goal6_regression.py tests/unit/test_goal6_static.py` — PASS (`45 passed`).
- `git diff --check` — PASS.
- `terraform fmt -check -recursive infrastructure/environments/development infrastructure/modules` — UNVERIFIED because the installed Snap Terraform binary is blocked by confinement (`snap-confine ... cap_dac_override not found`); Terraform v1.15.8 itself was available for the saved plan.

## Checkpoint and next approval

Phase 6-12 remains **UNVERIFIED**. The exact image is registered in the plan,
but no task definition has been applied and no query-limit verifier has run.
The next permitted operation requires a separate explicit approval bound to
this exact plan SHA-256, followed by immediate read-only task-definition
inspection. Any apply failure must stop without an implicit replacement plan or
retry.
