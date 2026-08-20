# Goal 6 non-empty DELETE probe task-definition apply — 2026-08-19

## Scope

Apply the separately approved, digest-bound development plan that registers
only updated ECS task definitions for the controlled Goal 6 RBAC remediation.
No task execution was approved or performed.

## Preconditions reverified

| Check | Result |
| --- | --- |
| Saved-plan SHA-256 | PASS — `b7be4075a42d0bf93408ed7d2468a44e150a38f022f8b987fb730084c555e716` |
| AWS account | PASS — `736956442295` |
| AWS Region | PASS — `ap-southeast-1` |
| Approved image digest | PASS — `sha256:b2a4629e1e207fa9b2d06cdca5956472f6e4f94e4f40723a5bc45f1a18b17a73` |

## Applied result

Terraform applied the reviewed saved plan directly and reported:

```text
Apply complete! Resources: 2 added, 0 changed, 2 destroyed.
```

The destroy/create pairs are ECS task-definition revision registration only:

| Resource | Prior revision | Active revision | Result |
| --- | ---: | ---: | --- |
| `ask-david-development-doris-admin-refresh` | 12 | 13 | PASS |
| `ask-david-development-doris-verifier` | 12 | 13 | PASS |

No replacement or mutation occurred for IAM, KMS, networking, security groups,
EC2, EBS, ECR, S3, Databricks, public resources, or production resources.

## Read-only post-apply inspection

Both revision `13` definitions are ACTIVE and retain:

- `awsvpc` network mode and Fargate compatibility;
- `512` CPU and `1024` MiB memory;
- the existing distinct least-privilege admin and verifier task roles;
- the exact approved ECR image digest.

The cluster had zero RUNNING tasks for both families immediately after apply.
No ECS task, Doris SQL, Databricks operation, or additional Terraform command
was executed after this inspection.

## Current checkpoint

This apply does not seed the disposable sentinel rows and does not validate
RBAC. The next action requires separate approval for one private admin-refresh
task using revision `13`; only after it succeeds may a revision-13 RBAC
verifier run be considered for separate approval.
