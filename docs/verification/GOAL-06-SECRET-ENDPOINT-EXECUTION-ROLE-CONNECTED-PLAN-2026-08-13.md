# Goal 6 secret endpoint and execution-role remediation — saved connected plan

Date: 2026-08-13
Scope: read-only Terraform planning and local artifact inspection
AWS account: `736956442295`
AWS region: `ap-southeast-1`
Apply: not run

## Plan identity

Saved plan:

`infrastructure/environments/development/goal-06-secret-endpoint-execution-role-remediation-20260813.tfplan`

SHA-256:

`2e84c69e612d0c229e7eb916a42c59cd0d475648278dfca104543d585405586a`

## Reviewed action set

The plan contains exactly two non-no-op resource actions:

| Action | Resource | Reviewed effect |
| --- | --- | --- |
| create | `aws_vpc_security_group_ingress_rule.goal6_admin_to_aws_endpoints[0]` | Allows TCP/443 from the dedicated Goal 6 admin task security group to the existing AWS interface-endpoint security group. |
| create | `module.iam.aws_iam_role_policy.task_execution_goal6_secrets[0]` | Adds exact-ARN `secretsmanager:GetSecretValue` for the three Goal 6 container secrets and `kms:Decrypt` for the existing Secrets KMS key to the ECS execution role. |

Terraform summary is `2 to add, 0 to change, 0 to destroy`.

The plan has no replacement or destroy, no ECS task definition or task
execution, no public exposure, no production target, and no Databricks, S3
data, unrelated IAM, KMS, or network action. The plan was created only after
the offline validation and the read-only account/region revalidation.

## Approval boundary

This artifact is evidence for a separate development apply approval. It does
not authorize apply, task retry, bundle/SQL execution, or any other AWS or
Databricks mutation.
