# Goal 6 Phase 6-6 private verifier endpoint remediation — offline validation

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **OFFLINE IMPLEMENTED AND VALIDATED — CONNECTED PLAN REQUIRED**

## Scope and boundary

The one approved Phase 6-6 health task stopped before its container started.
Read-only diagnosis proved that the verifier security group could not reach the
existing Secrets Manager interface endpoint on TCP `443`. The endpoint, private
DNS, exact Secrets Manager/KMS execution-role permissions, and private task
placement were otherwise confirmed. The task's bounded MariaDB health ping did
not execute and is not retried by this remediation.

This offline change adds exactly one Terraform-managed
`aws_vpc_security_group_ingress_rule`:

| Attribute | Contract |
| --- | --- |
| Resource | `goal6_verifier_to_aws_endpoints` |
| Destination security group | Existing `module.network.aws_endpoints_security_group_id` |
| Source security group | Existing `module.doris_verifier.verifier_security_group_id` |
| Protocol / port | TCP `443` only |
| Addressing | Security-group reference only; no `cidr_ipv4` |
| Exposure | Private AWS interface endpoints only; no public ingress |

It mirrors the existing narrow Goal 6 admin-task endpoint rule. It does not
change IAM, KMS, Secrets Manager objects or values, task definitions, ECS
tasks, ECR, Databricks, Doris host security groups, source data, or any
production resource.

## Offline validation evidence

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| `pytest -q -o addopts='' tests/unit/test_goal6_static.py tests/unit/test_goal5_static_goal6_regression.py` | PASS — 20 passed; two non-functional cache-permission warnings |
| `terraform fmt -check -recursive infrastructure` | PASS |
| Isolated `terraform init -backend=false -plugin-dir=<local provider cache>` | PASS — local cache only, no backend |
| Isolated `terraform validate` for `modules/doris-serving` | PASS |
| Isolated `terraform test` for `modules/doris-serving` | PASS — 1 passed, 0 failed |
| Isolated development-root `terraform init -backend=false -plugin-dir=<local provider cache>` | PASS — local cache only, no backend |
| Isolated development-root `terraform validate` | PASS |
| Isolated development-root `terraform test -test-directory=tests` | PASS — 7 passed, 0 failed |
| `git diff --check` | PASS |

`ruff`, `mypy`, `bandit`, `detect-secrets`, `tflint`, `trivy`, and `uv` are not
installed on this host. The system `pytest` also lacks `pytest-cov`, so the
targeted suite was deliberately run with project coverage addopts disabled;
the existing Goal 6 policy excludes Pydantic-dependent checks from its
acceptance gate. These unavailable tools are not represented as passing checks.

## Next approval boundary

Before any AWS mutation, reverify the approved account and region, create a
saved connected development Terraform plan, and inspect it. The only accepted
managed-resource action is one in-place create of this endpoint SG ingress rule.
The plan must contain zero replacement, destroy, public exposure, IAM/KMS,
task-definition, Databricks, or production changes. Applying that plan and any
single ECS health-task retry each require separate explicit approval.
