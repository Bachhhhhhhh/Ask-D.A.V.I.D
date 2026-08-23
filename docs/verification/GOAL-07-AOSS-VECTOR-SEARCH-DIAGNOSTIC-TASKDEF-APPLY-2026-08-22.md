# Goal 7 AOSS vector-search diagnostic task-definition apply — 2026-08-22

## Boundary

The explicitly approved saved Terraform plan was applied. The operation was
limited to replacing the Goal 7 private indexer task definition with the
diagnostic image. No ECS task was run and no other AWS, Databricks, Terraform,
ECR, SQL, or AOSS data-plane operation was performed.

## Apply evidence

| Field | Result |
| --- | --- |
| Account / region | `736956442295` / `ap-southeast-1` |
| Saved plan SHA-256 | `1183b9227664a27df56a7dbc584f0b29fe9523344adc48e2c5a49d5397af459c` |
| Terraform result | `1 added, 0 changed, 1 destroyed` |
| New task definition | `ask-david-development-goal7-indexer:8` |
| Image digest | `sha256:1be0e8d301f136230795d16bc086a0a90823646f4ca239155924ca13837e5779` |
| Entrypoint | `python -m ask_david_goal7.indexer` |
| Runtime | Fargate / `awsvpc` / CPU 512 / memory 1024 |
| Running indexer tasks after apply | `[]` |

Immediate read-only inspection confirmed revision 8 is `ACTIVE`, uses the
expected immutable digest, and retains the existing private runtime log group.

## Next approval boundary

Run exactly one private no-retry indexer task from revision 8, using the
existing Goal 7 private subnets/security group and `assignPublicIp=DISABLED`.
After it stops, inspect only ECS/ENI/CloudWatch results. If it fails, stop for
review without retry.
