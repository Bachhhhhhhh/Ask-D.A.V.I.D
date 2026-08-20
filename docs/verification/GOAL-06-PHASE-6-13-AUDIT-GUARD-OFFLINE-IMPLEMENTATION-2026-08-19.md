# Goal 6 Phase 6-13 audit guards — offline implementation

Date: `2026-08-19`

Status: `PASS — OFFLINE VALIDATED; NOT BUILT, DEPLOYED, OR EXECUTED`

## Approved scope

The approved remediation changed only the version-controlled audit guards,
static validator, regression tests, runbook, and durable evidence. No
Terraform, ECR, ECS task, Doris SQL, Databricks, or AWS operation occurred.

## Implemented guards

- `doris-admin-refresh` now reads back
  `SHOW VARIABLES LIKE 'enable_audit_plugin'` immediately after the audit
  migration and emits `audit-plugin-disabled` or `audit-plugin-unreadable`
  instead of claiming refresh completion.
- `doris-audit-verify` now requires the plugin to be enabled, verifies that the
  audit table is readable and non-empty, and distinguishes
  `audit-plugin-disabled`, `audit-plugin-unreadable`, `audit-log-empty`, and
  `audit-log-unreadable` from the existing exact-ID miss.
- Exact query-ID, identity, target, `EOF`, duration, and workload-group checks
  remain unchanged. No latest-row fallback or privilege broadening was added.
- Static validation, mocked failure-class coverage, and runbook guidance were
  updated.

## Offline validation

| Check | Result |
| --- | --- |
| `sh -n` admin and audit runners | PASS |
| `python3 scripts/validate_goal6.py` | PASS |
| Focused Goal 5/6 regression suite | PASS — `46 passed` |
| `git diff --check` | PASS |
| Pytest warnings | 2 non-failing cache-permission warnings |

## Reviewed source hashes

| File | SHA-256 |
| --- | --- |
| `docker/doris-verifier/doris-admin-refresh` | `ca2aa999675ed47b8236344e966933c93d207d16bfa527474a62fe96b0cebcae` |
| `docker/doris-verifier/doris-audit-verify` | `2b2c9316c0dffcf3aebac0611769e553e6fe43964ed3aa5cff7f79cc74b21da4` |
| `scripts/validate_goal6.py` | `2878c3df91ad85093e54eaeff206fcf3adeda03cc64b49c8c015958d7efa044c` |
| `tests/unit/test_goal6_static.py` | `b577a0a9703cd31a09454b2fc369a42d4d4f78a088f338d0e36c94856aba56e8` |
| `docs/runbooks/GOAL-06-DORIS.md` | `fa1535304077d3bd1009878667874311afbe07408cb5045b277c671bf821f878` |

## Checkpoint

The current revision-15 ECS task definitions still reference the prior image;
these source changes are not deployed. Phase 6-13 remains **UNVERIFIED**.
Building/scanning a new immutable image, ECR promotion, task-definition plan,
apply, admin refresh, fresh result task, and audit task each require their own
explicit approval boundaries.
