# Goal 6 RBAC non-empty DELETE-probe remediation plan

Date: `2026-08-19`

Status: **PLANNED — OFFLINE ROOT CAUSE CONFIRMED; NOT IMPLEMENTED**

## Triggering evidence

The one approved revision-12 RBAC verifier run stopped at DELETE with
`unexpected-allow`, after INSERT and UPDATE had produced authorization-layer
denials. The durable evidence is
`docs/verification/GOAL-06-RBAC-REVISION-12-EMPTY-PARTITION-RETRY-FAILURE-2026-08-19.md`.
The live disposable `goal6_authorization_probe` was empty; no retry followed.

## Confirmed root cause

The pinned Apache Doris 4.0.1 source at commit
`791725594deffd195e7fae19e00e03c3232f105a` establishes the following order:

1. `PruneEmptyPartition` calls `OlapTable.selectNonEmptyPartitionIds` and
   changes a scan with no non-empty selected partition into
   `LogicalEmptyRelation`.
2. `DeleteFromCommand` receives the resulting `PhysicalEmptyRelation`, calls
   `processEmptyRelation`, and returns before its later
   `checkTblPriv(..., PrivPredicate.LOAD)` branch.
3. The repository table is an unpartitioned, one-bucket `UNIQUE KEY` OLAP
   table and had no rows, so a DELETE of absent key `127` retained that
   empty-relation path.

The revision-12 guard sent `SET disable_empty_partition_prune = true` and the
DELETE in one MariaDB client invocation. Full-text inspection of the same
pinned source shows that this session variable is declared in
`SessionVariable` and is consulted by `CloudPartition`, but
`PruneEmptyPartition` itself does not consult it. It is therefore not a
reliable control for this local OLAP authorization-probe table. The connected
revision-12 result confirms that it did not force the required privilege path.

Primary-source references:

- [`DeleteFromCommand.java`](https://github.com/apache/doris/blob/791725594deffd195e7fae19e00e03c3232f105a/fe/fe-core/src/main/java/org/apache/doris/nereids/trees/plans/commands/DeleteFromCommand.java)
- [`PruneEmptyPartition.java`](https://github.com/apache/doris/blob/791725594deffd195e7fae19e00e03c3232f105a/fe/fe-core/src/main/java/org/apache/doris/nereids/rules/rewrite/PruneEmptyPartition.java)
- [`CloudPartition.java`](https://github.com/apache/doris/blob/791725594deffd195e7fae19e00e03c3232f105a/fe/fe-core/src/main/java/org/apache/doris/cloud/catalog/CloudPartition.java)
- [`SessionVariable.java`](https://github.com/apache/doris/blob/791725594deffd195e7fae19e00e03c3232f105a/fe/fe-core/src/main/java/org/apache/doris/qe/SessionVariable.java)

## Minimal remediation design

The correction is deliberately confined to the disposable internal Doris
authorization probe. It does not change Unity Catalog, S3, the authoritative
Business source, the serving result table, application-facing data, or any
cloud topology.

1. The privileged, controlled admin refresh must idempotently establish two
   fixed sentinel keys in `goal6_authorization_probe`: `126` and `128`. Their
   markers are fixed neutral technical strings. The query-only identity cannot
   insert, update, or delete these rows.
2. The query-only RBAC runner must require all three preconditions before
   DELETE: key `126` exists, key `128` exists, and reserved target key `127`
   is absent. It must emit only a sanitized guard marker and stop before DELETE
   on any failed precondition.
3. The DELETE remains exactly `WHERE probe_id = 127`. It must remove the
   ineffective `disable_empty_partition_prune` setting and must not restore
   `WHERE FALSE`.
4. With live rows on both sides of target `127`, the one unpartitioned probe
   partition is non-empty and its key range includes the absent target. Doris
   must consequently reach the ordinary `LOAD_PRIV` check rather than return
   through the empty-relation shortcut.
5. If the query-only identity were mistakenly granted DELETE/LOAD privilege,
   the target key remains absent; the statement affects zero rows. The runner
   still emits `unexpected-allow`, exits non-zero, and stops without running
   later probes. The sentinels remain untouched.

## Planned implementation surface

No executable source is changed by this plan. A separately approved offline
implementation would modify only these Goal 6-owned files:

- `doris/schemas/01_serving_database.sql` or a new ordered internal-only
  schema/migration file, to define the idempotent two-sentinel admin seed;
- `docker/doris-verifier/doris-admin-refresh`, to apply that controlled seed
  before read-only grant use;
- `docker/doris-verifier/doris-rbac-verify`, to enforce three preconditions,
  use the absent in-range target, and remove the ineffective session setting;
- `tests/unit/test_goal6_static.py`, `scripts/validate_goal6.py`, the Goal 6
  plan/runbook, and durable verification/status documents.

The implementation must include mocks proving: the seed is limited to the
disposable table and exact keys; all guard queries precede DELETE; a failed
guard emits no DELETE; an allowed DELETE stops the runner; and the prior
empty-table/session-setting pattern cannot return.

## Required approval sequence after implementation

1. approve offline source/tests/docs implementation and validation;
2. approve a local image build/scan;
3. approve immutable ECR promotion;
4. approve a task-definition-only Terraform plan and then its reviewed apply;
5. approve exactly one private admin refresh to establish the sentinels;
6. approve exactly one private, no-retry RBAC verifier task.

Each connected task remains independent. Any non-zero exit, missing sentinel
guard, wrong rejection layer, unexpectedly allowed statement, or mutation
outside the disposable probe requires a stop for review.

## Non-actions

This analysis did not alter executable source, build or push an image, invoke
Terraform, run an ECS task, query live Doris, access Databricks, or mutate AWS.
