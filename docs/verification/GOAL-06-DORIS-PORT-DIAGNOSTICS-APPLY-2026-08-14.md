# Goal 6 Doris port diagnostics — apply and read-only result

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Approved plan SHA-256: `0ea48ac9cf50a38a6b83879b5419ed58798528231fb77acba040c9b6e99db86b`

## Apply result

The exact saved plan applied successfully as `4 added, 0 changed, 4
destroyed`. It replaced only the FE/BE instances and their existing Terraform
volume attachments. The existing encrypted serving-data volumes were not
deleted or reset.

New private hosts:

| Role | Instance | Private IP | Subnet | Public IP | Health |
| --- | --- | --- | --- | --- | --- |
| FE | `i-0c8d9d95e7d635a21` | `10.42.64.238` | `subnet-09bc95f43115dca3e` | none | `ok/ok` |
| BE | `i-03a9c64f31b368055` | `10.42.71.97` | `subnet-09bc95f43115dca3e` | none | `ok/ok` |

Preserved volumes:

- FE `vol-012bc3410278ed85e`, encrypted, attached `/dev/sdf`,
  `DeleteOnTermination=false`;
- BE `vol-01e9b0ed05f7b92b9`, encrypted, attached `/dev/sdf`,
  `DeleteOnTermination=false`.

Both Goal 6 task definitions remain `ACTIVE` at revision 7. Read-only ECS
inspection found no running admin-refresh or verifier task.

## Listener evidence

The new summary contract is now observable in the EC2 console output:

```text
FE: container-diagnostics-summary, listener_state=starting,
    container_state=running, running=true, exit_code=0,
    error_present=false, redacted_log_lines=15
FE: container-diagnostics-summary, listener_state=unavailable,
    container_state=running, running=true, exit_code=0,
    error_present=false, redacted_log_lines=187
FE: doris-port-unavailable, port=9030

BE: container-diagnostics-summary, listener_state=starting,
    container_state=running, running=true, exit_code=0,
    error_present=false, redacted_log_lines=10
BE: container-diagnostics-summary, listener_state=unavailable,
    container_state=running, running=true, exit_code=0,
    error_present=false, redacted_log_lines=12
BE: doris-port-unavailable, port=9050
```

Both `scripts-user` cloud-init handlers then reported failure because the
fail-closed listener guard exited non-zero. The evidence rules out a Docker
launch failure or immediate container exit, but does not yet identify whether
the in-container Doris process is blocked by configuration or persisted
cluster metadata. No host log stream was present in the Doris CloudWatch log
group, so raw container diagnostics remain unavailable through the approved
read-only path.

## Acceptance impact

- EC2 replacement and volume preservation: PASS.
- Private IP, no public IP, subnet, and health checks: PASS.
- Diagnostic summary delivery to console: PASS.
- FE `doris-port-ready` on 9030: FAIL.
- BE `doris-port-ready` on 9050: FAIL.
- No task-before-readiness guard: PASS.

Goal 6 remains `BLOCKED` at Doris application listener readiness. No retry,
volume reset, metadata deletion, task run, SQL/job run, Databricks operation,
or additional Terraform operation was performed after the apply.

## Next action

Use the safe summary evidence to design the next offline declarative
diagnostic improvement or a separately approved persisted-state rebuild plan.
Do not infer that either serving volume is irrecoverable solely from this
result, and do not delete or format either volume implicitly.
