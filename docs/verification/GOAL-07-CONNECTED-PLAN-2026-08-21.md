# Goal 7 connected development Terraform plan — 2026-08-21

## Status

**SAVED PLAN CREATED AND REVIEWED — NO APPLY**

This checkpoint performed the separately approved connected development state
refresh and created one local saved Terraform plan. It did not apply or
destroy resources, run an ECS task, create an OpenSearch index, execute
Databricks SQL, deploy a bundle, or mutate Databricks resources outside the
single planned service-principal-secret create.

## Identity and environment

- AWS account: `736956442295`
- AWS region: `ap-southeast-1`
- AWS principal: `arn:aws:iam::736956442295:user/bach_dev_admin_david`
- Databricks workspace observed in refreshed state: `7474644358733471`
- Existing Unity Catalog metastore observed in refreshed state:
  `3a7f7e7a-680b-4bd6-907a-6d5e77b43178`
- Existing SQL warehouse observed in refreshed state:
  `757e0335c6efb51e`

## Saved artifact

- plan: `/tmp/goal7-connected-plan.cvxyDv/goal-07-development.tfplan`
- Terraform data directory: `/tmp/goal7-connected-tfdata.ALbPYb`
- SHA-256:
  `05b8bf41457d2093d0fc4230779b2e612fb120453c6b359e2d1e7e7a34309e31`
- repository-local Terraform state/cache: not modified

The plan artifact and temporary Terraform data are local ignored files and
must not be committed.

## Terraform action summary

`8 to add, 0 to change, 0 to destroy`; no replacement actions were present.

| Address | Action | Purpose |
| --- | --- | --- |
| `aws_secretsmanager_secret_version.goal7_workflow_oauth[0]` | create | Populate the Terraform-managed workflow OAuth secret version |
| `aws_vpc_security_group_ingress_rule.goal7_demo_to_doris[0]` | create | Private Goal 7 demo SG to Doris FE TCP/9030 |
| `aws_vpc_security_group_ingress_rule.goal7_indexer_to_aoss[0]` | create | Private Goal 7 indexer SG to AOSS endpoint TCP/443 |
| `module.databricks_identities.databricks_service_principal_secret.workflow[0]` | create | Terraform-managed short-lived workflow service-principal secret |
| `module.goal7_demo.aws_ecs_task_definition.this[0]` | create | Gated integrated-demo ECS task definition |
| `module.goal7_indexer.aws_ecs_task_definition.this[0]` | create | Gated private indexer ECS task definition |
| `module.iam.aws_iam_role_policy.task_execution_goal7_secrets[0]` | create | Least-privilege ECS execution-role secret read/decrypt policy |
| `module.secrets.aws_secretsmanager_secret.this["goal7/workflow-oauth"]` | create | KMS-encrypted workflow OAuth secret container |

## Negative action review

The saved plan JSON was filtered independently from the human-readable plan.

- Goal 6 EBS volume or attachment action: **0**
- Goal 6 EC2/user-data action: **0**
- replacement: **0**
- destroy: **0**
- unrelated AWS resource action: **0**
- OpenSearch collection/index mutation: **0**
- metastore/workspace-assignment/warehouse/cluster action: **0**
- public exposure or public CIDR action: **0**
- production action: **0**
- real Green SM data action: **0**

The only Databricks action is the explicitly reviewed workflow service-
principal-secret create. No bundle deployment, job run, SQL run, or task was
performed.

## Verification commands

- AWS STS identity check: **PASS**
- `python3 scripts/dev.py infra-preflight`: **PASS**
- Terraform backend/module/provider initialization with lockfile readonly:
  **PASS**
- connected Terraform saved plan: **PASS**
- saved-plan SHA-256 calculation: **PASS**
- filtered saved-plan JSON action review: **PASS**

## Next approval boundary

Apply is not authorized by this checkpoint. A separate approval must bind to
the exact SHA-256
`05b8bf41457d2093d0fc4230779b2e612fb120453c6b359e2d1e7e7a34309e31` and the
eight-create action set above. Before apply, reverify AWS account/region and
the saved artifact hash. After apply, perform only the approved read-only
resource inspection; do not run the indexer or integrated demo until those
checks pass and each task has its own approval.
