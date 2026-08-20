# Goal 6 FE listener bootstrap remediation — offline implementation

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: Terraform source, tests, documentation, and offline validation only

## Trigger and evidence

The approved private `admin-refresh:3` task reached `STOPPED` with container
exit code `1` and reported:

```text
ERROR 2002 (HY000): Can't connect to server on '10.42.76.67' (115)
```

The subsequent read-only diagnosis proved that the SG, local VPC route, NACL,
and private task path accepted TCP/9030. EC2 console output showed that Docker
pulled and launched the pinned FE/BE images, but it did not prove that the
processes remained bound to their service ports. The exact durable diagnosis
is recorded in
`GOAL-06-PRIVATE-ADMIN-TASK-REVISION-3-2026-08-13.md`.

## Root cause addressed by this remediation

The Terraform host bootstrap mounted `fe.conf`/`be.conf` but started the
official Doris FE/BE Docker images without the image entrypoint's required
discovery variables. The Docker command could therefore return a container ID
without establishing a usable FE query listener. The remediation follows the
official Docker deployment contract: FE receives `FE_SERVERS` and `FE_ID`; BE
receives `FE_SERVERS` and `BE_ADDR`; both receive the private network hint.
The contract is documented in the [Apache Doris Docker quick start](https://doris.apache.org/docs/4.x/getting-started/quick-start/)
and the upstream [Doris Docker runtime documentation](https://apache.googlesource.com/doris/+/refs/heads/master/docker/runtime/).

## Declarative changes

- Render the FE private address into BE user data from the Terraform-managed FE
  instance; the FE derives its own private address from the local interface at
  boot. No static cloud credential or public endpoint is introduced.
- Pass `FE_SERVERS=fe1:<private-ip>:9010` and `FE_ID=1` to the FE container.
- Pass `FE_SERVERS=fe1:<fe-private-ip>:9010` and
  `BE_ADDR=<be-private-ip>:9050` to the BE container.
- Add a local-only readiness guard: cloud-init emits a non-sensitive
  `doris-port-ready` marker only after the container remains running and its
  private 9030 (FE) or 9050 (BE) socket accepts; otherwise it emits
  `doris-port-unavailable` and exits non-zero. It does not alter ingress.
- Persist the non-sensitive bootstrap lifecycle markers in the encrypted
  role-volume log directory (`bootstrap-status.log`) so the dedicated
  CloudWatch stream can distinguish bootstrap-pending, container-exited, and
  listener-ready states. EC2 `running`/platform checks are not treated as
  application readiness.
- Add explicit FE bootstrap generation `2` and
  `user_data_replace_on_change = true`, so the next saved Terraform plan
  makes the FE replacement/re-attachment action visible and reviewable. The
  existing encrypted FE metadata and BE serving-data volumes remain
  Terraform-owned and are not replaced by this source change.
- Add static regression coverage for discovery variables, private-IP guards,
  readiness markers, generation wiring, and the two deliberate host
  replacements.

## Expected connected-plan boundary

This offline change does not create a plan or mutate AWS. A later explicitly
approved saved development plan must be inspected for the exact FE/BE
replacement and volume-attachment actions. Any unexpected destroy, public
exposure, IAM/KMS/network/Databricks change, production action, or source-data
change is a stop condition.

## Offline validation

| Check | Result |
| --- | --- |
| Goal 6 static validator | PASS |
| Terraform formatting/validation | PASS — Terraform `validate` succeeded with the locked providers |
| Terraform tests | PASS — 7 tests passed |
| Python unit tests | UNVERIFIED — pytest is unavailable in the current host environment |
| Shell syntax checks | PASS for verifier runners and a rendered FE host template |
| `git diff --check` | PASS |

## Revision after revision-4 task failure

The revision-4 private admin task reached a private ENI but failed with
`ERROR 2002 (HY000): Can't connect to server on '10.42.78.72' (115)`. The
offline correction in this checkpoint adds durable bootstrap markers and a
runbook gate requiring `doris-port-ready` evidence for both hosts before any
future task launch. It does not open network ingress, change IAM/KMS, or run a
task. A new connected plan is required only if the source change produces a
Terraform action; no plan or AWS operation is performed in this offline step.

The initial sandboxed Terraform validation attempt could not start the cached
provider plugins; rerunning the same offline commands with provider-process
execution enabled passed and did not contact AWS.

No Terraform connected plan/apply, AWS/Databricks operation, ECS task, ECR
push, bundle deployment, or SQL run occurred in this remediation.
