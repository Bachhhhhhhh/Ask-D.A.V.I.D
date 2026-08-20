# Goal 6 admin global-grant remediation — task-definition apply

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **PASS — NEW TASK-DEFINITION REVISIONS ACTIVE**

## Approved saved-plan apply

The project owner approved the exact saved plan with SHA-256:

```text
1f4b654bce71c95beed62d2ca3dc39a08a8c6dbca7fdaeee6798450a65ce68ad
```

Immediately before apply, the hash, approved account, preceding revision-7
image/commands, and absence of running ECS tasks were revalidated. Terraform
applied the saved artifact only and reported:

```text
Apply complete! Resources: 2 added, 0 changed, 2 destroyed.
```

The delete/create form is the reviewed ECS task-definition revision replacement:
Terraform registered the two revision-8 definitions and retired its revision-7
resource state. It did not launch a task.

## Read-only post-apply inspection

| Family | Active revision | Runtime contract | Command |
| --- | --- | --- | --- |
| `ask-david-development-doris-admin-refresh` | `:8` | Fargate, `awsvpc`, CPU `512`, memory `1024`, task-level entrypoint `null` | `/app/doris-admin-refresh` |
| `ask-david-development-doris-verifier` | `:8` | Fargate, `awsvpc`, CPU `512`, memory `1024`, task-level entrypoint `null` | `/app/doris-readonly-verify` |

Both container definitions use only:

```text
736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier@sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad
```

Immediate ECS inspection found zero running task ARNs in
`ask-david-development-cluster`.

There was no apply effect on IAM, KMS, Secrets Manager, network/security
groups, ECR image content, S3, EC2/EBS, Doris hosts, Databricks, Unity Catalog,
source data, SQL, production, or public exposure.

## Next approval boundary

The corrected admin runner is now deployed but unexecuted. One separately
approved private admin-refresh task from revision `:8` is required to validate
the governed Unity Catalog Iceberg REST path and disposable serving refresh.
It must use the existing private application subnets and admin security group,
assign no public IP, and stop without retry on any failure.
