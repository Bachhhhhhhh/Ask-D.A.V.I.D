# Goal 6 Doris serving-state rebuild — offline remediation

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: offline implementation and validation only; no connected plan or AWS
mutation has been performed for this change

## Trigger

The approved log-signal apply preserved the existing encrypted FE metadata and
BE serving-data volumes, but both containers still failed their private
listeners. FE reported a coarse `metadata` signal and BE a `configuration`
signal. This is sufficient to justify a disposable serving-state rebuild
design, but it is not proof that either old volume is irrecoverable.

Apache Doris documents metadata recovery as a specialist operation that can
cause metadata truncation or split-brain. This remediation therefore does not
enable `metadata_failure_recovery`, delete metadata, format a volume, or run a
task. The authoritative lakehouse remains outside the Doris volumes.

## Declarative remediation

The Goal 6 Terraform module now has an explicit, default-off
`rebuild_serving_state` gate. When enabled in a separately reviewed
development plan it will:

- create one new encrypted gp3 FE metadata volume and one new encrypted gp3 BE
  serving-state volume in the existing private data subnet/AZ;
- preserve the previously managed FE and BE volumes with
  `prevent_destroy = true` and no reformat/delete operation;
- replace only the FE/BE hosts and volume attachments needed to mount the new
  empty serving volumes, while retaining private IPs, instance sizing, root
  storage, security groups, IAM, KMS, and no-public-IP posture;
- keep the existing no-task-before-`doris-port-ready` guard;
- leave the old volumes detached but Terraform-managed for later read-only
  evidence or a separately approved cleanup decision.

This is a rebuild of disposable Doris serving state, not a rebuild of S3,
Unity Catalog, Databricks, or authoritative lakehouse data. No source write
path is introduced.

## Offline evidence

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| Goal 6 static/regression pytest subset | PASS |
| Rendered FE/BE bootstrap `bash -n` | PASS |
| Python compilation | PASS |
| Terraform format/validation with backend disabled | PASS when local provider mirror is available |
| `git diff --check` | PASS |

No Terraform connected plan/apply/destroy, AWS/Databricks operation, volume
reset, metadata recovery, ECS task, SQL/job, bundle, or ECR operation occurred
for this offline remediation.

## Approval boundary

Before any mutation, create and inspect one saved development Terraform plan
with `goal_6_rebuild_serving_state=true`. The plan must show exactly the
reviewed new encrypted FE/BE data-volume creates plus the required FE/BE host
and attachment replacements. It must show zero old-volume deletes, zero
replacement/destroy of IAM/KMS/network/S3/ECR/Databricks/production resources,
zero public exposure, and zero task-definition or task-run actions. A separate
hash-bound approval is required before applying that exact plan.

After apply, inspect both private IPs, volume IDs/attachments, encryption and
`DeleteOnTermination=false`, EC2 health, and the two persisted
`doris-port-ready` markers. Do not launch any verifier task unless both
markers pass.
