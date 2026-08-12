# Goal 4 Phase 4-0 connected read-only preflight — 2026-08-10

## Scope

This report records read-only discovery for Goal 4 in the existing Databricks
development workspace and the verified Goal 3 AWS development account. It does
not authorize or record a Goal 4 implementation.

No Databricks or AWS persistent resource was created, updated, replaced, or
deleted. No Terraform init, plan, apply, or destroy ran. No catalog, schema,
table, storage credential, external location, identity, grant, binding,
workflow, or cluster was created. Two read-only SQL statements ran on the
existing serverless SQL warehouse to verify the metastore and DBSQL version.

## Architecture boundary

- Unity Catalog remains the primary metadata, governance, and authorization
  authority.
- Amazon S3 and managed Apache Iceberg remain the required system of record.
- Databricks on AWS remains the data engineering and analytics platform.
- No AWS Glue database exists in the approved AWS account and Region.
- No Doris, OpenSearch retrieval, ingestion framework, controlled tool
  service, LangGraph/agent, Goal 5+, real Green SM data, or Green SM business
  logic was introduced.
- No accepted ADR was modified.

## Authenticated targets

| Property | Observed value | Result |
| --- | --- | --- |
| Databricks CLI | `v1.11.0` | PASS |
| Configured development profile | `ask-david-development` | PASS |
| Authentication type | OAuth U2M (`databricks-cli`) with token material held by the operating-system keyring; no token was requested or printed | PASS |
| Account-level OAuth profile | Not configured during Phase 4-0 | UNVERIFIED; required only if the approved design uses account-level identity APIs |
| Workspace host | `https://dbc-7f3363e3-d129.cloud.databricks.com` | PASS |
| Workspace ID | `7474644358733471` | PASS |
| Databricks account ID | `e7e97bc6-a872-4312-9a43-c0eb305b1b2e` | PASS |
| Authenticated principal | `b***@gmail.com` | PASS |
| Workspace administrator | Direct member of the workspace `admins` group | PASS |
| AWS account | `736956442295` | PASS |
| AWS principal | `arn:aws:iam::736956442295:user/bach_dev_admin_david` | PASS |
| AWS Region | `ap-southeast-1` | PASS |
| Git state before reporting | `main` matched `origin/main`; clean working tree | PASS |

The workspace creation date `2026-06-10` and exact commercial SKU label could
not be retrieved through the available workspace-level read-only APIs. The
required Premium-capable behavior is present: Unity Catalog is attached,
serverless compute is enabled, and a Databricks SQL query completed on the
existing serverless warehouse. The exact SKU label remains UNVERIFIED until an
account-level authoritative response or account-console evidence is available.

## Unity Catalog and regional association

| Property | Observed value | Result |
| --- | --- | --- |
| Current metastore ID | `3a7f7e7a-680b-4bd6-907a-6d5e77b43178` | PASS |
| Global metastore ID | `aws:ap-southeast-1:3a7f7e7a-680b-4bd6-907a-6d5e77b43178` | PASS |
| Metastore cloud | AWS | PASS |
| Metastore Region | `ap-southeast-1` | PASS |
| Workspace assignment | Workspace `7474644358733471` is assigned to that exact metastore | PASS |
| SQL confirmation | `current_metastore()` returned the same global metastore ID | PASS |
| Duplicate-metastore action | None | PASS |

Databricks requires a workspace to use a metastore in its Region. The attached
metastore is scoped to `ap-southeast-1`, matching the approved AWS development
Region. Goal 4 must reuse this assignment and must not create or assign a new
metastore.

The workspace-admin Unity Catalog principal has `CREATE_CATALOG`,
`CREATE_EXTERNAL_LOCATION`, and `CREATE_STORAGE_CREDENTIAL`, among other
workspace-admin metastore privileges. The named OAuth profile is suitable for
planning workspace-level Unity Catalog objects. Any later mutation remains
subject to the explicit Goal 4 plan/apply approval boundaries.

Official references:

- [Create a Unity Catalog metastore](https://docs.databricks.com/aws/en/data-governance/unity-catalog/create-metastore)
- [Unity Catalog setup guide](https://docs.databricks.com/aws/en/data-governance/unity-catalog/setup-uc)

## Existing catalog inventory

The catalog inventory used browse-only and unbound discovery so that catalogs
hidden by current `USE CATALOG` grants were not mistaken for absent objects.

| Catalog | Type | Isolation | Treatment |
| --- | --- | --- | --- |
| `workspace` | Managed | Isolated and read-write bound to workspace `7474644358733471` | Existing; do not modify or reuse |
| `ml` | Managed | Isolated; current principal lacks `USE CATALOG` | Existing; do not modify or reuse |
| `ml_model_store` | Managed | Open | Existing; do not modify or reuse |
| `samples` | System | Open | Existing; do not modify |
| `system` | System | Open | Existing; do not modify |

No `green_sm_*` catalog was visible in the complete browse/unbound inventory.
Repository governance does not yet resolve whether the roadmap names
`green_sm_raw`, `green_sm_curated`, `green_sm_business`, `green_sm_ai`,
`green_sm_platform`, and `green_sm_sandbox` are catalogs or schemas. Phase 4-1
must propose one hierarchy and stop for approval before creating namespaces.

## Existing storage integrations and identities

| Check | Observation | Result |
| --- | --- | --- |
| Project storage credential | None exists | PASS for collision check; creation is required later |
| Existing non-project credential | `databricks-iceberg-staging` uses AWS account `206578774388` | PASS boundary; it must not be reused |
| Databricks-managed credential | System-owned default credential exists | PASS boundary; it must not back Goal 4 system-of-record catalogs |
| Project external location | None exists | PASS for collision check; creation is required later |
| Existing external locations | Only the Databricks-managed default location was listed | PASS |
| Project service principal | None found | PASS for collision check; design is required later |
| Project group | None found | PASS for collision check; design is required later |
| Workspace binding precedent | Existing `workspace` catalog is isolated and bound read-write only to the current workspace | PASS |

The staging credential and its S3 location belong to another AWS account and
are outside Goal 4. They must not be imported, modified, or used by this
project.

## Existing Serverless SQL warehouse

| Property | Observed value | Result |
| --- | --- | --- |
| Name | `Serverless Starter Warehouse` | PASS |
| ID | `757e0335c6efb51e` | PASS |
| Type | `PRO` | PASS |
| Serverless | Enabled | PASS |
| Photon | Enabled | PASS |
| Size | Small | PASS |
| Maximum clusters | 1 | PASS |
| Auto-stop | 10 minutes | PASS |
| Permission | Current principal has `CAN_MANAGE` through `admins` | PASS |
| DBSQL version | `2026.20` from `current_version().dbsql_version` | PASS |
| SQL execution | Both read-only statements completed successfully | PASS |

The warehouse was initially stopped. The read-only SQL capability checks
auto-started it. No explicit start or stop API was called; its existing
10-minute auto-stop remained the cost control. A later read-only warehouse
inspection confirmed `STOPPED`, zero clusters, zero active sessions, and no
manual stop operation. Goal 4 must reuse this warehouse and must not create a
classic cluster or another SQL warehouse merely to validate managed Iceberg.

## Managed Apache Iceberg capability

Current official Databricks documentation states that:

- Unity Catalog-managed Iceberg tables can be created using Databricks SQL;
- the workspace must have Unity Catalog and serverless compute enabled;
- serverless compute maintains managed Iceberg metadata;
- managed Iceberg creation requires predictive optimization; the current
  metastore/catalog responses report predictive optimization enabled or
  inherited as enabled;
- `USING ICEBERG` must be explicit because the default managed table format is
  Delta Lake.

This workspace has Unity Catalog, serverless compute, a working serverless SQL
warehouse, and DBSQL `2026.20`. The supported SQL path is therefore PASS at the
capability level. No table was created during preflight, so actual managed
Iceberg create/write/update/snapshot behavior remains UNVERIFIED until the
separately approved connected execution phase.

Official references:

- [What is Apache Iceberg in Databricks?](https://docs.databricks.com/aws/en/iceberg/)
- [Unity Catalog managed tables for Delta Lake and Apache Iceberg](https://docs.databricks.com/aws/en/tables/managed)
- [`current_version` function](https://docs.databricks.com/aws/en/sql/language-manual/functions/current_version)

## Goal 3 AWS storage discovery

Terraform `1.10.5` read the existing remote state without running init, plan,
apply, or destroy. The verified roots expose or contain:

- State bucket: `ask-david-tfstate-736956442295-ap-southeast-1`
- State KMS key ARN:
  `arn:aws:kms:ap-southeast-1:736956442295:key/a89c9900-a328-4fcd-898f-ce7923e20de7`
- Development VPC: `vpc-007ba758b98a9ab9e`
- Storage KMS key ARN:
  `arn:aws:kms:ap-southeast-1:736956442295:key/a480662f-1d15-48b4-badd-c698c74eeb18`
- Raw bucket: `ask-david-dev-736956442295-ap-southeast-1-raw`
- Curated bucket: `ask-david-dev-736956442295-ap-southeast-1-curated`
- Business bucket: `ask-david-dev-736956442295-ap-southeast-1-business`
- Documents bucket: `ask-david-dev-736956442295-ap-southeast-1-documents`
- Artifacts bucket: `ask-david-dev-736956442295-ap-southeast-1-artifacts`
- Audit bucket: `ask-david-dev-736956442295-ap-southeast-1-audit`
- Logs bucket: `ask-david-dev-736956442295-ap-southeast-1-logs`

Read-only AWS inspection confirmed the Raw, Curated, and Business buckets use
the same enabled customer-managed KMS key in `ap-southeast-1`. Goal 3 evidence
already verifies versioning, TLS-only policies, ownership enforcement, and
public-access blocking.

The current Goal 3 root outputs do not export the storage bucket map or storage
KMS ARN. Phase 4-1 must design a declarative remote-state/output contract rather
than hard-code those values in Goal 4 source.

No Unity Catalog IAM role, storage credential, or external location currently
connects serverless compute to these Goal 3 buckets. The bucket naming,
ownership, Region, and KMS configuration are compatible with the documented
Databricks S3 integration requirements, but actual serverless access to the
Goal 3 managed-storage prefixes is UNVERIFIED until the Terraform-managed IAM
role, storage credential, external locations, KMS permissions, and catalog
managed locations exist and are validated. Security must not be weakened to
close this gap.

Official references:

- [Connect to an AWS S3 external location](https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-storage/s3/)
- [Create a storage credential and external location for S3](https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-storage/s3/s3-external-location-manual)
- [Managed versus external assets in Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/managed-versus-external)

## PASS / FAIL / UNVERIFIED summary

| Prerequisite | Result | Evidence or blocker |
| --- | --- | --- |
| Databricks CLI installed | PASS | `v1.11.0` |
| Named development OAuth profile | PASS | `ask-david-development` uses OAuth U2M and resolves to the approved workspace and administrator principal |
| Account-level OAuth and account-admin privilege | UNVERIFIED | Workspace OAuth does not prove access to account-level identity APIs |
| Approved workspace reachable | PASS | Authenticated workspace APIs and SQL succeeded |
| Workspace ID and administrator status | PASS | Assignment API and SCIM group membership |
| Exact workspace creation date | UNVERIFIED | Not exposed by available workspace-level API |
| Premium-capable functionality | PASS | Unity Catalog and serverless DBSQL are operational |
| Exact commercial SKU label | UNVERIFIED | Requires authoritative account-level evidence |
| Workspace/Region compatibility | PASS | Attached AWS metastore is scoped to `ap-southeast-1` |
| Existing metastore verified | PASS | API and `current_metastore()` agree |
| Existing metastore reused | PASS so far | No metastore mutation occurred |
| Expected existing catalogs | PASS | All five found with browse/unbound discovery |
| Existing catalogs unchanged | PASS | Read-only discovery only |
| Existing serverless warehouse | PASS | Small, serverless, DBSQL `2026.20`, auto-stop 10 |
| Managed Iceberg SQL capability | PASS | Current workspace capabilities match official requirements |
| Actual managed Iceberg operations | UNVERIFIED | No mutation is allowed in Phase 4-0 |
| Goal 3 S3/KMS prerequisites | PASS | Remote-state and read-only AWS inspection |
| Serverless access to Goal 3 storage | UNVERIFIED | Project IAM credential/location do not exist yet |
| Project identities and grants | UNVERIFIED | No project service principal or group exists yet |
| No AWS Glue competing catalog | PASS | Glue database inventory returned an empty list |
| Repository clean before report | PASS | `main` matched `origin/main` |
| Goal 5+ boundary | PASS | No implementation introduced |

## Stopping condition

Phase 4-0 is complete. The named OAuth U2M profile
`ask-david-development` was validated against the approved workspace,
workspace ID, Databricks account ID, and administrator principal. The legacy
PAT-backed `DEFAULT` profile is not required for Goal 4 automation and must not
be selected by the repository-managed configuration.

The exact commercial SKU label and workspace creation date remain UNVERIFIED
because the current OAuth principal did not expose an authoritative account
workspace response. This is not a capability blocker: Unity Catalog,
serverless compute, and DBSQL `2026.20` are directly operational. Actual
managed-Iceberg mutations and serverless access to the Goal 3 S3 prefixes are
correctly deferred to separately approved later phases.

Phase 4-1 may require an additional named account-level OAuth profile for
account groups, service principals, workspace assignments, or service
principal roles. That profile and account-admin privilege must be verified
before any connected identity plan; they were not assumed from workspace-admin
membership.

The next checkpoint is Phase 4-1 design. It must resolve the `green_sm_*`
catalog-versus-schema hierarchy and stop for review before any connected or
persistent mutation.
