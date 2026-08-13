# Goal 5 source-access remediation

Date: 2026-08-13  
Scope: offline analysis and declarative remediation after the first approved
synthetic-ingestion run. No Terraform apply, AWS mutation, Databricks
mutation, bundle operation, SQL run, or job retry occurred in this checkpoint.
The separately approved connected-plan checkpoint was run only after the
offline remediation. Its apply was approved, but it stopped after the AWS
policy update when Databricks rejected both external-location creates; no
workflow, bundle, SQL, or retry followed.

## Observed failure evidence

The approved one-time run of job `382877731318442` was accepted as run
`1025066514456351` on existing Serverless Small warehouse
`757e0335c6efb51e`.

| Task | Result | Evidence |
| --- | --- | --- |
| `create_goal5_tables` | `SUCCESS` | The idempotent DDL completed. It may have created the nine empty Goal 5 managed tables; no ingestion result is inferred from DDL success. |
| `ingest_structured_csv` | `FAILED` | `INSUFFICIENT_PERMISSIONS`: User does not have permission SELECT on any file. |
| `ingest_document` | `FAILED` | Same `INSUFFICIENT_PERMISSIONS` result. |
| `ingest_cdc` | `FAILED` | Same `INSUFFICIENT_PERMISSIONS` result. |
| `verify_goal5_outputs` | `UPSTREAM_FAILED` | Not executed. |
| `verify_goal5_idempotency` | `UPSTREAM_FAILED` | Not executed. |

No retry occurred. The source-ingestion SQL did not reach a governed table
write, so structured/document/CDC data, quality results, provenance, and
ingestion-run success evidence remain unverified.

## Root cause

The three Terraform-managed fixture objects exist below these approved paths:

- raw bucket: `unity-catalog/development/goal5/structured/` and
  `unity-catalog/development/goal5/cdc/`;
- documents bucket: `unity-catalog/development/goal5/documents/`.

The seven existing Goal 4 external locations cover only managed-table roots
such as `green_sm_raw` and `green_sm_ai`; they do not cover the Goal 5 source
prefixes. The existing Unity Catalog storage role likewise limits S3 list and
object actions to the managed-table roots. `read_files(...)` therefore reaches
Unity Catalog's file authorization boundary before source rows can be read.

Databricks documentation requires `READ FILES` on the external location for
`read_files(...)`; the remediation retains that UC control instead of granting
direct S3 access. See [read_files table-valued function](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files)
and [Unity Catalog privileges](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/privileges-reference).

## Declarative remediation

The repository now defines exactly two additional development-only locations:

| Location | URL scope | Access model |
| --- | --- | --- |
| `ask-david-development-goal5-raw-sources` | raw bucket `unity-catalog/development/goal5` | read-only; workflow SP has only `READ FILES` |
| `ask-david-development-goal5-document-sources` | documents bucket `unity-catalog/development/goal5/documents` | read-only; workflow SP has only `READ FILES` |

The workflow principal is referenced by the Terraform-created service
principal application ID, not a hard-coded ID or display name. No grant is
given to the denied test principal or the data-engineer group. Existing seven
managed locations retain their prior `CREATE MANAGED STORAGE` grant model and
do not receive `READ FILES`.

The existing storage-role inline policy gains only:

- prefix-scoped `s3:ListBucket` for the two source paths;
- `s3:GetObject` and `s3:GetObjectVersion` for the corresponding object ARNs.

It gains no source `PutObject`, `DeleteObject`, wildcard path, direct user
identity, KMS policy change, or storage-credential change.

## Offline validation

| Check | Result |
| --- | --- |
| Goal 4 static validator | PASS |
| Goal 5 static validator | PASS |
| Focused static regression tests | PASS — 39 tests |
| Ruff lint | PASS |
| Ruff format check | PASS |
| Mypy | PASS — 7 source files |
| `git diff --check` | PASS |
| Terraform fmt/validate/test, TFLint, Trivy | UNVERIFIED — the local tool binaries are unavailable in this session; no substitute parser or connected command was used. |

The first test invocation executed all 39 tests but pytest-cov could not write
the pre-existing workspace `coverage.xml`; the focused rerun disabled coverage
artifact generation and passed all 39 tests. This does not substitute for the
repository-wide coverage gate.

## Saved connected-plan evidence

The first plan attempt was rejected before approval because the documented
transient `goal_5_source_objects_enabled = true` input was omitted. That
stale-input artifact (`f316bf24782c11f00bee8e3bbf409702ebafe3e6db5a977774a15765825d330a`)
would have destroyed the three Terraform-managed fixture objects, so it was
not used.

The corrected saved plan was generated with that transient input and has
SHA-256:

`41536708b1a67a37cbc87e9e1c6e046cefc858547cea3925c49e489c38fb09e6`

Its reviewed action set is exactly `6 to add, 1 to change, 0 to destroy`:

- AWS: one in-place `aws_iam_role_policy` update adding only scoped source
  list/read permissions;
- Databricks: two read-only source external locations, two development
  workspace bindings, and two workflow-principal `READ FILES` grants;
- no source-object action, KMS change, storage-credential change, metastore,
  catalog/schema, warehouse/compute, replacement, or destroy.

The plan is saved outside the repository at
`/tmp/goal5-source-access-remediation-20260813.tfplan`; its JSON inspection
reported 191 no-op resources and no unreviewed action.

## Fresh-plan apply evidence

