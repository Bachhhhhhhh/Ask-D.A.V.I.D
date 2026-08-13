# Goal 5 MVP — Minimal ingestion and transformation implementation plan

## 1. Status and stopping boundary

This is the Phase 5-1 design and implementation contract for the reduced,
synthetic-only Goal 5 MVP. The design was reviewed offline before the current
Phase 5-2 source work. It does not authorize a Terraform plan/apply,
bundle validation/deployment, SQL/job execution, S3 mutation, or Databricks
mutation.

The fixed development target is AWS account `736956442295`, Region
`ap-southeast-1`, Databricks workspace `7474644358733471`, existing Unity
Catalog metastore `3a7f7e7a-680b-4bd6-907a-6d5e77b43178`, and existing Small
Serverless SQL Warehouse `757e0335c6efb51e`.

The source-access remediation has been applied and read-only inspected. The
first post-remediation workflow run failed in the CDC task because its
`unique_events` CTE was referenced outside the statement that defined it.
The offline correction and its stopping boundary are recorded in
`docs/verification/GOAL-05-CDC-SQL-REMEDIATION-2026-08-13.md`; no retry is
authorized until that correction passes offline and strict connected bundle
validation.

## 2. Objective and non-goals

The MVP proves three reusable patterns with neutral technical fixtures:

1. structured CSV file ingestion into Raw, Curated, and Business;
2. TXT/Markdown document preservation and governed metadata;
3. deterministic CDC batch history and current-state interpretation.

It does not add relational database connectivity, Debezium, Kafka, MSK,
Kinesis, streaming infrastructure, REST extraction, generalized replay or
backfill, advanced schema evolution or watermarks, PDF/OCR/chunking,
embeddings, OpenSearch, Doris, LangGraph, agents, or real Green SM
data. These are explicitly deferred by the Goal 5 objective and roadmap.

## 3. Reuse and architecture contract

The implementation reuses the existing project catalog, six project schemas,
IAM-based storage credential, seven external locations, managed-storage
prefixes, and Serverless SQL warehouse. It creates no metastore, catalog,
schema, storage credential, external location, warehouse, persistent cluster,
Doris, OpenSearch collection, or AWS Glue catalog.

Unity Catalog remains the sole governance and authorization authority. S3 is
the durable storage layer. All governed Goal 5 tables are managed tables with
no explicit `LOCATION` clause.

The existing Goal 4 bundle root remains the repository's Databricks bundle
root. Goal 5 resources are additive and are isolated by `goal-05` names,
properties, paths, and job identities; no Goal 4 job or table identity is
changed. Because the bundle root is shared, its full source set and Goal 4
strict validation must be rerun after implementation before any deployment.

## 4. Table-format policy

Every new governed source-of-truth table is created with `USING ICEBERG` and
without `LOCATION`. After connected execution, the authoritative Tables API
classifies each table as one of:

- native `ICEBERG` — PASS;
- managed `DELTA` with explicit UniForm/Iceberg compatibility properties and
  Iceberg metadata — `DELTA_UNIFORM_ICEBERG`, PASS WITH DISCLOSURE;
- plain `DELTA` without interoperability — FAIL;
- any other format — UNVERIFIED and stop.

The implementation never labels `DELTA_UNIFORM_ICEBERG` as native Iceberg. It
does not drop or recreate the seven existing Goal 4 tables. The exact live
format and relevant Tables API properties are recorded in the final report.
The accepted Goal 4 compatibility profile is carried forward; ADRs remain
unchanged. If a requirement cannot be satisfied by either accepted format,
stop for a separate architecture decision instead of changing an ADR here.

## 5. Repository layout

The implementation will use these existing project areas:

