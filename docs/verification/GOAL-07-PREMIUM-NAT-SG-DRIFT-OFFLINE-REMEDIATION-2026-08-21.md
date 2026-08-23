# Goal 7 dedicated task SG drift — offline remediation

## Scope

This checkpoint addresses an unexpected change in the saved connected plan
for the Goal 7 indexer image promotion. It is source, test, and documentation
only. No Terraform apply, ECS task, AWS mutation, Databricks operation, ECR
push, bundle deployment, or SQL run occurred here.

## Evidence of the blocker

The saved plan `/tmp/goal7-aoss406-taskdef-20260821.tfplan` has SHA-256
`7833e285c3cbb1b6f2d3a5af0d8421dea77070aed4a38365ae9bbfb637fa68a5`.
Its reviewed output unexpectedly contained:

- one in-place update to `aws_security_group.goal7_tasks[0]` removing the
  three existing explicit egress rules; and
- one replacement of the Goal 7 indexer task definition for the corrected
  image digest `sha256:56263b9c594825f1509f305bb9911b499acd944dcc9971731d04dc18b530a641`.

The expected scope was only the task-definition replacement. The plan was not
applied.

## Root cause and correction

The dedicated SG intentionally declares `egress = []` to prevent the AWS
default allow-all egress rule. Its three allowlisted paths are separate
`aws_vpc_security_group_egress_rule` resources. Without an explicit lifecycle
boundary, Terraform refresh compared the legacy inline attribute with those
separately managed rules and proposed revoking them.

The SG now retains `egress = []` for creation semantics and declares:

```hcl
lifecycle {
  ignore_changes = [egress]
}
```

The separate rule resources remain the source of truth for the Databricks NAT,
AWS interface-endpoint, and S3 gateway-prefix-list paths. This correction is
intended to make a subsequent plan report the existing rules as no-op rather
than removing them.

## Offline validation

The following checks were run after the correction:

- `python3 scripts/validate_goal7.py` — PASS
- Goal 7 static regression tests — PASS (18 passed before adding this
  regression; rerun result is recorded with this checkpoint)
- Python compile check — PASS
- Ruff lint and format checks — PASS
- `git diff --check` — PASS
- `python3 scripts/dev.py infra-preflight` — PASS

Terraform connected planning was deliberately not rerun in this checkpoint.
Terraform type validation was not independently completed because the local
provider/tool invocation was blocked by the environment approval timeout.
Mypy and Trivy are unavailable in this environment; no result is claimed for
those tools.

## Boundary

This checkpoint does not prove the corrected image task, AOSS index creation,
vector upsert/search, authorization rejection, or end-to-end Goal 7
acceptance. A new saved connected plan must be created and reviewed separately
before any apply or task execution.
