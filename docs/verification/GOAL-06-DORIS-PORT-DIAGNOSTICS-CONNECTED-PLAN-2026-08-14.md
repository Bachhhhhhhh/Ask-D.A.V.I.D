# Goal 6 Doris port diagnostics — saved connected plan

Date: 2026-08-14
Environment: development only
AWS account: `736956442295`
Region: `ap-southeast-1`

## Plan artifact

- Path: `infrastructure/environments/development/goal-06-doris-port-diagnostics-20260814.tfplan`
- SHA-256: `0ea48ac9cf50a38a6b83879b5419ed58798528231fb77acba040c9b6e99db86b`
- Terraform: `v1.15.8`
- AWS provider: repository-pinned `v6.56.0`
- Backend: reviewed development S3 backend from ignored `backend.hcl`

The plan performed connected remote-state refresh only and was generated from
the current repository source plus the existing ignored development inputs.
No apply, destroy, task run, SQL/job, Databricks bundle operation, ECR push, or
out-of-band AWS mutation occurred.

## Exact action inventory

The saved plan reports `4 to add, 0 to change, 4 to destroy`:

| Resource | Action | Reason |
| --- | --- | --- |
| `module.doris_serving.aws_instance.fe[0]` | replace | Terraform-owned FE bootstrap/user-data changed |
| `module.doris_serving.aws_instance.be[0]` | replace | Terraform-owned BE bootstrap/user-data changed |
| `module.doris_serving.aws_volume_attachment.fe[0]` | replace | instance ID follows the reviewed FE replacement |
| `module.doris_serving.aws_volume_attachment.be[0]` | replace | instance ID follows the reviewed BE replacement |

The FE and BE encrypted serving-data volumes remain the same Terraform-managed
volume resources; the plan contains no `aws_ebs_volume` destroy, no metadata
reset, and no serving-data deletion. There are no IAM, KMS, network,
security-group, S3, ECR, Databricks, task-definition, public-exposure, or
production actions.

## Approval boundary

This is a saved plan only. Applying it requires a separate exact SHA-256
approval. After apply, inspect the new status-stream
`container-diagnostics-summary` records and the `doris-port-ready` markers for
both FE (`9030`) and BE (`9050`). Do not launch an ECS verifier task unless
both listeners are ready. If diagnostics show an irrecoverable persisted-state
problem, stop and propose a separate declarative rebuild plan; do not reset a
volume implicitly.
