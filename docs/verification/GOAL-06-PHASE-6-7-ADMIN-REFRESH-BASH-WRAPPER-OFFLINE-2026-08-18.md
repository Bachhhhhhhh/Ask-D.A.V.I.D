# Goal 6 Phase 6-7 admin-refresh Bash wrapper — offline preparation

Date: `2026-08-18`

Status: `OFFLINE VALIDATED — TASK NOT RUN`

## Purpose

The FE/BE listener and BE storage-capacity checkpoint is PASS. Phase 6-7 must
resume with exactly one revision-8 admin-refresh task to validate Unity Catalog
Iceberg REST interoperability and populate the initial rebuildable Doris
serving copy. The existing repository launch wrapper is PowerShell, but `pwsh`
is unavailable on the current Linux host. Reconstructing its AWS commands
manually would weaken the reviewed execution contract.

This change adds a Bash implementation of the same guarded one-task workflow.
It does not change the task definition, image, Doris SQL, AWS infrastructure,
Databricks resources, Unity Catalog permissions, source data, or network.

## Read-only preflight

| Check | Result |
| --- | --- |
| AWS account | PASS — `736956442295` |
| AWS region | PASS — `ap-southeast-1` |
| Admin task definition | PASS — `ask-david-development-doris-admin-refresh:8`, ACTIVE |
| Image | PASS — digest `sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad` |
| Runtime | PASS — private Fargate `awsvpc`, CPU `512`, memory `1024` |
| FE/BE | PASS — `10.42.64.238` / `10.42.71.97` |
| Workspace origin | PASS — `https://dbc-7f3363e3-d129.cloud.databricks.com` |
| Running admin tasks | PASS — none |
| Databricks CLI/profile | PASS — CLI `1.11.0`, development profile authenticated |
| Unity Catalog metastore | PASS — `3a7f7e7a-680b-4bd6-907a-6d5e77b43178`, AWS `ap-southeast-1`, external access enabled |
| Development catalog | PASS — `ask_david_development`, isolated, Terraform-managed |
| Dedicated Doris external-read principal | PASS — active application `c63e5acc-4d00-4107-9ba3-4705c7f95fbc`, workspace service-principal object `76225913692184` |
| Catalog grant | PASS — `USE_CATALOG` only for the Doris principal |
| Business-schema grants | PASS — `USE_SCHEMA`, `EXTERNAL_USE_SCHEMA` only for the Doris principal |
| Allowlisted source-table grant | PASS — `SELECT` only for the Doris principal |
| Source write/create/admin privilege | PASS — none present in the inspected catalog/schema/table assignments |
| Source table classification | PASS — managed `DELTA_UNIFORM_ICEBERG`; Tables API reports `data_source_format=DELTA` plus `delta.universalFormat.enabledFormats=iceberg` |
| Iceberg metadata location | PASS — approved Business S3 managed-storage path under `_iceberg/metadata` |
| Live Doris interoperability | UNVERIFIED — requires the separately approved connected admin task |

No secret value was requested or printed. Read-only task-definition inspection
showed only Secrets Manager ARN references for the expected admin, query, and
Databricks OAuth containers.

The Tables API currently reports two analyzed synthetic rows and the expected
neutral columns (`metric_date`, `category`, `event_count`, `metric_total`, and
provenance fields). This statistic is discovery evidence, not a substitute for
the required connected Doris query or authoritative-result comparison. The
source is not claimed as native Iceberg: its live classification is managed
Delta UniForm with an enabled Iceberg-compatible representation.

## Bash wrapper contract

`infrastructure/scripts/run-goal6-admin-refresh.sh`:

- requires an explicit `--confirm-goal6-admin-refresh` switch;
- verifies account, region, active task family/revision, digest-pinned image,
  Fargate/`awsvpc`, CPU/memory, task role, execution role, null task-level
  entrypoint, and fixed `/app/doris-admin-refresh` command;
- verifies exact FE, BE, and Databricks workspace-origin environment values;
- verifies the complete expected environment-name and secret-reference-name
  sets, regional/account ARN prefixes, and CloudWatch log configuration;
- launches exactly one task in exactly two approved private application
  subnets with only the admin SG and `assignPublicIp=DISABLED`;
- supplies no ECS command override;
- requires a private task attachment, exit code zero, exactly one task log
  stream, and the sanitized admin-refresh completed marker;
- emits only sanitized task/ENI/log metadata;
- performs no retry and does not call Terraform, Databricks CLI, S3 APIs, or
  Secrets Manager value retrieval.

The immutable task image's existing runner may create its temporary Doris
Unity Catalog Iceberg REST catalog, read the single allowlisted governed
source, populate only internal rebuildable Doris objects, and drop the
temporary catalog. It must not write Unity Catalog/S3 or the source table.

## Offline validation

| Command/check | Result |
| --- | --- |
| `bash -n infrastructure/scripts/run-goal6-admin-refresh.sh` | PASS |
| `python3 scripts/validate_goal6.py` | PASS |
| Focused Goal 6 plus Goal 5 regression suite with coverage addopts disabled | PASS — 27 tests |
| `git diff --check` | PASS |

The focused pytest run emitted two non-failing warnings because the existing
`.pytest_cache` directory is not writable. No test failed.

## Reviewed hashes

- Bash wrapper:
  `95f58b26c2210a0cd116cf3f145ba0e2e6ea0d90a0f8327a6bc6c2e87a2cc542`
- Existing PowerShell wrapper:
  `b239a3eaae5b52e8977ca5ac9590b14d71525a387f839ab358782bc5ed0bed8f`
- Immutable image runner source:
  `ac32c927e5b78c12bcb57984b9a59aa96165907907707100d66c1cb993d57d79`
- Goal 6 static validator:
  `3ba84cd1b29010fa34f0028c1e784d39161262901248cca808cbf5921710bc48`
- Focused regression source:
  `43d963e3be55714e16f3470b9cfddb5d74fc993491549270e5d7749b8f6b5da9`

## Approval boundary

No ECS task, Terraform operation, AWS mutation, Databricks mutation, Unity
Catalog operation, Doris SQL, ECR operation, or bundle operation occurred.

The next step requires separate approval to launch exactly one private
revision-8 admin-refresh task using the reviewed Bash wrapper. A task failure
must stop without retry; only a separately approved, non-secret error
inspection may follow.
