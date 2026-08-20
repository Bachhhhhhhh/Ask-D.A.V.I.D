# Goal 6 FE readiness-marker remediation — connected plan evidence

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: saved Terraform plan and read-only inspection only

## Boundary and identity

The plan was created after explicit approval for the readiness-marker
remediation. The caller identity was read-only verified as account
`736956442295`; the configured Terraform region was `ap-southeast-1`. The
remote development state was refreshed and a local saved plan was produced.
No apply, destroy, ECS task launch, ECR push, SQL/job run, Databricks
operation, or bundle operation occurred.

## Saved artifact

| Item | Value |
| --- | --- |
| Artifact | `infrastructure/environments/development/goal-06-fe-readiness-marker-remediation-20260813.tfplan` |
| SHA-256 | `07a9efc1f932b2eabc48216aef89cc476f0f6cfbc582a5a3d83b13b69f5349a6` |
| State mode | connected development remote-state refresh |
| Plan result | `243 no-op`, `6 delete/create`, `0 in-place change` |

The plan artifact is ignored by Git (`*.tfplan`) and is not a repository
source file.

## Exact non-no-op action set

The six delete/create replacements are limited to the declarative readiness
marker/user-data change and its known dependency propagation:

1. `module.doris_serving.aws_instance.fe[0]` — replacement due to `user_data`;
2. `module.doris_serving.aws_instance.be[0]` — replacement due to `user_data`;
3. `module.doris_serving.aws_volume_attachment.fe[0]` — replacement due to
   `instance_id`;
4. `module.doris_serving.aws_volume_attachment.be[0]` — replacement due to
   `instance_id`;
5. `module.doris_verifier.aws_ecs_task_definition.admin[0]` — replacement due
   to `container_definitions` receiving replacement-host values;
6. `module.doris_verifier.aws_ecs_task_definition.verifier[0]` — replacement
   due to `container_definitions` receiving replacement-host values.

There are no IAM, KMS, security-group, route/NACL, S3, ECR, Secrets Manager,
Databricks, production, public-exposure, or source-data actions. There are no
standalone volume deletions; the existing role volumes remain represented by
the attachment replacements.

## Review result and next boundary

The action set matches the approved readiness-marker remediation. This is a
plan-only checkpoint. Goal 6 remains blocked until a separate, explicit
hash-bound approval is given for applying this exact artifact. After any
approved apply, FE and BE persisted readiness markers must be inspected before
requesting another one-off private verifier task.
