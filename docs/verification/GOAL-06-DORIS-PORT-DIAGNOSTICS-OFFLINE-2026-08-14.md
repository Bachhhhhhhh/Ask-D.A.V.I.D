# Goal 6 Doris port-readiness diagnostics — offline remediation

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: Terraform-owned bootstrap source, static tests, and documentation

## Trigger

Read-only inspection after the persisted private-IP apply showed that both
hosts reached `host-prerequisites-ready` and then emitted:

```text
FE: doris-port-unavailable (9030)
BE: doris-port-unavailable (9050)
```

No `container-launch-failed` or `container-exited` marker was visible, while
the encrypted-volume container stream was delayed or absent. EC2 health and
private-IP/volume attachment checks were healthy. No verifier task was run.
The failure therefore requires process-level evidence before selecting a
configuration or persisted-state repair.

## Offline remediation

The host bootstrap now emits a Terraform-owned
`container-diagnostics-summary` record to the status stream at launch,
listener-ready, listener-unavailable, and container-exited boundaries. The
record is intentionally bounded and contains only:

- listener state and port;
- container present/state/running values;
- numeric Docker exit code;
- a boolean indicating whether Docker reported an error;
- the number of recently available log lines.

Raw Doris output remains in the encrypted-volume `container-diagnostics.log`
after the existing secret-pattern redaction. Raw `docker logs` is never copied
to console or CloudWatch status output. No private IP, IAM/KMS, security-group,
volume, image, task-definition, or external-ingress behavior changed in this
offline remediation.

This provides a safe decision point for the next connected inspection:

- `container-launch-failed` or no container → image/runtime launch diagnosis;
- `container-exited` with an exit code → process/configuration diagnosis;
- `container-diagnostics-summary` with `running=true` and
  `listener_state=unavailable` → in-container listener or persisted-state
  diagnosis;
- `listener_state=ready` → readiness evidence only; it does not authorize a
  task run until both hosts are ready.

## Offline validation

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| Goal 6 static/regression tests | PASS |
| Terraform-template render-equivalent `bash -n` for FE and BE | PASS |
| `git diff --check` | PASS |

Checks requiring a connected AWS/Doris operation remain intentionally
unverified. No Terraform plan/apply/destroy, AWS/Databricks mutation, ECS
task, SQL/job run, bundle operation, ECR operation, volume reset, or metadata
deletion occurred.

The repository `make goal6-static` wrapper could not run because `uv` is not
installed in this environment. Terraform `fmt`/`validate` were not rerun in
this sub-step because the available `/snap/bin/terraform` launcher is blocked
by the sandbox; the source-level validator and render-equivalent shell parse
are the reproducible checks reported above.

## Next approval boundary

After review, create one saved connected development Terraform plan. It must
contain only the reviewed FE/BE bootstrap replacement needed to publish this
summary and zero volume reset/deletion, IAM/KMS, network, security-group,
S3/ECR/Databricks, public-exposure, production, task, or unrelated actions.
Apply requires a separate exact-plan approval. Do not run a verifier task until
both hosts emit `doris-port-ready` and the summary is consistent with a
healthy listener.