```text
packages/ingestion-framework/
  pyproject.toml
  src/ask_david_ingestion/
    __init__.py
    contracts.py
    models.py
    adapters.py
    quality.py

synthetic_data/goal_05/
  contracts/structured.json
  contracts/document.json
  contracts/cdc.json
  structured/synthetic_events.csv
  documents/neutral_technical_guide.md
  cdc/synthetic_changes.jsonl

databricks/sql/goal_05/
  01_create_goal5_tables.sql
  02_ingest_structured_csv.sql
  03_ingest_document.sql
  04_ingest_cdc.sql
  05_verify_goal5_outputs.sql
  06_verify_goal5_idempotency.sql

databricks/bundles/goal_05_ingestion/resources.yml

scripts/validate_goal5.py
tests/unit/test_goal5_contracts.py
tests/unit/test_goal5_adapters.py
tests/unit/test_goal5_static.py
docs/runbooks/GOAL-05-INGESTION.md
```

The existing `packages/platform-foundation` package remains responsible for
environment configuration. The new package is a small typed domain library,
not a second platform hierarchy and not an agent runtime.

## 6. Machine-readable contracts

Contracts are JSON so parsing uses the Python standard library and does not
introduce a runtime dependency solely for configuration. Each contract has a
version and a common block:

```json
{
  "contract_version": "1.0",
  "dataset_id": "goal5.synthetic.events",
  "source_type": "structured_file",
  "source": "goal5/structured/synthetic_events.csv",
  "target_catalog": "ask_david_development",
  "target_schema": "green_sm_raw",
  "target_table": "goal5_structured_raw_events",
  "sensitivity_classification": "synthetic_technical",
  "quality_rules": [
    {"name": "required_fields", "columns": ["event_id", "entity_id"]},
    {"name": "unique_primary_key", "columns": ["event_id"]}
  ]
}
```

Contract-specific requirements are:

- structured: `schema` with typed columns and `primary_key`;
- document: `allowed_content_types`, `document_id_strategy`, and required
  metadata fields;
- CDC: `primary_key`, `operation_field`, `event_id_field`,
  `event_time_field`, and `sequence_field`.

The validator rejects missing or blank fields, unsupported source types,
unknown contract fields, duplicate schema columns, invalid quality-rule names,
an undeclared Iceberg-interoperability policy, and source/target keys outside
the approved development contract. The runtime resolves logical source keys
from Terraform-derived task parameters; bucket names are not hard-coded in
tracked contracts. Errors are typed and include a stable code and field path.
No credentials or tokens are valid contract fields.

## 7. Common run and provenance model

`IngestionRun` is an immutable typed record with:

- `run_id`, `dataset_id`, `source_type`, `source`, and `source_version`;
- `started_at`, `completed_at`, and status (`RUNNING`, `SUCCEEDED`,
  `FAILED`, or `PARTIAL`);
- input, accepted, and rejected counts;
- validation error summary without secrets.

`Provenance` attaches dataset identity, source URI/file, source record or
document identity, and ingestion run ID to every accepted, quarantined, and
derived record. Run IDs are unique per execution. Idempotency keys are
separate from run IDs so a retry is auditable without duplicating trusted
data.

## 8. SourceAdapter abstraction

The package defines a typed `SourceAdapter` protocol with explicit contract
validation and ingestion methods. It returns an `AdapterResult` containing
accepted records, quarantined records, deterministic statistics, and
provenance; it does not connect to cloud services or hold credentials.

### FileSourceAdapter

- Supports CSV only for this MVP.
- Reads a deterministic local fixture through `csv.DictReader`.
- Validates exact headers and declared scalar types.
- Captures invalid rows with stable reason codes such as
  `SCHEMA_MISMATCH`, `MISSING_REQUIRED_FIELD`, or `INVALID_TYPE`.
- Preserves valid source rows for Raw and applies deterministic primary-key
  selection for Curated: highest source row number wins, with canonical-row
  hash as a stable tie breaker.
- Runs required/not-null and uniqueness quality rules.

### DocumentSourceAdapter

- Supports only `text/plain` and `text/markdown`.
- Derives a stable document ID from dataset/source identity and a version from
  content SHA-256.
- Emits filename, content type, source URI, source system, classification,
  ingestion run ID, and ingestion timestamp.
