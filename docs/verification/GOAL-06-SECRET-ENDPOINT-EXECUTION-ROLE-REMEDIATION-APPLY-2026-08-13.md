# Goal 6 secret endpoint and execution-role remediation — apply evidence

Date: 2026-08-13
AWS account: `736956442295`
AWS region: `ap-southeast-1`
Saved plan SHA-256: `2e84c69e612d0c229e7eb916a42c59cd0d475648278dfca104543d585405586a`

## Apply result

The approved saved plan was applied without creating an implicit plan:

`Apply complete! Resources: 2 added, 0 changed, 0 destroyed.`

Applied resources were exactly:

1. `aws_vpc_security_group_ingress_rule.goal6_admin_to_aws_endpoints[0]`
2. `module.iam.aws_iam_role_policy.task_execution_goal6_secrets[0]`

No replacement, destroy, ECS task run, public exposure, production change, or
unrelated AWS/Databricks mutation occurred.

## Read-only post-apply evidence

- AWS identity remained account `736956442295` in the approved region.
- Rule `sgr-0952ea339a38e0c31` is TCP/443 from the dedicated admin task SG
  `sg-07a0dd2e8af8aa178` to the existing interface-endpoint SG
  `sg-09df4c29eba7991fa`.
- Policy `read-goal6-secret-containers` on
  `ask-david-development-ecs-execution` contains only exact-ARN
  `secretsmanager:GetSecretValue` for the three Goal 6 container secrets and
  exact-key `kms:Decrypt` for the Secrets KMS key. No wildcard action or
  resource was observed.

The remediation is applied. A separate approval is still required before the
single no-retry private admin-task verification run. Doris health, Unity
Catalog interoperability, serving refresh, rebuild, and read-only acceptance
remain unverified.
