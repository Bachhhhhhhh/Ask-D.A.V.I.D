# Goal 6 RBAC non-empty DELETE-probe remediation — offline implementation

Date: `2026-08-19`

Status: **OFFLINE VALIDATED — NOT BUILT, PUSHED, DEPLOYED, SEEDED, OR EXECUTED**

## Scope

This implements the approved non-empty DELETE-probe remediation defined in
`GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-REMEDIATION-PLAN-2026-08-19.md`. It changes
only Goal 6 source, static tests, validation, plan/runbook, and durable status.
It does not call AWS, Databricks, Terraform, ECR, ECS, or live Doris.

The established sorted per-file source aggregate for a future verifier-image
build—`docker/Dockerfile.doris-verifier`, all regular files below
`docker/doris-verifier/`, and all regular files below `doris/`—is:

```text
181100d9a1cad8b8285369616a32f0f3a9c848ed15f5b198ff11f85f8f79d673
```

The exact remediated RBAC runner hash is:

```text
2f0a37088a8bd24b88c4cb60eb5723275842326cc2cfb1ee40077f6289f11d9c
```

## Implemented contract

`doris/schemas/01_serving_database.sql` now seeds the disposable
`ask_david_serving_development.goal6_authorization_probe` through the existing
controlled admin schema manifest with two fixed neutral rows:

| Key | Marker | Purpose |
| ---: | --- | --- |
| `126` | `goal6_guard_lower` | Lower sentinel |
| `128` | `goal6_guard_upper` | Upper sentinel |

The table is a `UNIQUE KEY` table, so repeated controlled admin refreshes
converge to the same logical sentinel rows. The existing admin runner already
executes this schema manifest before granting the query-only identity; no
additional admin command or cloud resource was added.

`docker/doris-verifier/doris-rbac-verify` now:

1. requires count `1` for sentinel `126`;
2. requires count `0` for target `127`;
3. requires count `1` for sentinel `128`;
4. emits a sanitized `delete-probe-guard` marker only after all three checks;
5. sends only `DELETE ... WHERE probe_id = 127`; and
6. stops before DELETE for any missing/invalid guard and fails closed if the
   DELETE is unexpectedly allowed.

The ineffective `disable_empty_partition_prune` session setting is removed.
The target remains absent, so even a mistakenly authorized DELETE affects zero
rows and cannot alter a serving result, a sentinel, Unity Catalog, S3, or an
authoritative source.

## Regression coverage

The static contract now requires both exact schema sentinels, all three runner
constants, the sanitized guard marker, the direct reserved-key DELETE, and
absence of both `WHERE FALSE` DELETE and the ineffective session setting.
Runtime mocks cover:

- all seven expected authorization denials with successful guard;
- accepted canonical Doris privilege-token evidence;
- rejection of a generic non-authorization failure;
- stop before DELETE when target key is present;
- stop before DELETE when the lower sentinel is missing;
- sanitized stop on guard-query failure; and
- fail-closed behavior if an absent-key DELETE unexpectedly succeeds.

## Offline validation

| Check | Result |
| --- | --- |
| POSIX shell parse | PASS — `sh -n docker/doris-verifier/doris-rbac-verify` |
| Goal 6 static validator | PASS — `python3 scripts/validate_goal6.py` |
| Goal 6 regression suite | PASS — 44 tests |
| Goal 5/6 cross-goal regression | PASS — 1 test |
| Python compilation | PASS — `python3 -m compileall -q scripts/validate_goal6.py` |
| Diff integrity | PASS — `git diff --check` |

Pytest emitted only `.pytest_cache` permission warnings; no test failed.

## Next approval boundary

This code is not in the deployed revision-12 image. A separately approved
local image build/scan is required before any ECR promotion, Terraform
task-definition update, admin seed refresh, or RBAC verification task. The
admin seed refresh and RBAC task each require their own approval.