- Rejects PDF, binary, and unsupported MIME types before execution.
- Preserves the original object; it does not chunk, embed, index, or retrieve
  the document.

### CDCSourceAdapter

- Reads deterministic JSON Lines events.
- Validates `INSERT`, `UPDATE`, and `DELETE`, event ID, entity key,
  event-time, sequence, source, and payload.
- Keeps one raw history record per unique event ID with duplicate occurrence
  count and duplicate provenance, so the complete unique history is retained
  without uncontrolled retry duplication.
- Orders events deterministically by entity, event time, sequence, then event
  ID; duplicate event IDs are applied once.
- Uses a documented tombstone policy: DELETE remains in current state with
  `is_deleted = true`, a null payload, and the deleting event provenance.

## 9. Goal 5 governed tables

All tables are under existing schemas and receive `data_classification =
synthetic-only`, `goal = goal-05`, and `table_format_policy =
iceberg-or-delta-uniform-iceberg` properties.

| Layer/schema | Table | Responsibility |
| --- | --- | --- |
| `green_sm_platform` | `goal5_ingestion_runs` | Auditable run lifecycle and counts |
| `green_sm_platform` | `goal5_quality_results` | Required/not-null, uniqueness, schema, and reconciliation results |
| `green_sm_raw` | `goal5_structured_raw_events` | Source-faithful valid structured rows and provenance |
| `green_sm_raw` | `goal5_structured_quarantine` | Invalid structured rows and explicit reason |
| `green_sm_curated` | `goal5_structured_curated_events` | Deterministically deduplicated and quality-filtered rows |
| `green_sm_business` | `goal5_structured_business_metrics` | Generic category/day aggregates only |
| `green_sm_ai` | `goal5_document_metadata` | Governed document identity, version, metadata, and provenance |
| `green_sm_raw` | `goal5_cdc_history` | Unique CDC history, duplicate counts, and event provenance |
| `green_sm_curated` | `goal5_cdc_current_state` | Latest deterministic state including DELETE tombstones |

No Goal 4 table is altered. The quarantine table is governed Raw-layer data,
not a bypass around Unity Catalog.

## 10. Connected source fixtures and AWS boundary

The structured CSV and Markdown source must exist in the approved S3 prefixes
so the connected workflow proves actual file/document ingestion rather than a
`VALUES`-only simulation. The minimal declarative AWS extension is:

1. one `aws_s3_object` in the existing raw bucket at
   `unity-catalog/development/goal5/structured/synthetic_events.csv`;
2. one `aws_s3_object` in the existing documents bucket at
   `unity-catalog/development/goal5/documents/neutral_technical_guide.md`;
3. one `aws_s3_object` in the existing raw bucket at
   `unity-catalog/development/goal5/cdc/synthetic_changes.jsonl`.

All three objects are SSE-KMS encrypted through the existing bucket/KMS
configuration, tagged synthetic-only/Goal 5, and owned by Terraform from
tracked fixture files. No bucket, IAM, KMS, network, external-location, or
credential change is expected. The connected Terraform plan must show exactly
three object creates (plus any output-only changes), zero replacement, zero
destroy, and zero unrelated resource actions. This is a separate approval
boundary; if a read-only capability check finds another safe supported source
path, these objects must not be created unnecessarily.

## 11. SQL workflow and bundle design

Add one Goal 5 workflow to the existing bundle, using the existing warehouse
and existing workflow service principal. The workflow has these sequential SQL
tasks:

1. create the nine managed tables with `USING ICEBERG`, no `LOCATION`, and
   idempotent `CREATE TABLE IF NOT EXISTS`; immediately run a fail-closed
   pre-write table-property check requiring native Iceberg or explicit UniForm
   interoperability before any source data is written;
2. read the CSV with the Databricks SQL `read_files` table-valued function,
   apply contract/schema checks, merge valid rows to Raw, quarantine invalid
   rows with reasons, deduplicate to Curated, and build generic Business
   aggregates;
