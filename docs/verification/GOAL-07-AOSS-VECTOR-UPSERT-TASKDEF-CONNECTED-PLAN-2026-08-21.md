# Goal 7 AOSS vector upsert task-definition plan — 2026-08-21

## Boundary

This checkpoint was approved for updating the ignored development indexer
digest and creating/reviewing one saved connected Terraform plan. The plan was
not applied. No ECS task, bundle/SQL operation, AOSS mutation, Databricks
mutation, ECR push, or unrelated AWS resource operation occurred in this
checkpoint.

## Inputs and revalidation

| Check | Result |
| --- | --- |
| AWS account | PASS — `736956442295` |
| AWS region | PASS — `ap-southeast-1` |
| Databricks development profile | PASS — `ask-david-development`, valid |
| Goal 7 gate | `goal_7_enabled=true`, `goal_7_indexer_task_enabled=true` |
| Indexer digest input | Updated only in ignored `terraform.tfvars` to `sha256:bd3b9f2afd102cf165ee6b303fd973b228233d72406967d81c3b616e2f350b5e` |
| Demo digest input | Unchanged — `sha256:c854fe57c92ad16be5cdb9935cfa16736164749a9812c9183157ad9417fae84f` |
| Offline preflight/static validation | PASS |

## Saved plan

| Attribute | Value |
| --- | --- |
| Plan artifact | `/tmp/goal7-aoss-vector-upsert-taskdef-20260821.tfplan` |
| Plan SHA-256 | `538bd60db293e0c52fda59793adfa26c541f2fd4397c51de3c04f1f495c03f10` |
| Create actions | `1` |
| Delete actions | `1` |
| Update actions | `0` |
| No-op resources | `278` |
| Replacement address | `module.goal7_indexer.aws_ecs_task_definition.this[0]` |

The replacement changes only the task-definition image from the previous
indexer digest to the newly promoted digest. The command remains
`python -m ask_david_goal7.indexer`; the existing private subnets, task role,
execution role, workflow OAuth secret reference, log group, and Goal 7
networking are unchanged. There are no Goal 6, production, public-exposure,
Databricks, AOSS, IAM, KMS, S3, or other resource actions.

## Current checkpoint

This plan is saved and reviewed but not applied. Goal 7 remains
**UNVERIFIED**. The next separate approval must name this exact plan SHA-256
before any apply. After apply, a separate approval is required for exactly one
private no-retry indexer task and read-only ECS/ENI/CloudWatch inspection.
