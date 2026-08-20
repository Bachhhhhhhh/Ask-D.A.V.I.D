# Goal 6 RBAC schema-ordering correction — connected admin refresh

Date: 2026-08-19
Status: **PASS — SCHEMA-BEARING REVISION 10 COMPLETED; RBAC NOT RETRIED**

## Approved execution contract

| Bound input | Value |
| --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| ECS cluster | `ask-david-development-cluster` |
| Task definition | `ask-david-development-doris-admin-refresh:10` |
| Image digest | `sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6` |
| Private application subnets | `subnet-034f5f1c9bca753f1`, `subnet-0a1aad220d82ef879` |
| Admin security group | `sg-07a0dd2e8af8aa178` |
| Public IP | `DISABLED` |
| FE / BE | `10.42.64.238` / `10.42.71.97` |

Pre-run inspection confirmed account `736956442295`, region
`ap-southeast-1`, both expected FE/BE instances running, the exact ACTIVE
revision/image/Fargate contract, and no existing RUNNING admin task.

## Connected result

| Evidence | Result |
| --- | --- |
| ECS task | `c08352df6d7846128c7852e3d130b700` |
| Lifecycle | STOPPED / desired STOPPED |
| Container exit | `0` |
| Launch type / platform | Fargate / `1.4.0` |
| Private network | subnet `subnet-0a1aad220d82ef879`, IP `10.42.47.44` |
| Ephemeral ENI | `eni-098e9bbf7734f2bb6`, deleted after stop |
| CloudWatch stream | `admin/doris-admin/c08352df6d7846128c7852e3d130b700` |
| Completion marker | `{"goal":"goal-06","operation":"admin-refresh","status":"completed"}` |
| Retry count | `0` |
| RUNNING admin tasks after inspection | `0` |

The fixed runner is fail-fast and emits `completed` only after executing the
version-controlled schema files, applying the query-only grants/properties,
creating and reading the temporary allowlisted Unity Catalog Iceberg REST
catalog, reloading the internal disposable serving table, updating refresh
state, and dropping the temporary catalog. Consequently the schema-bearing
revision has now applied `CREATE TABLE IF NOT EXISTS` for
`goal6_authorization_probe`, closing the ordering defect that caused the prior
RBAC task to fail before its privilege check.

## Boundary

No RBAC retry, second ECS task, Terraform operation, ECR push, Databricks
mutation, Unity Catalog/S3/source write, public networking, or production
operation occurred. The corrected live precondition is present, but Phase
6-11 remains unverified until one separately approved revision-10 RBAC task
completes with all seven authorization denials.

The separately approved RBAC retry subsequently confirmed authorization-layer
denials for `INSERT` and `UPDATE`, then stopped at `DELETE` because Doris
constant-folded `WHERE FALSE` to an empty no-op before its LOAD privilege
check. No row was deleted, but this is not denial evidence. See
`GOAL-06-RBAC-REVISION-10-RETRY-FAILURE-2026-08-19.md`.