3. read the approved Markdown object, merge document metadata by
   `(document_id, document_version)`, and record original-object provenance;
4. read the CDC JSONL batch, merge unique history with duplicate counts, apply
   ordered INSERT/UPDATE/DELETE semantics, and write current-state tombstones;
5. expose read-only output and idempotency assertions; a repeat of the exact
   three source versions is a separate approved workflow execution; and
6. run fail-closed read-only assertions for counts, quarantine reasons,
   provenance, quality results, current CDC state, source-object paths, and
   all three accepted table-format categories. The final authoritative
   classification is still performed with the Tables API; a SQL metadata
   check is only a pre-write safety gate and cannot relabel a table.

SQL task parameters provide catalog name, warehouse ID, source URIs, contract
versions, and deterministic fixture version identifiers. Dynamic paths are
validated against the approved development prefixes before use. No arbitrary
SQL or generated code is accepted from a user or agent.

## 12. Idempotency and failure semantics

Idempotency keys are:

- structured: `(dataset_id, source_uri, source_row_number, record_hash)`;
- document: `(dataset_id, document_id, document_version)`;
- CDC: `(dataset_id, event_id)`.

Every repeat receives a new `run_id` but does not duplicate trusted output.
Structured duplicate primary keys remain visible in Raw and resolve
deterministically in Curated. A document repeat creates an audit run but no
duplicate metadata version. CDC repeats do not reapply events or alter current
state, while duplicate occurrence counts remain auditable.

Offline and connected-safe checks cover invalid contracts, invalid CSV schema,
failed quality rules, unsupported content type, duplicate CDC IDs, and
out-of-order CDC events. Failures are explicit, do not mark a successful run,
do not publish invalid rows to trusted Curated/Business tables, and retain
provenance for quarantined input.

## 13. Security and governance

- Only the existing IAM-backed Unity Catalog storage credential accesses S3.
- The three approved Goal 5 fixtures sit outside the seven Goal 4 managed-table
  roots. They use exactly two Terraform-managed, read-only external locations:
  the raw Goal 5 prefix for CSV/CDC and the document Goal 5 prefix for Markdown.
  The workflow service principal receives `READ FILES` only on those two
  locations, identified by Terraform-derived application ID. It receives no
  `WRITE FILES`, direct IAM identity, or broader data-engineer-group file grant.
- The storage-role inline policy permits only prefix-scoped `ListBucket` and
  `GetObject`/`GetObjectVersion` on those source paths. It does not add source
  write/delete actions or change the existing KMS policy.
- No static AWS or Databricks credential is added to contracts, fixtures,
  SQL, logs, or run metadata.
- The workflow service principal is the only writer for the approved job.
- Unity Catalog governs all tables and metadata; no direct agent or user S3
  bypass is added.
- Original documents remain in the approved S3 document prefix; metadata is
  governed in `green_sm_ai`.
- All fixtures are clearly neutral synthetic technical data.
- No Goal 5 code executes inside an agent runtime; the package is an offline
  ingestion-domain library and Databricks executes only reviewed SQL files.

## 14. Implementation file ownership

Expected source changes after approval:

- new `packages/ingestion-framework` package and its tests;
- new JSON contracts and neutral fixtures under `synthetic_data/goal_05`;
- new Goal 5 SQL and bundle resource definitions;
- additive Goal 5 static validator and developer command wiring;
- three Terraform-managed source-object resources and sanitized outputs if
  needed;
- Goal 5 runbook and verification documentation;
- `docs/PROJECT_STATUS.md` checkpoint updates.

Accepted ADRs, Goal 4 table identities, Goal 4 remediation paths, local
`terraform.tfvars`, `backend.hcl`, state, saved plans, OAuth tokens, and AWS
credentials are never modified or tracked.

## 15. Offline validation plan

After implementation, before any connected action, run:

```bash
make format-check
make lint
make typecheck
make test
make databricks-static
make goal5-static
make security
git diff --check
```

