# Goal 6 Phase 6-7 admin refresh — connected execution

Date: `2026-08-18`

Status: `PASS — GOVERNED EXTERNAL READ AND INITIAL INTERNAL REFRESH`

## Approved execution contract

The approved operation was exactly one private ECS Fargate execution of the
Terraform-created admin task definition. It could bootstrap only the dedicated
Doris identities/guardrails, create a temporary Unity Catalog Iceberg REST
catalog, read the single allowlisted Goal 5 source, replace the internal
disposable serving copy, update internal refresh state, and drop the temporary
catalog. No retry was permitted.

| Bound input | Value |
| --- | --- |
| AWS account | `736956442295` |
| Region | `ap-southeast-1` |
| ECS cluster | `ask-david-development-cluster` |
| Task definition | `ask-david-development-doris-admin-refresh:8` |
| Immutable image digest | `sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad` |
| Application subnets | `subnet-034f5f1c9bca753f1`, `subnet-0a1aad220d82ef879` |
| Admin security group | `sg-07a0dd2e8af8aa178` |
| Public IP | `DISABLED` |
| FE / BE | `10.42.64.238` / `10.42.71.97` |
| Databricks workspace | `https://dbc-7f3363e3-d129.cloud.databricks.com` |
| Allowlisted source | `ask_david_development.green_sm_business.goal5_structured_business_metrics` |

The guarded execution wrapper source SHA-256 was
`95f58b26c2210a0cd116cf3f145ba0e2e6ea0d90a0f8327a6bc6c2e87a2cc542`.

## Connected result

| Evidence | Result |
| --- | --- |
| ECS task ID | `40f70181929648a6879ed973fb75bc57` |
| Launch type / platform | `FARGATE` / `1.4.0` |
| Lifecycle | `STOPPED` / desired `STOPPED` |
| Container | `doris-admin`, exit code `0` |
| Start / stop | `2026-08-18T16:57:28.897+07:00` / `2026-08-18T16:57:59.420+07:00` |
| ENI | `eni-04684b2193296bba4` |
| Private subnet | `subnet-034f5f1c9bca753f1` |
| Private IPv4 | `10.42.25.231` |
| CloudWatch stream | `admin/doris-admin/40f70181929648a6879ed973fb75bc57` |
| Completion record | `{"goal":"goal-06","operation":"admin-refresh","status":"completed"}` |
| Running tasks in admin family after inspection | `0` |
| Retry count | `0` |

CloudWatch also contains MariaDB client deprecation/TLS-verification warnings.
They contain no password, OAuth token, client secret, AWS credential, SQL
result, or source data. They did not change the exit status. Future image
maintenance should replace the deprecated `mysql` program name with
`mariadb`; this is not an authorization to change or redeploy the current
admin task.

## What the completed marker proves

The fixed runner emits `completed` only after all earlier commands return
success. Therefore this execution proves that:

1. the private task reached FE `9030` and authenticated to Doris;
2. the intended Databricks OAuth machine identity obtained an access token;
3. Doris created the temporary Unity Catalog Iceberg REST catalog using
   OAuth and credential vending, with no static AWS key;
4. Doris successfully queried the allowlisted
   `DELTA_UNIFORM_ICEBERG` source through that catalog;
5. the internal disposable `serving_metric_daily` copy was truncated and
   reloaded from that source;
6. internal `serving_refresh_state` was updated;
7. the temporary catalog was dropped before the marker was emitted;
8. no Unity Catalog, S3, or authoritative source write statement exists in
   the executed runner/template.

This is actual connected interoperability evidence. It is not inferred from
Databricks table properties alone and it does not claim native Iceberg.

## Phase 6-7 acceptance mapping

| Requirement | Result |
| --- | --- |
| Intended governed catalog connection | PASS |
| Dedicated least-privilege UC source identity | PASS — separately inspected and unchanged |
| Approved source discovery/read | PASS |
| Delta UniForm Iceberg interoperability by real Doris query | PASS |
| No static AWS keys | PASS |
| No source write path | PASS |
| Temporary catalog removed | PASS |
| Source/destination row-count parity | UNVERIFIED — completion alone does not expose both counts |
| Representative source/value parity | UNVERIFIED — requires the separately approved verifier path |

Phase 6-7's fundamental integration blocker is closed. The two parity checks
remain deliberately unclaimed and are carried into the Phase 6-8
representative-result verification.

## Mutation boundary

No Terraform plan/apply/destroy, ECR push, Databricks mutation, Unity Catalog
grant change, S3/source write, public-network change, production operation, or
second ECS task occurred. No secret value was requested or printed.

The next connected mutation boundary is an independently approved immutable
ECR push of the already built/scanned later-phase verifier image. Registering
that digest in ECS remains a separate saved-plan and apply boundary.
