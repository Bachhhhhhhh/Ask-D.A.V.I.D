# Goal 6 Secrets Manager task-start remediation — offline implementation

Date: 2026-08-13
Scope: Terraform source, static tests, and documentation only
Connected plan/apply/task: none

## Remediation implemented

The deterministic inspection after the failed admin task showed that the
existing interface-endpoint security group omitted the dedicated Goal 6 admin
task SG and that the shared ECS execution role lacked the permissions required
for ECS agent secret injection. The offline source change now:

1. exposes the existing AWS interface-endpoint SG from the network module and
   adds one Goal 6-gated TCP/443 ingress rule from the admin task SG only;
2. exposes the Secrets KMS key ARN;
3. wires exactly the three Goal 6 secret ARNs and that KMS ARN into the IAM
   module; and
4. creates one Goal 6-gated execution-role inline policy granting only
   `secretsmanager:GetSecretValue` on those three ARNs and `kms:Decrypt` on the
   exact Secrets KMS key.

No wildcard Secrets Manager/KMS action, CIDR endpoint ingress, secret value,
AWS mutation, Terraform connected plan/apply, or task retry was performed.

## Offline validation

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| `python3 -m py_compile scripts/validate_goal6.py tests/unit/test_goal6_static.py` | PASS |
| Terraform mock tests (`development.tftest.hcl`, `goal4.tftest.hcl`) | PASS — 7 passed, 0 failed. Test fixtures explicitly disable Goal 6 task definitions when the foundation gate is false. |
| Terraform `validate` | PASS — configuration is valid. |
| Terraform `fmt -check` on changed `.tf`/`.tftest.hcl` files | PASS |
| `git diff --check` | PASS |
| Terraform connected plan/apply | NOT RUN — requires separate approval |
| ECS task run/retry | NOT RUN — blocked until saved-plan review and approval |

The next checkpoint is a new saved connected development Terraform plan. It
must contain only the reviewed endpoint-SG ingress rule, execution-role exact
secret/KMS policy, and any state/output updates intrinsically required by those
two changes; otherwise stop for review.

## Saved connected plan review

The approved read-only connected planning checkpoint created and inspected
`infrastructure/environments/development/goal-06-secret-endpoint-execution-role-remediation-20260813.tfplan`.

Plan SHA-256:

`2e84c69e612d0c229e7eb916a42c59cd0d475648278dfca104543d585405586a`

The plan has exactly two non-no-op resource actions:

1. create `aws_vpc_security_group_ingress_rule.goal6_admin_to_aws_endpoints[0]`
   — TCP/443 from the dedicated Goal 6 admin task security group to the
   existing AWS interface-endpoint security group;
2. create `module.iam.aws_iam_role_policy.task_execution_goal6_secrets[0]`
   — exact-ARN `secretsmanager:GetSecretValue` for the three Goal 6 container
   secrets and `kms:Decrypt` for the existing Secrets KMS key on the ECS
   execution role.

Terraform summary: `2 to add, 0 to change, 0 to destroy`.

No ECS task definition, task run, replacement, destroy, public exposure,
production, Databricks, S3 data, or unrelated IAM/KMS/network action is in the
saved plan. Apply remains a separate approval boundary; no apply had run at
the time this plan review was recorded.

## Approved apply and post-apply inspection

The user-approved apply of the exact saved plan completed successfully for
account `736956442295` in `ap-southeast-1`:

`Apply complete! Resources: 2 added, 0 changed, 0 destroyed.`

Read-only inspection then confirmed:

- security-group rule `sgr-0952ea339a38e0c31` allows only TCP/443 from
  `sg-07a0dd2e8af8aa178` (the dedicated Goal 6 admin task SG) to
  `sg-09df4c29eba7991fa` (the existing AWS interface-endpoint SG), with the
  Goal 6 private-endpoints-only description;
- inline policy `read-goal6-secret-containers` is attached to
  `ask-david-development-ecs-execution` and grants only
  `secretsmanager:GetSecretValue` on the three Goal 6 container secret ARNs
  plus `kms:Decrypt` on the exact Secrets KMS key;
- no task was started by this apply and no unrelated resource changed.

The next action is a separately approved single private admin-task retry using
the existing revision-2 task definition. No retry has been run yet.
