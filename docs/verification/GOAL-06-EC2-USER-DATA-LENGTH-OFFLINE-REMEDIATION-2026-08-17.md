# Goal 6 EC2 user-data length offline remediation

Date: 2026-08-17
Environment: development only
Status: **OFFLINE IMPLEMENTATION COMPLETE — CONNECTED PLAN/APPLY NOT AUTHORIZED**

## Triggering evidence

The approved connected development plan for the BE storage-capacity correction
stopped before a saved-plan artifact was written. AWS provider validation
rejected the rendered EC2 bootstrap because `user_data` exceeded AWS's
16,384-byte limit. No Terraform apply, EC2/EBS mutation, ECS task, ECR action,
Databricks operation, or AWS control-plane change occurred in that attempt.

## Minimal correction

This remediation only:

1. removes redundant comments from the Terraform-rendered shell template;
2. factors the otherwise unchanged FE and BE `user_data` expressions into
   `local.fe_user_data` and `local.be_user_data`; and
3. adds the fail-closed `ec2_user_data_is_within_aws_limit` Terraform check,
   requiring both deterministic size-equivalents to be at most `16384` bytes.

The shell commands, Docker arguments, discovery variables, storage-root
configuration, capacity check, image references, IAM, KMS, network rules,
volumes, and instance-replacement semantics are unchanged. The guard uses the
fixed 21-byte AWS EBS-volume-ID shape while every other input matches the
instance payload, allowing it to evaluate before a replacement volume has an
allocated ID. A future connected plan fails before review if the resulting
payload budget is too large.

## Offline validation

| Check | Result |
| --- | --- |
| Shell template syntax (`bash -n`) | PASS |
| Goal 6 static validator (`python3 scripts/validate_goal6.py`) | PASS |
| Focused Goal 6 pytest | PASS — 23 passed |
| Python compilation | PASS |
| `terraform fmt -check -recursive infrastructure` | PASS |
| Mocked Doris module Terraform test | PASS — 1 passed, 0 failed |
| Rendered FE size-equivalent | PASS — 14,117 bytes (2,267-byte margin) |
| Rendered BE size-equivalent | PASS — 14,128 bytes (2,256-byte margin) |
| `git diff --check` | PASS |

The development-root `terraform validate` remains **UNVERIFIED** in this run.
Its checked-out `.terraform` directory is owned by `nobody`, so it cannot
update its module manifest. A complete temporary copy was used instead, but
the provider initialization did not reach `validate` before the local tooling
run ended. This is not treated as a configuration PASS; the isolated mocked
Doris module test above is the Terraform evidence for this change.

Ruff, mypy, TFLint, and Trivy remain **UNVERIFIED** on this host unless their
executables become available; this remediation does not infer their results.

## Next approval boundary

After review, a separately approved saved connected development Terraform plan
is required. It must be reviewed anew; it does not authorize an apply, an ECS
task, deletion or creation of any EBS volume, or changes outside the reviewed
Doris bootstrap replacement path.