After identity and plan-hash revalidation, the fresh plan was applied once.
The apply log is outside the repository at
`/tmp/goal5-source-access-remediation-r2-20260813-apply.log` (SHA-256
`98025bd2f096b15bc7fb1bbfc9c018f17a82568aab55277eeca14e8f8b228988`); it ended with
`Apply complete! Resources: 6 added, 0 changed, 0 destroyed.`

Immediate read-only inspection then confirmed:

- both source external locations exist, use the existing storage credential,
  are read-only and isolated, and point only to the approved Goal 5 prefixes;
- each location has exactly the workflow service principal
  `b2bdec62-62db-432d-bc6f-1f92b78053b0` with `READ_FILES`;
- each location is bound read/write to workspace `7474644358733471`;
- the IAM source-read statements remain prefix/object scoped, with no source
  write/delete, wildcard bucket access, KMS, credential, or other resource
  change;
- no bundle, job, SQL, table, or compute operation was run in this
  checkpoint.

This proves the source-access remediation itself, not successful ingestion.

## Required next approval

The failed saved plan above was not reused. The fresh saved connected
development plan that was applied has SHA-256

`2d6f0c09217e9edecda9878e2be5d496263a3c2c91d67ed17bcccb13a0772dc4`

The fresh plan is saved outside the repository at
`/tmp/goal5-source-access-remediation-r2-20260813.tfplan`; its JSON
inspection reported 192 no-op resources and no unreviewed action.

No further Terraform mutation is authorized by this report. After a separate
explicit approval, run the deployed Goal 5 workflow exactly once on the
existing Serverless SQL Warehouse. Expected next actions are:

- one workflow run using the already deployed source set;
- no Terraform, bundle, AWS control-plane, compute-creation, or ad-hoc SQL
  operation;
- stop immediately on any task failure, with no implicit retry.

The run requires a separate approval and must be followed by immediate
read-only task inspection.

## Apply attempt evidence and current blocker

The corrected plan above was applied once after identity and hash
revalidation. The apply log is outside the repository at
`/tmp/goal5-source-access-remediation-20260813-apply.log` (SHA-256
`a3425163f9496b40743f5a9be3ee852fc741f538c49d2f50953a7901da6d47e6`). The
`aws_iam_role_policy` update completed successfully. Both external-location
creates then failed with Databricks `PERMISSION_DENIED` stating that the AWS
IAM role had no READ permission on the approved raw and documents URLs.

This is a failed partial apply, not Goal 5 verification. No successful
external-location, grant, or workspace-binding completion is inferred from
the failed log. The old saved plan must not be reused; the fresh remaining-
actions plan documented above requires a separate approval before any further
mutation.

## Post-failure read-only revalidation

The approved development identity was rechecked as AWS account
`736956442295`, region `ap-southeast-1`, with the existing Databricks
development profile and storage credential. The role's live inline policy now
contains the intended `ListApprovedIngestionSourcePrefixes` and
`ReadApprovedIngestionSourceObjects` statements. AWS IAM policy simulation
returned `allowed` for the source `ListBucket`, `GetObject`,
`GetObjectVersion`, and storage-KMS decrypt/describe checks. Both fixture
objects are SSE-KMS encrypted with the approved storage key, and the live KMS
policy names the storage role as an allowed principal.

The Databricks external-location inventory still contains only the eight
pre-existing locations; neither Goal 5 source location exists, so no source
grant or workspace binding can have completed. This evidence confirms that
the failed plan's IAM update is present and that the remaining plan should
contain only the six Databricks creates. It does not prove that Databricks
has completed the external-location validation, and it does not authorize a
retry.

The fresh plan contained exactly 6 creates and 192 no-op resources, with zero
updates, replacements, and destroys. The six creates were the two source
external locations, two development workspace bindings, and two scoped
workflow-principal `READ FILES` grants. The storage IAM policy, all three
source objects, KMS, storage credential, metastore, catalogs, schemas,
warehouse, and compute were all no-op.

## Goal 5 workflow attempt and blocker

After the source-access apply, the separately approved one-time workflow run
was triggered as job `382877731318442`, run `616649104578361`, on existing
Small Serverless SQL Warehouse `757e0335c6efb51e`. The terminal parent state was
`FAILED` / `INTERNAL_ERROR` with this task result:

| Task | Result |
| --- | --- |
| `create_goal5_tables` | `SUCCESS` |
| `ingest_structured_csv` | `SUCCESS` |
| `ingest_document` | `SUCCESS` |
| `ingest_cdc` | `FAILED` |
| `verify_goal5_outputs` | `UPSTREAM_FAILED` / skipped |
| `verify_goal5_idempotency` | `UPSTREAM_FAILED` / skipped |

The failed CDC task run was `590606768066484`. Its read-only run output was:
`[TABLE_OR_VIEW_NOT_FOUND] The table or view unique_events cannot be found`.
The cause is SQL scope: `unique_events` is a CTE defined for the first
`MERGE` only, then referenced by later independent `MERGE` statements in
`04_ingest_cdc.sql`. It is not a source-access or IAM failure.

No retry, cancellation, redeploy, ad-hoc SQL, or second workflow run occurred.
Goal 5 ingestion remains unverified. The next approval boundary is an offline
CDC SQL remediation (materialize or repeat the deterministic CTE for each
statement), static/regression validation, and a fresh strict bundle validation
before any retry is considered.
