# Goal 7 corrected indexer task-definition plan

## Boundary

This is a saved connected development Terraform plan only. Terraform refreshed
the approved AWS/Databricks development state and wrote a local plan artifact.
No AWS resource was mutated, no ECS task ran, and no ECR, Databricks, SQL,
bundle, or AOSS operation was performed.

## Revalidation

- AWS account: `736956442295` — PASS
- Region: `ap-southeast-1` — PASS from Terraform refresh
- Environment: development only
- Prior drifted plan: rejected and not applied

## Saved plan

- Artifact: `/tmp/goal7-aoss406-taskdef-20260821-r2.tfplan`
- SHA-256: `e75cc08ab828779e98ee54f821ed3e83f4c1469de987c36df9560d66eed33712`
- Source image digest:
  `sha256:56263b9c594825f1509f305bb9911b499acd944dcc9971731d04dc18b530a641`

Machine-readable inspection of the saved plan reported:

| Action | Count |
| --- | ---: |
| create | 1 |
| delete | 1 |
| update | 0 |
| no-op | 278 |

The sole non-no-op address is:

`module.goal7_indexer.aws_ecs_task_definition.this[0]`

It is the expected ECS task-definition replacement (`delete` + `create`) to
register the corrected digest. There are zero SG, EBS, IAM, KMS, network,
Databricks, AOSS, production, public-exposure, or unrelated resource actions.

## Decision boundary

This plan is eligible for a separate explicit apply approval. It has not been
applied. After apply approval, only this exact hash-bound plan may be applied;
the next separate boundary is one private no-retry indexer task run.
