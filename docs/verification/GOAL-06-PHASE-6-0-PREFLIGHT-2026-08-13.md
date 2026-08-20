# Goal 6 Phase 6-0 preflight

Date: 2026-08-13
Scope: read-only development preflight for the Apache Doris serving-layer goal.

## Safety boundary

No AWS, Databricks, Unity Catalog, Doris, Terraform, SQL warehouse, bundle, or
job mutation occurred. The AWS CLI and Databricks CLI were used only for the
read-only inspections recorded below. No credential, token, secret value, or
source-object content was retrieved.

## Result

| Prerequisite | Result | Evidence |
| --- | --- | --- |
| Goal 5 health | PASS | Immutable evidence commit `9c0d67b30db96a24d015c9cb79821b2fbb107f23`; its final zero-drift plan and successful workflow are recorded in [Goal 5 final verification](GOAL-05-FINAL-VERIFICATION-2026-08-13.md). |
| AWS identity and account | PASS | Read-only STS returned account `736956442295` for the approved development administrator. |
| AWS region | PASS | All AWS inspection used `ap-southeast-1`; the attached UC metastore also reports that region. |
| Databricks authentication and workspace | PASS | Databricks CLI `1.11.0`, profile `ask-david-development`, and the authenticated development governance administrator are valid. The attached workspace ID is `7474644358733471`. |
| Unity Catalog metastore | PASS | Workspace `7474644358733471` is attached to metastore `3a7f7e7a-680b-4bd6-907a-6d5e77b43178`, named `metastore_aws_ap_southeast_1`; it reports `external_access_enabled: true` and region `ap-southeast-1`. |
| Project isolation | PASS | `ask_david_development` remains an isolated, development-only catalog bound read/write only to workspace `7474644358733471`. System/sample/workspace catalogs were inspected but not changed. |
| Candidate source data | PASS WITH DISCLOSURE | All nine Goal 5 tables are Unity Catalog `MANAGED`, `data_source_format=DELTA`, with `delta.enableIcebergCompatV2=true`, `delta.universalFormat.enabledFormats=iceberg`, approved S3 `_iceberg/metadata` paths, and `HAS_DIRECT_EXTERNAL_ENGINE_READ_SUPPORT`. They are **DELTA_UNIFORM_ICEBERG**, not native Iceberg. |
| Unity Catalog external-read feasibility | PASS IN PRINCIPLE | Databricks documents Iceberg REST read access for managed Delta tables with Iceberg reads enabled. The current metastore has external access enabled. A dedicated principal and scoped `EXTERNAL USE SCHEMA` grants do not yet exist, so a real Doris query remains unverified. |
| Secure machine authentication feasibility | PASS IN PRINCIPLE | Databricks documents OAuth for Iceberg REST; Doris documents OAuth2 plus vended credentials from 3.1.0 onward. No personal PAT or static AWS key is proposed. A secret reference/delivery design remains to be implemented and tested. |
| Existing Doris resources | PASS | Read-only AWS inventory found no Doris ECS task definition/service, EC2 instance, ECR repository, security group, or EBS volume. Databricks has no service principal whose display name contains `doris`. |
| Private verification execution path | PASS WITH DESIGN WORK REQUIRED | Existing Goal 3B Fargate smoke infrastructure proves private task launch in application subnets with no public IP, but it is explicitly restricted to the three Goal 3B smoke checks and has no usable egress/permissions for Doris verification. A separate, Terraform-managed ephemeral Fargate verifier is required; no public path or bastion is justified. |
| Current Doris/Unity Catalog interoperability | UNVERIFIED | Required proof is an actual connected Doris query against an approved Delta UniForm Iceberg source. No Doris deployment exists yet, so this has not and must not be inferred from metadata. |

## Candidate source allowlist

The initial design must limit Doris to the smallest set of governed synthetic
sources. All timestamps below are table API `updated_at` values; the row counts
are current catalog statistics, not a substitute for a connected source-count
comparison.

