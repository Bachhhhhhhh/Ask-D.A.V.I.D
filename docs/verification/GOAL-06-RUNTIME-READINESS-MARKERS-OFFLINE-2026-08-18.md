# Goal 6 runtime readiness markers — offline remediation

Date: `2026-08-18`

Status: `OFFLINE VALIDATED — CONNECTED TASK NOT RUN`

## Purpose

The TCP `9020` security-group remediation is applied and VPC Flow Logs prove
BE-to-FE traffic changed from `REJECT` to bidirectional `ACCEPT`. The current
FE/BE bootstrap processes have completed, however, and neither the current EC2
console output nor `/ask-david-development/doris` contains a current FE/BE host
stream with the required application markers. Historical or absent markers are
not sufficient evidence of current Doris readiness.

This change adds a deterministic, non-mutating evidence path without replacing
or restarting either healthy EC2 host.

## Implemented contract

- PowerShell wrapper:
  `infrastructure/scripts/run-goal6-readiness-markers.ps1`
- Linux/Bash wrapper:
  `infrastructure/scripts/run-goal6-readiness-markers.sh`
- The Bash wrapper is the executable path in the current environment because
  `pwsh` is not installed.
- Both wrappers fail closed on account, region, immutable task-definition
  revision/image, private Fargate network mode, task command/entrypoint,
  private subnets, admin security group, FE/BE address, or injected-secret
  reference mismatch.
- The task override is exactly `[-c, <script>]`, matching the reviewed image's
  `/bin/sh` entrypoint.
- The task executes only the bounded, read-only `SHOW BACKENDS;` statement.
- Secret JSON is parsed only inside the task, the password is supplied through
  `MYSQL_PWD`, and neither credentials nor raw backend rows are logged.
- No refresh, DDL, DML, S3 write, Databricks operation, Terraform operation,
  infrastructure mutation, or implicit retry is present.

Success requires and records all five CloudWatch markers:

1. FE `listener_state=ready`;
2. FE `doris-port-ready`, port `9030`;
3. BE `listener_state=ready`;
4. BE `doris-port-ready`, port `9050`;
5. BE `be-storage-capacity-ready`, with `alive=true`,
   `decommissioned=false`, and `non_zero_total_capacity=true`.

The FE markers are emitted only after an authenticated SQL connection to FE
succeeds. The BE markers are emitted only when FE's live `SHOW BACKENDS` row
for `10.42.71.97` meets every health and capacity condition. This is
FE-control-plane evidence of the BE heartbeat/listener and storage state; it
does not claim that a historical host-bootstrap stream was reconstructed.

## Offline validation

| Check | Result |
| --- | --- |
| `bash -n infrastructure/scripts/run-goal6-readiness-markers.sh` | PASS |
| `python3 scripts/validate_goal6.py` | PASS |
| Focused Goal 6 plus Goal 5 regression tests with repository coverage addopts disabled | PASS — 26 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |
| Native PowerShell parse/runtime | UNVERIFIED — `pwsh` is not installed; the Bash implementation is the reviewed runnable path |

The initial system `pytest` invocation inherited repository coverage arguments
but the system environment lacks `pytest-cov`; it stopped during option parsing
before collecting tests. Re-running the focused suite with
`-o addopts=''` executed all 26 targeted tests successfully. Two non-failing
warnings report that the pre-existing `.pytest_cache` directory is not
writable.

## Reviewed source hashes

- Bash wrapper:
  `cb9a1e794dd833836e18ae590a830910b34b1a064edf5821eb505064eb0179af`
- PowerShell wrapper:
  `83b6e90a812cb367a04541b4f16075ae941182a9444ea91241f1e0db23a874f3`
- Static validator:
  `587d09b7ca96f1181d2853fe28dd6e0ff4cf93b90cc58fe760f35ebd49cb6cf2`
- Regression tests:
  `276a3dd1b5fdccc8f9242f98d9355e08b95226a47f874ada90f013403913499a`

## Approval boundary

No ECS task, Terraform operation, AWS mutation, ECR operation, Databricks
operation, or SQL execution occurred during this offline remediation.

The next action requires separate approval for exactly one private diagnostic
task. It must use the reviewed revision-8 admin task definition and immutable
image, two approved private application subnets, the existing admin security
group, `assignPublicIp=DISABLED`, and the exact read-only marker command. It
must stop without retry if the task exits non-zero or any marker is absent.