If Terraform is touched, additionally run the existing offline Terraform
format, validation, mock tests, TFLint, and Trivy gates. The Goal 5 static
validator must fail closed on missing contract fields, unsupported MIME,
plain-Delta policy, unsafe path, mutation in verification SQL, missing
idempotency key, or Goal 6+ resources. No connected plan or execution occurs
in this phase.

## 16. Connected approval sequence

Each boundary is separate and exact:

1. read-only revalidation of identity/workspace/metastore/warehouse and
   source prefixes;
2. saved Terraform plan for the three source objects, only if still required,
   with `goal_5_source_objects_enabled = true`; the default is false;
3. approval and apply of that exact saved plan;
4. strict connected bundle validation for the exact Goal 5 source set, with no
   job/SQL execution. The corrected CDC source set passed this checkpoint on
   `2026-08-13`; durable evidence is
   `docs/verification/GOAL-05-CDC-BUNDLE-VALIDATION-2026-08-13.md` and its
   aggregate is `bd4cd49ee07147f9f240a10b936c78dad76b9dca62622b10f0fb62f6318eb3cd`;
5. approval and bundle deployment, with immediate read-only job/file
   inspection. The corrected source deployment passed on `2026-08-13`; see
   `docs/verification/GOAL-05-CDC-BUNDLE-DEPLOYMENT-2026-08-13.md`;
6. approval for one run of the synthetic Goal 5 workflow on the existing Small
   Serverless warehouse;
7. immediate read-only task/run/warehouse inspection and stop on any failure;
8. offline remediation and static/regression validation for any deterministic
   SQL failure. The single corrected workflow retry on `2026-08-13` reached
   ingestion success but failed the CDC output assertion because a JSON numeric
   field was compared to one text spelling. The approved offline correction
   compares that value numerically while retaining the UPDATE and DELETE
   acceptance semantics; see
   `docs/verification/GOAL-05-CDC-OUTPUT-ASSERTION-REMEDIATION-2026-08-13.md`.
   The fresh strict bundle validation passed on `2026-08-13`; see
   `docs/verification/GOAL-05-CDC-OUTPUT-ASSERTION-BUNDLE-VALIDATION-2026-08-13.md`.
   The separately approved redeployment passed on `2026-08-13`; see
   `docs/verification/GOAL-05-CDC-OUTPUT-ASSERTION-BUNDLE-DEPLOYMENT-2026-08-13.md`.
   A separate workflow-run approval is now required;
9. separate approval for any retry, idempotency rerun, or safe-failure job if
   the first workflow does not cover it deterministically;
10. read-only Tables API format inventory and S3/source/provenance checks.

Unexpected AWS or Databricks resource creation, replacement, destroy, new
warehouse/cluster, production scope, Goal 6+ resource, plain Delta output,
missing source object, or failed task stops the sequence for review.

## 17. Cost and operational controls

No persistent compute is added. The existing Small Serverless SQL Warehouse
with 10-minute auto-stop is reused. The three tiny encrypted source objects
have negligible storage cost; SQL execution is limited to deterministic synthetic
fixtures and must be reported before each billable run. No job retry is
configured implicitly, and no always-on schedule is created.

## 18. Acceptance mapping

The final report must independently mark each Goal 5 criterion PASS,
PASS WITH DISCLOSURE, DEFERRED, FAIL, or UNVERIFIED. Connected evidence is
required for the three actual flows, S3 original-object preservation,
governed output, idempotency behavior, and authoritative table format. Offline
tests cover contracts, adapters, validation errors, quarantine, quality rules,
CDC semantics, unsupported documents, deterministic ordering, and static
scope/security contracts. Deferred production integrations are recorded as
DEFERRED and do not count as failures.

## 19. Stop condition

The offline implementation phase is complete in the reviewed working tree.
The offline and strict bundle-validation stops are complete. The next stop is
the separately approved bundle-deployment boundary. Do not create source
objects, run a connected plan, deploy, execute a job, create compute, or
mutate AWS/Databricks until the exact next checkpoint is separately approved.
