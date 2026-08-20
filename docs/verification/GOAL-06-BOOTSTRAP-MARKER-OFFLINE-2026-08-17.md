# Goal 6 bootstrap-marker remediation — offline evidence

Date: 2026-08-17

Environment: development source only (`736956442295`, `ap-southeast-1`)
Status: offline implementation and validation only; no connected plan/apply,
AWS/Databricks mutation, instance replacement, ECS task, or volume operation
was performed for this change.

## Trigger

The current FE and BE instances are `running` with `ok/ok` EC2 health checks,
but their latest console output contains only early kernel/network/cloud-init
messages. No Doris lifecycle marker or dedicated host CloudWatch stream is
currently available. The existing bootstrap emitted its first durable marker
only after volume mount, package installation, and CloudWatch-agent startup,
so a missing or early-failing user-data run could be indistinguishable from a
listener failure.

## Offline implementation

The Terraform-owned host template now:

- emits a non-secret `bootstrap-invoked` marker immediately at script entry;
- writes the marker to stdout, the root log
  `/var/log/goal6-doris-bootstrap.log`, and the system journal;
- installs an EXIT trap that emits `bootstrap-failed` with only the numeric
  exit code when the script exits before readiness;
- copies the pre-mount root markers into the encrypted role-volume
  `bootstrap-status.log` after the volume is mounted;
- collects the root marker file through a dedicated CloudWatch stream
  `{instance_id}/<role>/bootstrap-root` once the agent is available;
- retains the existing bounded, non-secret `doris-port-ready`,
  `doris-port-unavailable`, and diagnostics-summary contract.

The readiness marker remains fail-closed: `bootstrap-invoked` or
`bootstrap-failed` is diagnostic evidence only and cannot authorize an ECS
task. FE and BE must still independently emit `doris-port-ready`.

## Validation

The following checks are required for this offline change:

```text
python3 scripts/validate_goal6.py
python3 -m pytest -o addopts='' -q tests/unit/test_goal6_static.py tests/unit/test_goal5_static_goal6_regression.py
git diff --check
```

Observed results:

- `python3 scripts/validate_goal6.py` — PASS;
- targeted Goal 6/static regression tests — PASS (`19 passed`);
- `bash -n infrastructure/modules/doris-serving/templates/doris-host.sh.tftpl` — PASS;
- targeted Python compilation — PASS;
- `git diff --check` — PASS;
- `make goal6-static` — NOT RUN because `uv` is not installed; the underlying
  validator was run directly and passed.

Terraform connected planning/apply, instance replacement, SSM setup, CloudWatch
mutation, ECS task execution, and volume reset remain outside this remediation.

## Next approval boundary

If the offline checks pass, create a new saved development Terraform plan and
inspect it before any apply. The expected connected action is limited to the
reviewed FE/BE user-data replacement required to deliver this template change;
unexpected volume, IAM, KMS, network, security-group, task-definition,
production, public-exposure, or destroy actions must be zero. A separate
hash-bound approval is required before applying that exact plan.
