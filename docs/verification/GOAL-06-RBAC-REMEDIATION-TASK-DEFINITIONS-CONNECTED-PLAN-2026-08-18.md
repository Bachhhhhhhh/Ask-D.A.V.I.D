# Goal 6 RBAC remediation — task-definition connected plan

Date: 2026-08-18
Status: **REVIEWED — AWAITING HASH-BOUND APPLY APPROVAL**

## Scope

This saved development plan promotes only the reviewed RBAC-remediation
verifier image. It does not authorize an apply or any ECS task execution.

| Item | Value |
| --- | --- |
| AWS account | `736956442295` |
| Region | `ap-southeast-1` |
| Plan artifact | `/tmp/goal-06-rbac-task-definitions-20260818.tfplan` (local, ignored) |
| Plan SHA-256 | `09a97fcdc9cacdbd82e69ea8157a7f74753fc8578d5280be8ce62433179ac7db` |
| Previous deployed image digest | `sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510` |
| Reviewed replacement image digest | `sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6` |

## Preconditions and local checks

- Development tfvars were updated only locally (and remain Git-ignored) to
  use the reviewed immutable ECR digest with verifier task definitions enabled.
- `python3 scripts/dev.py infra-preflight` passed.
- `python3 scripts/validate_goal6.py` passed.
- AWS identity was reverified as account `736956442295` in
  `ap-southeast-1` before the connected plan.

## Reviewed plan actions

The plan has exactly two non-no-op managed-resource changes:

| Address | Terraform action | Replacement cause | Before → after image |
| --- | --- | --- | --- |
| `module.doris_verifier.aws_ecs_task_definition.admin[0]` | `delete, create` | `container_definitions` | `2c2e35…` → `c7e9cb…` |
| `module.doris_verifier.aws_ecs_task_definition.verifier[0]` | `delete, create` | `container_definitions` | `2c2e35…` → `c7e9cb…` |

All other managed resources are no-op. There are no changes to IAM, KMS,
networking, security groups, ECR, EC2/EBS, S3, Databricks, public exposure, or
production resources. ECS task-definition replacement here means registering
new revisions; it does not run a task or remove a running service.

## Boundary

This report is plan evidence only. Applying the exact SHA-bound artifact needs
a separate explicit approval. A later RBAC verifier execution needs another
separate approval after the new revision is active.
