# Goal 6 Doris listener host-prerequisite remediation — connected plan evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: connected read-only Terraform refresh and saved-plan review only

## Approval and revalidation

The connected plan step was explicitly approved. AWS identity was revalidated
read-only as account `736956442295` and the configured Terraform region and
development variables are `ap-southeast-1`. No credentials were printed.

Terraform v1.15.8 used the approved development backend and the local provider
mirror. Remote Terraform state and current Databricks/AWS provider state were
refreshed. No apply, destroy, ECS task, SQL/job, bundle, or ad-hoc cloud
mutation occurred.

## Saved artifact integrity

```text
infrastructure/environments/development/goal-06-doris-listener-host-prereq-remediation-20260814.tfplan
SHA-256: bbe5e504b136fd639995c033d90afecf3a557fb430dbd3a1f194f29e5b7a0bbd
```

The plan was inspected with `terraform show -json` from the development root.
The JSON inspection was local only and did not expose secret values.

## Exact action set

Terraform reports:

```text
Plan: 6 to add, 0 to change, 6 to destroy.
```

The six delete/create pairs are all reviewed replacements:

| Terraform address | Action | Replacement path | Reason |
| --- | --- | --- | --- |
| `module.doris_serving.aws_instance.fe[0]` | delete/create | `user_data` | host prerequisite and diagnostics bootstrap |
| `module.doris_serving.aws_instance.be[0]` | delete/create | `user_data` | host prerequisite and diagnostics bootstrap |
| `module.doris_serving.aws_volume_attachment.fe[0]` | delete/create | `instance_id` | reattach existing FE role volume to replacement host |
| `module.doris_serving.aws_volume_attachment.be[0]` | delete/create | `instance_id` | reattach existing BE role volume to replacement host |
| `module.doris_verifier.aws_ecs_task_definition.admin[0]` | delete/create | `container_definitions` | propagate replacement private FE/BE addresses |
| `module.doris_verifier.aws_ecs_task_definition.verifier[0]` | delete/create | `container_definitions` | propagate replacement private FE address |

The JSON review found exactly 6 non-no-op resources and 243 `no-op` resources.
All non-no-op addresses are under `module.doris_serving` or
`module.doris_verifier`. There are zero in-place changes and zero actions for
IAM, KMS, security groups, routes/NACLs, S3, ECR, Secrets Manager, Databricks,
production, public exposure, or source data.

Output updates only reflect replacement host/task-definition identities:
`goal_6_doris_admin_task_definition_arn`,
`goal_6_doris_be_private_ip`, `goal_6_doris_fe_private_ip`, and
`goal_6_doris_verifier_task_definition_arn`.

## Review result and next boundary

The action set matches the approved offline remediation and is suitable for a
separate hash-bound apply decision. This report does not approve or perform
that apply. No verifier task may run until both replacement hosts emit
`doris-port-ready`.