| Candidate | Format | Approx. rows | Neutral dimensions / metrics | Initial use |
| --- | --- | ---: | --- | --- |
| `ask_david_development.green_sm_business.goal5_structured_business_metrics` | DELTA_UNIFORM_ICEBERG | 2 | `metric_date`, `category`; `event_count`, `metric_total`; `transformed_at` | Primary allowlisted source for `serving_metric_daily` / `serving_metric_by_dimension`. |
| `ask_david_development.green_sm_curated.goal5_structured_curated_events` | DELTA_UNIFORM_ICEBERG | 2 | `event_time`, `category`, `entity_id`; `metric_value`; `curated_at` | Optional justified detail source for a neutral entity/activity mart. Not exposed by default. |
| `ask_david_development.green_sm_curated.goal5_cdc_current_state` | DELTA_UNIFORM_ICEBERG | 2 | `entity_id`, `operation_applied`, `event_time`, `sequence`; `updated_at` | Optional incremental-refresh marker/source; not a source of authority. |
| `ask_david_development.green_sm_platform.goal5_ingestion_runs` | DELTA_UNIFORM_ICEBERG | 8 | dataset/run/status/count/timestamps | Optional freshness and refresh provenance only. |
| `ask_david_development.green_sm_platform.goal5_quality_results` | DELTA_UNIFORM_ICEBERG | 11 | dataset/rule/status/check timestamp | Optional quality provenance only. |

The Raw, quarantine, document-metadata, and CDC-history tables are not in the
initial serving allowlist. They remain governed lakehouse objects and are not
made discoverable to Doris by default.

## External-access baseline

- The project managed-storage credential is
  `ask-david-development-managed-iceberg`, using the Terraform-managed AWS IAM
  role `ask-david-development-unity-catalog-storage`. It is isolated to the
  development workspace.
- The project’s catalog and managed schema locations are isolated and use only
  approved Goal 3 S3 prefixes. No new AWS Glue or Hive Metastore exists.
- Current schema grants cover existing engineering/business-reader groups.
  They contain no `EXTERNAL USE SCHEMA` grant for a Doris principal.
- Current workspace service principals are the Goal 4 workflow principal, the
  denied-test principal, and an unrelated MLOps principal. No dedicated Doris
  external-read principal exists.

## Official compatibility research

- [Databricks: Access tables from Apache Iceberg clients](https://docs.databricks.com/aws/en/external-access/iceberg)
  specifies the Unity Catalog Iceberg REST endpoint, requires metastore
  external access, `EXTERNAL USE SCHEMA`, and OAuth/PAT authentication, and
  explicitly permits read-only access to managed Delta tables with Iceberg
  reads enabled.
- [Databricks: credential vending](https://docs.databricks.com/aws/en/external-access/credential-vending)
  describes short-lived table/path credentials that inherit the configured
  principal's privileges. It requires reachable workspace and storage URLs.
- [Databricks: Unity Catalog integrations](https://docs.databricks.com/aws/en/external-access/integrations)
  lists Doris as an Iceberg REST catalog integration.
- [Apache Doris: Iceberg REST Catalog API](https://doris.apache.org/docs/3.x/lakehouse/metastores/iceberg-rest/)
  documents OAuth2, credential vending, and a Databricks Unity Catalog Iceberg
  REST configuration. OAuth2 and vended credentials are supported from Doris
  3.1.0 onward.
- [Apache Doris: Iceberg Catalog](https://doris.apache.org/docs/4.x/lakehouse/catalogs/iceberg-catalog/)
  documents REST catalog support and the Iceberg SDK mapping for current Doris
  releases. The chosen configuration must explicitly prevent Doris source
  writes despite the engine supporting some Iceberg write operations.

## Private execution-path conclusion

The verified Goal 3B pattern is an ECS Fargate task in private application
subnets with `assignPublicIp=DISABLED`, a dedicated security group, and
CloudWatch Logs evidence. It proves the selected VPC can host an approved
private verifier, but its task definitions, IAM role, and smoke security group
are intentionally Goal-3B-specific. Goal 6 must define a separate verifier
and narrowly allow only DNS, HTTPS to the Databricks workspace/S3 path, and the
future private Doris SQL endpoint. The Codex host will use the ECS control
plane and read CloudWatch evidence; it will not directly connect to Doris.

## Stopping condition and next action

Phase 6-0 is complete. No fundamental account, region, metastore, source-format,
or security mismatch was found. The next action is Phase 6-1: produce the
development deployment and integration design, including a cost/topology
comparison and a concrete private-verifier design. Provisioning, privileges,
secrets, Terraform connected plans, and any Doris query remain unauthorized.
