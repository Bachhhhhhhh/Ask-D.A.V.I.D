# Goal 7 AOSS vector upsert task-definition apply — 2026-08-21

## Boundary

The exact saved plan was explicitly approved for apply. No new plan was
generated, and no ECS task, bundle/SQL operation, AOSS mutation, Databricks
mutation, ECR push, or unrelated AWS resource operation was performed.

## Plan and apply evidence

| Attribute | Value |
| --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| Plan artifact | `/tmp/goal7-aoss-vector-upsert-taskdef-20260821.tfplan` |
| Plan SHA-256 | `538bd60db293e0c52fda59793adfa26c541f2fd4397c51de3c04f1f495c03f10` |
| Terraform result | PASS — `1 added, 0 changed, 1 destroyed` |
| Managed resource | `module.goal7_indexer.aws_ecs_task_definition.this[0]` only |
| New revision | `ask-david-development-goal7-indexer:4` |
| Old revision | `:3` is INACTIVE |
| Running indexer tasks after apply | `[]` |

## Read-only task-definition inspection

Revision `:4` is ACTIVE, Fargate/`awsvpc`, and uses:

- image digest `sha256:bd3b9f2afd102cf165ee6b303fd973b228233d72406967d81c3b616e2f350b5e`;
- command `python -m ask_david_goal7.indexer`;
- existing ECS workload and execution roles;
- existing Goal 7 private runtime log group and workflow OAuth secret reference;
- existing approved catalog, AOSS endpoint/index, warehouse, and HTTPS workspace
  host settings.

No task was started by this apply. The one-shot private indexer run remains a
separate approval boundary.

## Current checkpoint

The corrected task definition is deployed, but Goal 7 remains **UNVERIFIED**.
The next required approval is for exactly one private, no-retry indexer task
using revision `:4`, followed only by immediate read-only ECS/ENI/CloudWatch
inspection. If that task fails, no retry is authorized without review.
