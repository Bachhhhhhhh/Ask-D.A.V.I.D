# Goal 6 Doris listener diagnostics/startup remediation — connected plan evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: connected read-only Terraform refresh and saved-plan review only

## Approval and revalidation

The connected plan step was explicitly approved. Read-only AWS identity
verification returned account `736956442295` as
`arn:aws:iam::736956442295:user/bach_dev_admin_david`; the configured region is
`ap-southeast-1`. The ignored development inputs retain the observed Goal 6
FE/BE private addresses `10.42.69.177` and `10.42.77.49`, the existing data
subnet, and the pinned images. No credentials were printed.

Terraform v1.15.8 refreshed the approved S3 backend state and current
AWS/Databricks provider state. Because the repository lockfile does not contain
the local provider-mirror checksums, the plan was generated in an isolated
validation copy with a temporary lockfile derived from the already-approved
local provider mirror. The source, modules, ignored tfvars, backend settings,
and synthetic fixtures were copied without functional changes. The resulting
plan artifact was copied unchanged into the development root and its SHA-256
was rechecked. No apply, destroy, ECS task, SQL/job, bundle, or ad-hoc cloud
mutation occurred.

## Saved artifact integrity

```text
infrastructure/environments/development/goal-06-doris-listener-diagnostics-remediation-20260814.tfplan
SHA-256: 8f8c674cbe1fe23141c7aedf376c93e4840cfc3d1a2f3a2d571c584c72285cd6
```

The plan was inspected with `terraform show -json`; only action addresses,
actions, replacement paths, and resource counts were retained in this report.

## Exact action set

Terraform reports:

```text
Plan: 4 to add, 0 to change, 4 to destroy.
```

The four actions are the following reviewed replacements:

| Terraform address | Action | Replacement path | Result |
| --- | --- | --- | --- |
| `module.doris_serving.aws_instance.fe[0]` | delete/create | `user_data` | FE bootstrap diagnostics/startup remediation |
| `module.doris_serving.aws_instance.be[0]` | delete/create | `user_data` | BE bootstrap diagnostics/startup remediation |
| `module.doris_serving.aws_volume_attachment.fe[0]` | delete/create | `instance_id` | reattach existing FE data volume |
| `module.doris_serving.aws_volume_attachment.be[0]` | delete/create | `instance_id` | reattach existing BE data volume |

The plan contains 249 resource-change entries, of which exactly four are
non-no-op. FE and BE private IPs remain `10.42.69.177` and `10.42.77.49`.
Existing `/dev/sdf` volumes `vol-012bc3410278ed85e` and
`vol-01e9b0ed05f7b92b9` remain the serving-data volumes; no standalone data
volume deletion or reset is planned.

The review found zero actions for ECS task definitions, IAM, KMS, security
groups, routes/NACLs, S3, ECR, Secrets Manager, Databricks, RDS, Redis,
production, public exposure, or source data. There are no destroy-only actions
and no unexpected replacement paths.

## Review result and next boundary

The action set matches the approved offline listener diagnostics/startup
remediation. This report records plan review only; it does not approve or
perform the plan apply. A separate hash-bound approval is required before
applying this exact artifact. Both replacement hosts must emit
`doris-port-ready` before any Goal 6 verifier task is considered.
