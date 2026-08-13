# Goal 5 MVP Phase 5-1 design review

## Review status

**DESIGN READY — IMPLEMENTATION NOT APPROVED**

The Phase 5-1 design in
`docs/plans/GOAL-05-MVP-INGESTION-PLAN.md` was reviewed offline on
2026-08-12 against the Goal 5 objective, repository governance, accepted ADRs,
Goal 4 evidence, current Databricks preflight, and the current repository
layout.

No source implementation, Terraform edit, bundle edit, SQL edit, AWS
operation, Databricks mutation, table mutation, job run, or compute creation
occurred during this review.

## Design review matrix

| Requirement | Result | Evidence or boundary |
| --- | --- | --- |
| Synthetic-only structured, document, and CDC MVP | PASS | Three neutral fixture paths; real Green SM data and production connectors are excluded. |
| Unity Catalog authority and approved S3 storage | PASS | Existing catalog, schemas, IAM credential, external locations, and managed storage are reused. |
| Accepted table-format profile | PASS WITH DISCLOSURE | Native ICEBERG or verified managed Delta UniForm; no plain Delta; actual Tables API format is recorded. |
| Contract and adapter boundary | PASS | JSON contracts plus typed SourceAdapter, FileSourceAdapter, DocumentSourceAdapter, and CDCSourceAdapter are specified. |
| Provenance and run model | PASS | Unique run ID, source version, counts, status, and record/document/event provenance are required. |
| Structured requirements | PASS | CSV schema validation, quarantine reason, deterministic primary-key deduplication, quality rules, Raw → Curated → Business. |
| Document requirements | PASS | TXT/Markdown only, original object in approved S3, metadata/version/provenance table, no chunking/embedding/indexing. |
| CDC requirements | PASS | INSERT/UPDATE/DELETE, raw history, deterministic ordering, event-id deduplication, documented tombstone current state. |
| Idempotency and safe failures | PASS | Stable source keys are separate from run IDs; repeats do not duplicate trusted output; invalid inputs remain quarantined. |
| Existing compute reuse | PASS | Existing Small Serverless SQL Warehouse is reused; no persistent cluster or warehouse is proposed. |
| AWS scope | PASS WITH APPROVAL | At most three Terraform-managed source objects in existing buckets; expected plan is three creates and no replacement/destroy/unrelated actions. |
| Security and ADR boundaries | PASS | No credentials in contracts/logs; no agent access, Doris, OpenSearch, Glue, or ADR edits. |
| Validation and stop conditions | PASS | Offline gates precede connected boundaries; any unexpected resource, format, scope, or task failure stops for review. |

## Open approval boundary

At the time of this report, implementation remained **AWAITING EXPLICIT DESIGN
APPROVAL**. That boundary has since been resolved by the current offline-only
Phase 5-2 implementation checkpoint; the report remains a historical design
review and does not authorize connected operations. The implementation phase
must not:

- run Terraform plan/apply/destroy;
- deploy or validate a connected Databricks bundle;
- execute SQL/jobs;
- mutate AWS or Databricks;
- create compute;
- modify Goal 4 tables.

The first connected boundary after offline validation is a separate,
saved-plan review for the three source objects, only if a read-only supported
source path cannot be used. Bundle deployment and workflow execution each
require separate approvals.

## Known limitations

- The current Tables API shows existing Goal 4 tables as managed Delta UniForm;
  this is accepted but must remain explicitly disclosed.
- The exact runtime support for the planned SQL `read_files` and parameterized
  source-path expressions must be confirmed by strict connected bundle/SQL
  capability checks at their approval boundaries.
- At the time of this design review, no Goal 5 output, table, source object,
  job, or adapter had been implemented or verified yet. Current implementation
  status is recorded separately by the Phase 5-2 report.

## Review conclusion

Phase 5-1 design was internally consistent with the repository and approved
architecture. Its implementation authorization and offline results are
recorded in the Phase 5-2 report; connected execution remains a separate
approval boundary.
