# Goal 6 Doris log-signal classification — saved connected plan

Date: 2026-08-14
Environment: development only
AWS account: `736956442295`
Region: `ap-southeast-1`

## Plan artifact

- Path: `infrastructure/environments/development/goal-06-doris-log-signal-20260814.tfplan`
- SHA-256: `52ec78fc93cc6ada79ed2404a9a04433785022c70817b6b3585738a160f970b0`
- Terraform: `v1.15.8`
- AWS provider: repository-pinned `v6.56.0`

The plan was generated after the previous diagnostics apply and read the
current remote state. No apply, destroy, task run, SQL/job, Databricks bundle
operation, ECR push, volume reset, or out-of-band AWS mutation occurred.

## Exact action inventory

The saved plan reports `4 to add, 0 to change, 4 to destroy`:

- `module.doris_serving.aws_instance.fe[0]` — replace for the new
  Terraform-owned bootstrap source;
- `module.doris_serving.aws_instance.be[0]` — replace for the new
  Terraform-owned bootstrap source;
- `module.doris_serving.aws_volume_attachment.fe[0]` — replace because its
  instance ID follows the FE replacement;
- `module.doris_serving.aws_volume_attachment.be[0]` — replace because its
  instance ID follows the BE replacement.

No `aws_ebs_volume` resource is destroyed. There are no IAM, KMS, network,
security-group, S3, ECR, Databricks, task-definition, public-exposure,
production, or unrelated actions.

## Approval boundary

This plan is not applied. A separate exact SHA-256 approval is required. If
applied, inspect the new coarse `log_signal` values and listener markers before
proposing any persisted-state action. Do not run a task or reset a volume unless
both listeners become ready and a separately reviewed remediation authorizes
the operation.
