# Goal 6 later-phase verifier contracts — offline implementation

Date: `2026-08-18`

Status: `OFFLINE VALIDATED — LOCAL IMAGE BUILT/SCANNED, NOT DEPLOYED`

## Acceptance gaps addressed

The initial Goal 6 image contained admin refresh, positive read-only result,
and rebuild commands, but it had no executable evidence path for:

- Phase 6-11 DML/DDL/database-access rejection;
- Phase 6-12 configured timeout enforcement;
- Phase 6-13 audit identity/target/state/duration/workload correlation.

The Goal requires connected evidence rather than configuration-only claims.
This offline implementation adds separate fail-closed runners for those
acceptance items without launching a task.

## Official Doris 4.x contracts checked

- `SLEEP` is a scalar function taking an integer argument and returning a
  Boolean; official branch-4.0 source defines this signature.
- `SHOW PROPERTY LIKE 'query_timeout'` exposes the current query identity's
  `query_timeout` without requiring grant-level visibility; the `FOR <user>`
  form is reserved for principals with permission to inspect another user's
  properties.
- `SHOW GRANTS` exposes global, database/table, and workload-group privileges.
- `internal.__internal_schema.audit_log` exposes `query_id`, `user`, `state`,
  `query_time`, `stmt`, and `workload_group`; official documentation defines
  `EOF` as successful query execution.
- Temporary tables are session-bound and removed automatically. The CREATE
  negative test uses a valid OLAP temporary-table form.

Primary references:

- <https://github.com/apache/doris/blob/branch-4.0/fe/fe-core/src/main/java/org/apache/doris/nereids/trees/expressions/functions/scalar/Sleep.java>
- <https://doris.apache.org/docs/4.x/sql-manual/sql-statements/account-management/SHOW-PROPERTY/>
- <https://doris.apache.org/docs/4.x/sql-manual/sql-statements/account-management/SHOW-GRANTS/>
- <https://doris.apache.org/docs/4.x/admin-manual/system-tables/internal_schema/audit_log/>
- <https://doris.apache.org/docs/4.x/table-design/temporary-table/>

## Implemented runners

### `doris-rbac-verify`

- Uses only the injected future Query Service read-only identity.
- Requires an approved serving-table SELECT and inspects current grants.
- Rejects any observed admin, node, load, alter, create, or drop privilege.
- Executes actual negative probes for INSERT, UPDATE, DELETE, CREATE, ALTER,
  DROP, and unauthorized audit-database access.
- DML probes use `WHERE FALSE`, so an unexpected allow changes zero rows.
- CREATE targets a session-scoped temporary table.
- ALTER/DROP target only a dedicated disposable authorization probe, never a
  serving result or lakehouse source.
- Accepts only a permission/privilege denial; parser/object-not-found failures
  are rejected as the wrong evidence layer.

The internal schema now declares
`ask_david_serving_development.goal6_authorization_probe`, and the versioned
rebuild migration drops it with the other disposable serving objects.

### `doris-query-limit-verify`

- Uses only the read-only query identity.
- Requires live `query_timeout=30` through the current-user `SHOW PROPERTY LIKE`
  form. It deliberately does not request grant-level visibility for another
  user.
- Runs the official `SLEEP(31)` scalar function under an outer 40-second
  process bound.
- Requires failure at the timeout/cancellation layer and a 25–40 second
  duration; success, early unrelated failure, or outer-timeout-only behavior
  is rejected.
- Performs no DML, DDL, or data scan.

### `doris-audit-verify`

- Uses the dedicated admin secret only to read the internal Doris audit table;
  it also receives the query secret solely to match the expected query user.
- Requires an exact previously recorded query ID.
- Polls for at most 60 seconds.
- Requires identity match, target-table match, `EOF`, numeric `query_time`,
  and `goal6_readonly` workload-group correlation.
- Emits only sanitized booleans/query metadata, never statement text or secret
  values.

## Offline validation

| Check | Result |
| --- | --- |
| POSIX shell parse for all six image runners | PASS |
| Goal 6 static validator | PASS |
| Focused Goal 6 plus Goal 5 regression suite | PASS — 35 tests |
| Mocked complete result contract | PASS |
| Mocked RBAC positive/7-denial contract | PASS |
| Mocked timeout property/enforcement contract | PASS |
| Mocked audit correlation contract | PASS |
| `git diff --check` | PASS |

Two pytest cache warnings are non-failing and result from the existing
non-writable `.pytest_cache` directory.

## Reviewed hashes

- Dockerfile:
  `ce10d57a7071c5cd2034ea45baca496f4359be905d47ae33c2ad14473e6af43e`
- Result runner:
  `ce104f716aa7ae2afb88ec2a761db8140b65426dc97260334d5e63c861765fd7`
- RBAC runner:
  `a33214572f76119576d07ccdc2925ee6ec17961a744eafd91c15a55d29cfce73`
- Query-limit runner:
  `10bc15895bc5c3ff066ba5f8651053f3e8b9100bc72e6f57a48baaa9951d71d7`
- Audit runner:
  `4e417a2f37e27e3aa485aa49aae9886a60027067d6257f59293dfa816761facc`
- Serving schema:
  `59473755c85455c15f739a83f20dc17eb1fb27606181d3efcda205abc8ac7502`
- Rebuild migration:
  `eefcc3972dd382e1e0849505da212f056afe3fff351eb200cdd232777bdd3443`
- Static validator:
  `2ddc878a32b0e207312cf864c9f491e7c213b801d3db21534b26bff3ab44ffa3`
- Regression tests:
  `64212e44d8d681f8421f8de2195f437b95ecf27417c8547e9ff7170376914b8b`

## Deployment and execution boundaries

The reviewed source set was subsequently built and scanned as a local image.
Its source aggregate, local image digest, non-root/runtime checks, and zero
HIGH/CRITICAL Trivy result are recorded in
`GOAL-06-LATER-PHASE-IMAGE-BUILD-SCAN-2026-08-18.md`.

No ECR push occurred, no task definition changed, and no
ECS/Doris/Databricks/Terraform/AWS operation ran. The active revision-8 image
does not contain these runners. After the pending Phase 6-7 admin-refresh
succeeds, promotion still requires a separately approved immutable ECR push
and a separately reviewed/applied Terraform task-definition revision. Each
later runner then requires its own explicit task approval and no-retry
execution contract.
