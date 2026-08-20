# Goal 6 persisted Doris IP remediation — connected plan evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: connected read-only refresh and saved Terraform-plan review; no apply

## Revalidation

The approved connected-plan step reverified AWS account `736956442295` as the
development identity and region `ap-southeast-1`. The current ignored Goal 6
inputs are FE `10.42.64.238` and BE `10.42.71.97`. The existing S3 backend was
used only for state refresh and state locking; no resource mutation occurred.

## Saved artifact integrity

```text
infrastructure/environments/development/goal-06-doris-persisted-ip-remediation-20260814.tfplan
SHA-256: c7d1368001470bff744d38eb50e6dfb77e6b1f40a7a1a10a1d70c33112cca83e
```

The artifact was generated in an isolated validation copy with the same
repository source, ignored development inputs, backend configuration, and
provider versions. It was copied unchanged into the development root and the
source and repository hashes match exactly. The plan file is ignored by Git;
no state, credential, or plan artifact is tracked.

## Exact action set

Terraform output reports:

```text
Plan: 6 to add, 0 to change, 6 to destroy.
```

The output contains exactly these six replacement addresses and no other
resource action headers:

| Address | Replacement reason | Preserved scope |
| --- | --- | --- |
| `module.doris_serving.aws_instance.fe[0]` | private IP `10.42.69.177` → `10.42.64.238` and rendered expected-IP bootstrap data | same pinned FE image, instance type, private subnet, encrypted root/data design |
| `module.doris_serving.aws_instance.be[0]` | private IP `10.42.77.49` → `10.42.71.97` and rendered expected-IP bootstrap data | same pinned BE image, instance type, private subnet, encrypted root/data design |
| `module.doris_serving.aws_volume_attachment.fe[0]` | new FE instance ID | existing encrypted FE metadata volume reattached at `/dev/sdf` |
| `module.doris_serving.aws_volume_attachment.be[0]` | new BE instance ID | existing encrypted BE serving-data volume reattached at `/dev/sdf` |
| `module.doris_verifier.aws_ecs_task_definition.admin[0]` | `DORIS_FE_HOST`/`DORIS_BE_HOST` environment values | same task family, image, roles, secrets, network mode, and command |
| `module.doris_verifier.aws_ecs_task_definition.verifier[0]` | `DORIS_FE_HOST` environment value | same task family, image, role, secret, network mode, and command |

There are zero in-place updates, zero destroy-only actions, and zero
unrelated actions for IAM, KMS, security groups, routes/NACLs, S3, ECR,
Secrets Manager, CloudWatch, RDS, Redis, Databricks, production, or public
exposure. The plan does not delete or recreate either role data volume; only
the volume attachments are replaced. Root volumes of replaced instances obey
the existing reviewed `delete_on_termination` behavior.

## Review result and approval boundary

The action set matches the offline persisted-IP remediation design. This report
does not approve apply. A separate hash-bound approval is required before
applying this exact artifact. After apply, recheck both private IPv4 addresses,
volume attachments, EC2 health, and FE/BE `doris-port-ready` markers before any
Goal 6 verifier task. If the BE listener still fails, stop and design a
declarative metadata migration/rebuild; do not erase the persisted volume.
