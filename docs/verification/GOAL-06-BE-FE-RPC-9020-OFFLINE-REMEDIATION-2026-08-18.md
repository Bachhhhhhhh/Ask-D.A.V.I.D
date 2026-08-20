# Goal 6 BE-to-FE RPC 9020 remediation — offline evidence

Date: 2026-08-18

Environment: development source only (`736956442295`, `ap-southeast-1`)

Status: offline implementation and validation only. No connected Terraform
plan/apply/destroy, AWS/Databricks mutation, EC2 replacement, ECS task, SQL
operation, or volume operation was performed for this remediation.

## Confirmed cause

The project owner supplied already-gathered connected diagnostics and
explicitly requested that they not be repeated:

- FE `10.42.64.238` is healthy and listens on TCP `9020`;
- BE `10.42.71.97` is healthy and listens on TCP `9050`;
- the dedicated BE data volume is healthy and approximately one percent used;
- BE logs continuously report transport-open timeouts to FE `9020` from
  `report_disk_callback`, `report_tablet_callback`, `report_task_callback`,
  and `report_index_policy_callback`;
- no current security-group rule permits the BE group to initiate TCP `9020`
  to the FE group.

This evidence isolates the remaining defect to network authorization. Local
listeners and healthy EC2 checks cannot substitute for a permitted cross-host
path.

## Declarative remediation

Terraform adds exactly two development-only rules:

1. BE security-group egress to the paired FE security group on TCP `9020`;
2. FE security-group ingress from the paired BE security group on TCP `9020`.

Both rules reference security-group IDs. They add no CIDR, public exposure,
broader port range, instance/user-data change, data-volume action, IAM/KMS
change, ECS/task-definition change, Databricks change, or production change.

Regression coverage requires both rule resources, both exact port bounds, and
the paired source/destination security groups in the Python static suite and
the Terraform module test.

## Offline validation

Executed commands:

```text
python3 scripts/validate_goal6.py
python3 -m pytest -o addopts='' -q tests/unit/test_goal6_static.py tests/unit/test_goal5_static_goal6_regression.py
terraform fmt -check -recursive infrastructure
terraform -chdir=infrastructure/modules/doris-serving init -backend=false
terraform -chdir=infrastructure/modules/doris-serving validate
terraform -chdir=infrastructure/modules/doris-serving test -test-directory=tests
bash -n infrastructure/modules/doris-serving/templates/doris-host.sh.tftpl
python3 -m compileall -q scripts/validate_goal6.py tests/unit/test_goal6_static.py
git diff --check
```

Observed results:

- Goal 6 static validator: PASS;
- focused Python regression suite: PASS (`24 passed`); pytest emitted two
  non-failing cache warnings because the existing `.pytest_cache` is not
  writable;
- Terraform recursive infrastructure formatting check: PASS;
- Doris serving module `terraform validate`: PASS;
- mocked Doris serving module test: PASS (`1 passed`, `0 failed`);
- bootstrap-template shell syntax and targeted Python compilation: PASS;
- `git diff --check`: PASS.

The first module-test execution exposed one test-only assertion that compared
mocked security-group IDs which remain unknown during `command = plan`. The
assertion was corrected to validate the deterministic ingress/egress port
bounds at plan time; the Python static regression continues to validate the
exact SG reference direction. The complete suite then passed as listed above.

## Next approval boundary

After offline validation passes, create one saved connected development plan
only with separate approval. The reviewed action contract is:

- exactly two creates: paired TCP `9020` BE-egress and FE-ingress rules;
- update/replace/destroy: zero;
- EC2, user data, EBS volumes/attachments, IAM/KMS, ECS/task definitions,
  Databricks, public exposure, production, and unrelated actions: zero.

Any different plan must stop for review. Apply requires a separate approval
bound to the saved-plan SHA-256. After apply, read-only evidence must show the
BE callback timeouts have ceased and the BE reports usable storage/capacity
before Goal 6 can continue.
