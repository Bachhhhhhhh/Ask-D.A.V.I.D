# Goal 6 representative result contract — offline remediation

Date: `2026-08-18`

Status: `OFFLINE VALIDATED — LOCAL IMAGE BUILT/SCANNED, NOT DEPLOYED`

## Gap

The existing read-only verifier emitted source dataset, refresh timestamp,
query ID, row count, and duration, but it omitted the required
`query_result`. It also issued `SELECT LAST_QUERY_ID()` through a separate
MariaDB client connection after the count query. That is insufficient evidence
that the recorded ID belongs to the representative result query.

This gap affects Phase 6-13 and final acceptance item 39. It does not affect
the already deployed revision-8 admin-refresh runner or the pending Phase 6-7
task.

## Remediation

`docker/doris-verifier/doris-readonly-verify` now performs one TLS MariaDB
session containing:

1. selection of the fixed read-only workload group;
2. one deterministic representative row from the internal serving table;
3. immediate `SELECT LAST_QUERY_ID()` in that same session;
4. serving row count and maximum refresh timestamp.

The runner validates the exact three-line/tabular response, numeric fields,
non-empty provenance/timestamps/query ID, and the allowlisted source-table
name. It emits one JSON object containing:

- `query_result` with neutral metric date/category/count/total and provenance;
- `source_dataset`;
- `refresh_timestamp`;
- `executed_query_id`;
- `row_count`;
- `execution_duration`;
- `started_at`.

It remains strictly read-only and contains no INSERT, UPDATE, DELETE, CREATE,
DROP, or ALTER statement.

## Offline evidence

| Check | Result |
| --- | --- |
| POSIX shell parse | PASS |
| Goal 6 static validator | PASS |
| Focused Goal 6 plus Goal 5 regression tests | PASS — 28 tests |
| Mocked single-session result-contract execution | PASS — typed JSON and exact provenance/result assertions |
| `git diff --check` | PASS |

The focused pytest run emitted two non-failing warnings because the existing
`.pytest_cache` directory is not writable.

## Reviewed hashes

- Read-only verifier:
  `ce104f716aa7ae2afb88ec2a761db8140b65426dc97260334d5e63c861765fd7`
- Goal 6 static validator:
  `63c3d82ddcd86fe58661919e7a498db3c6d57339186087905e0ebf26c5bb37a2`
- Regression tests:
  `8138a96edcf57774b8d23f39b8de8109acdb18f3039f2e0f2df2711e1ff51604`

## Deployment boundary

The remediated source was subsequently packaged in a local image and scanned;
the exact source aggregate, local image digest, runtime checks, and vulnerability
result are recorded in
`GOAL-06-LATER-PHASE-IMAGE-BUILD-SCAN-2026-08-18.md`.

No ECR push, Terraform plan/apply, task-definition update, ECS task, Doris SQL,
Databricks operation, or AWS mutation occurred. The current revision-8 task
definitions still reference the prior immutable image and therefore do not
contain this verifier remediation. After Phase 6-7 admin-refresh succeeds, the
local artifact must be pushed under a new immutable ECR digest after separate
approval and registered in new task-definition revisions through a separately
reviewed saved Terraform plan. No later verifier result may claim this contract
until that deployment sequence completes.
