# Goal 6 admin global-grant remediation — ECR push

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **PASS — EXACT SCANNED IMAGE PUSHED**

## Approved artifact

| Property | Value |
| --- | --- |
| Source aggregate | `ad0056f26ac2901410075224e57ae1406c5cfe2405e6374280bf44dbb1dd423b` |
| Local image ID | `sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad` |
| Repository | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier` |
| Immutable tag | `goal6-admin-priv-ad0056f2` |

Before push, the account identity was revalidated as `736956442295`, the
source aggregate and local image ID were exact matches, and the target tag was
absent. Docker authenticated to ECR through stdin only; no credential value was
printed. It logged out after remote inspection.

## Result

The only mutation was ECR image/blob upload. Immediate read-only ECR inspection
reported:

| Field | Value |
| --- | --- |
| Image digest | `sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad` |
| Tag | `goal6-admin-priv-ad0056f2` |
| Media type | `application/vnd.oci.image.index.v1+json` |
| Size | `17,886,363` bytes |

The remote digest matches the approved local image ID. No Terraform plan/apply,
ECS task execution, task-definition update, SQL, Databricks, Unity Catalog, S3,
IAM, KMS, network, source-data, production, or other AWS resource mutation
occurred.

## Next approval boundary

The active Fargate task definitions still reference their preceding verifier
image. A separately approved ignored-tfvars update and saved Terraform plan may
propose only the two expected task-definition revision registrations for the
digest above. That plan must be reviewed before any apply. Another admin-refresh
execution requires separate approval after an approved task-definition apply.
