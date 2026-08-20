# Goal 6 Doris log-signal classification — apply and result

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Approved plan SHA-256: `52ec78fc93cc6ada79ed2404a9a04433785022c70817b6b3585738a160f970b0`

## Apply result

The exact saved plan applied successfully as `4 added, 0 changed, 4
destroyed`. New private hosts are:

- FE `i-0fd40482113ec99a0`, `10.42.64.238`, no public IP;
- BE `i-0cc6353584df5a9d4`, `10.42.71.97`, no public IP.

Both remain in the approved private subnet. The existing encrypted serving
volumes were preserved and attached at `/dev/sdf` with
`DeleteOnTermination=false`. No task definition changed and no Goal 6 task
was run.

## Terminal diagnostics

After the bounded listener guard:

```text
FE: listener_state=unavailable, container_state=running, running=true,
    exit_code=0, error_present=false, redacted_log_lines=187,
    log_signal=metadata, doris-port-unavailable (9030)

BE: listener_state=unavailable, container_state=running, running=true,
    exit_code=0, error_present=false, redacted_log_lines=12,
    log_signal=configuration, doris-port-unavailable (9050)
```

The FE signal is consistent with a persisted metadata/cluster-identity issue;
the BE signal is consistent with an in-container configuration/startup issue.
These are diagnostic classifications, not proof that either volume is
irrecoverable. No raw logs were emitted, no CloudWatch host stream appeared,
and no out-of-band shell or volume inspection was performed.

## Acceptance impact

- Exact plan application: PASS.
- Private IP/subnet/no-public-IP/volume preservation: PASS.
- Container launch and runtime state: PASS.
- FE listener 9030: FAIL (`doris-port-unavailable`).
- BE listener 9050: FAIL (`doris-port-unavailable`).
- No task-before-readiness guard: PASS.

Goal 6 remains `BLOCKED` at Doris application readiness. A separate
declarative remediation design is required before any metadata or serving-data
rebuild. No volume reset, format, deletion, task run, or retry was performed.
