# Goal 6 private admin-refresh wrapper — offline remediation

Date: 2026-08-13
Scope: wrapper source, static validation, regression tests, and documentation only
Cloud operation: none

## Change

Added `infrastructure/scripts/run-goal6-admin-refresh.ps1` as the dedicated
Goal 6 private execution path. The existing Goal 3B smoke wrapper remains
unchanged and is not reused.

The wrapper fails closed unless the caller supplies the explicit
`-ConfirmGoal6AdminRefresh` switch and all reviewed inputs pass validation. It
then performs read-only identity and task-definition inspection before one
Fargate `RunTask` request using the supplied private application subnets,
dedicated admin security group, and `assignPublicIp=DISABLED`. It requires the
exact family, revision, Fargate/`awsvpc` shape, container command, and immutable
image digest. It waits for `STOPPED` without retry, verifies exit code and
private ECS attachment metadata, and reads the non-sensitive completion marker
through CloudWatch Logs without printing raw log events.
It does not retrieve secrets or log-event contents and contains no Terraform,
Databricks, S3, or secret-value operation.

## Offline validation

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| `python3 -m py_compile scripts/validate_goal6.py tests/unit/test_goal6_static.py` | PASS |
| `git diff --check` | PASS |
| `python3 -m pytest -q tests/unit/test_goal6_static.py` | UNVERIFIED — system Python has no `pytest` module. |
| `python3 scripts/dev.py goal6-static` / `make goal6-static` | UNVERIFIED — the repository command requires `uv`, which is not installed on this host. |
| Connected AWS/Databricks operation | NOT RUN — prohibited in this approval |
| Wrapper execution / ECS task run | NOT RUN — requires separate task-run approval |

The wrapper is source-only support for the next checkpoint. Goal 6 Doris
health, Unity Catalog integration, refresh, and serving validation remain
UNVERIFIED until a separately approved private admin-refresh task run succeeds.
