# Goal 7 AOSS diagnostic indexer task-definition connected plan — 2026-08-22

## Boundary

The ignored development image digest was updated to the already-pushed
diagnostic image. A connected Terraform plan was created and inspected. No
apply, ECS task run, ECR push, Databricks, SQL, AOSS data-plane, or unrelated
AWS mutation was performed.

## Plan evidence

| Field | Value |
| --- | --- |
| Account / region | `736956442295` / `ap-southeast-1` |
| Plan artifact | `/tmp/goal7-indexer-aoss-diagnostics-taskdef-20260822.tfplan` |
| Plan SHA-256 | `1183b9227664a27df56a7dbc584f0b29fe9523344adc48e2c5a49d5397af459c` |
| Current revision | `ask-david-development-goal7-indexer:7` |
| New image digest | `sha256:1be0e8d301f136230795d16bc086a0a90823646f4ca239155924ca13837e5779` |
| Expected actions | exactly one ECS task-definition replacement (`delete,create`) |
| Other AWS/Databricks actions | `0` |
| EBS, EC2, network, IAM, KMS, S3, AOSS collection | unchanged / `0` actions |

The plan is saved and unchanged. It is not approved for apply by this report.

## Next approval boundary

Apply only this exact saved plan after explicit approval. After apply, perform
read-only task-definition inspection; running the private indexer remains a
separate one-shot approval and must not be implicit.
