# Goal 6 later-phase verifier task-definition apply

Date: `2026-08-18`
Environment: development only
Status: **APPLY PASS — NO ECS TASK RUN**

## Reviewed saved plan

- AWS account: `736956442295`
- Region: `ap-southeast-1`
- Saved-plan SHA-256:
  `66f28c1c5b646637dd70536238c8cb69db2cad84a7a378fe0f737769ac87dcb9`
- Immutable image digest:
  `sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510`

Identity was reverified immediately before apply as AWS account
`736956442295` in `ap-southeast-1`; the saved-plan hash matched the reviewed
artifact.

The plan contained exactly two replacements, both caused only by
`container_definitions`:

| Task-definition family | Planned action | Result |
| --- | --- | --- |
| `ask-david-development-doris-admin-refresh` | replacement/revision registration | PASS — revision `9` ACTIVE |
| `ask-david-development-doris-verifier` | replacement/revision registration | PASS — revision `9` ACTIVE |

Terraform reported `2 added, 0 changed, 2 destroyed`. For ECS task-definition
resources, this is the provider's registration of a new revision and
deregistration of the prior Terraform-owned revision; it is not an ECS task
run and does not replace EC2, EBS, networking, or persistent Doris state.

## Post-apply read-only inspection

Both active revision-9 definitions confirm:

- Fargate `512` CPU / `1024` MiB;
- `awsvpc` network mode;
- the reviewed immutable image digest;
- unchanged executable commands:
  `/app/doris-admin-refresh` and `/app/doris-readonly-verify`;
- admin secret-reference names limited to the existing admin, OAuth, and query
  containers; verifier secret-reference name limited to the existing query
  container.

`list-tasks` found no `RUNNING` task for either family in
`ask-david-development-cluster`.

## Scope confirmation

No IAM, KMS, security-group, route, VPC endpoint, ECR repository/image push,
EC2, EBS, S3, Databricks, warehouse, SQL, bundle, public-exposure, or
production action was present in the saved plan or apply output.

## Next approval boundary

The next operation is a separately approved, exactly-one private read-only
verifier task for a specific operation (`readonly`, `rbac`, or `query-limit`).
This apply does not authorize task execution, an authoritative refresh,
Databricks SQL, or any further Terraform action.
