# Goal 5 connected synthetic verification

Date: 2026-08-13
Scope: connected synthetic execution evidence and subsequent read-only
Databricks/AWS verification. This report does not replace the required final
Terraform no-drift evidence or the final acceptance report.

## Successful three-path workflow

The separately approved one-time run `172279846311777` of job
`382877731318442` completed `SUCCESS` on existing Serverless SQL Warehouse
`757e0335c6efb51e`. All six tasks succeeded, including all three ingestion
paths, output assertions, and idempotency assertions. Full task/run evidence
is recorded in
`GOAL-05-NUMERIC-ASSERTION-WORKFLOW-SUCCESS-2026-08-13.md`.

The successful read-only output assertions prove:

- structured Raw has three valid rows; one invalid row is quarantined as
  `INVALID_TYPE`; Curated is deduplicated to two event IDs; and Business
  aggregates reconcile to Curated;
- the approved Markdown document has governed metadata, accepted validation,
  and the approved S3 source URI;
- CDC Raw retains four unique events with duplicate occurrence count two;
  current state has the `entity-001` UPDATE value 120 and `entity-002` DELETE
  tombstone; and CDC validation status is recorded;
- auditable ingestion runs and passing quality results exist for all three
  patterns.

The successful read-only idempotency assertions prove that re-execution of the
same CSV/document version/CDC batch retained unique trusted-data keys, applied
CDC events at most once, and created at least six auditable source-pattern
runs. No generalized replay/backfill facility was created.

## Source-object and storage evidence

Read-only AWS `head-object` checks in approved account `736956442295`, region
`ap-southeast-1`, confirmed all approved synthetic inputs still exist and use
the existing storage KMS key with `aws:kms` encryption:

| Input | Bucket/prefix | Bytes | Content type |
| --- | --- | ---: | --- |
| Structured CSV | raw `/unity-catalog/development/goal5/structured/synthetic_events.csv` | 262 | `text/csv` |
| Markdown document | documents `/unity-catalog/development/goal5/documents/neutral_technical_guide.md` | 240 | `text/markdown` |
| CDC JSONL | raw `/unity-catalog/development/goal5/cdc/synthetic_changes.jsonl` | 852 | `application/x-ndjson` |

The source objects, source locations, workspace bindings, workflow-principal
`READ FILES` grants, and prefix-scoped IAM read policy were previously
inspected and recorded in
`GOAL-05-SOURCE-ACCESS-REMEDIATION-2026-08-13.md`. No direct user/S3 bypass,
source write/delete grant, static credential, or KMS-policy expansion was
introduced.

## Authoritative table format evidence

The Databricks Tables API was queried read-only for all nine Goal 5
source-of-truth tables. The fail-closed
`scripts/verify_goal5_table_inventory.py` accepted the sanitized API inventory.
Every table is:

- `table_type = MANAGED`;
- `data_source_format = DELTA`;
- `delta.enableIcebergCompatV2 = true`;
- `delta.universalFormat.enabledFormats = iceberg`; and
- backed by an approved S3 `_iceberg/metadata` path.

Each is therefore classified as `DELTA_UNIFORM_ICEBERG`, not native Iceberg.
The exact required disclosure is: **Unity Catalog managed Delta with UniForm
Iceberg interoperability.** No plain Delta-only or unmanaged Goal 5 table was
observed.

## Foundation and cost controls

- The workspace remains attached to metastore
  `3a7f7e7a-680b-4bd6-907a-6d5e77b43178` in workspace `7474644358733471`.
- Bundle remote summary shows the existing five Goal 4 jobs and the one Goal 5
  job; no duplicate Goal 5 job was created.
- All six existing Goal 4 project tables were read-only inspected as managed
  Delta UniForm with Iceberg compatibility, so Goal 4 remains healthy.
- Cluster inventory is empty. The only compute used is the existing Small/PRO
  Serverless warehouse. It was observed RUNNING after the approved workflow,
  with zero active sessions and 10-minute auto-stop; no persistent cluster or
  warehouse was created.

## Safe failures and scope controls

The passed 124-test offline suite covers invalid contracts, invalid CSV
schema/scalars, quarantine behavior, unsupported document content, invalid CDC
events, duplicate/out-of-order CDC behavior, quality failures, and fail-closed
table-format validation. Goal 5 static validation rejects Doris, OpenSearch,
LangGraph, Supervisor, or specialized-agent scope in its configuration.
Only neutral `synthetic_technical` fixtures are present; no real Green SM data
or business logic was introduced.

## Remaining finalization boundary

Goal 5 source/access resources are Terraform-managed. The final outstanding
connected evidence is one separately approved saved development Terraform plan
using the transient input `goal_5_source_objects_enabled=true`. That input is
required because the default false value would otherwise propose deletion of
the intentionally retained source fixtures. Expected final result is zero
non-no-op actions; any create/update/replace/destroy stops for review. The
saved plan must be reviewed before final status can be claimed.
