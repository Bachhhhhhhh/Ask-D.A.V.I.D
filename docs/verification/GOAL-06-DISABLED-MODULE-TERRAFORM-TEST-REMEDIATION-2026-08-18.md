# Goal 6 disabled-module Terraform test remediation

Date: `2026-08-18`

Status: **OFFLINE VALIDATED — CONNECTED PLAN NOT CREATED**

## Trigger

The approved pre-plan offline gate stopped before any connected Terraform
operation. Development-root mock tests evaluated the Doris bootstrap locals
while `goal_6_enabled=false`. Those locals indexed Terraform resources with
`count = 0` and passed absent Goal 6 secret ARNs to `templatefile`, so the
disabled foundation and Goal 4 plans failed before a saved plan could be
created.

No AWS or Databricks state was read by the failed test. No connected plan,
apply, destroy, ECS task, bundle, SQL, or cloud mutation occurred.

## Minimal remediation

The four FE/BE bootstrap locals now render only when `var.enabled=true`:

- FE instance user data;
- BE instance user data;
- FE deterministic size-check payload;
- BE deterministic size-check payload.

Disabled mode returns an empty local value and cannot evaluate counted
resources or absent secret inputs. Enabled mode keeps the existing template,
inputs, generation markers, instance assignment, replacement semantics, and
16,384-byte fail-closed guard unchanged.

Static validation and regression tests require all four enabled gates. The
existing development and Goal 4 Terraform tests provide the disabled-mode
regression, while the isolated Doris module test exercises enabled mode.

## Offline validation

| Check | Result |
| --- | --- |
| Goal 6 static validator | PASS |
| Focused Goal 6/Goal 5 regression pytest | PASS — 39 tests |
| Python compilation | PASS |
| Infrastructure preflight | PASS |
| Shell wrapper syntax | PASS |
| Terraform format check | PASS |
| Development-root Terraform validate | PASS |
| Development/Goal 4 mock Terraform tests | PASS — 7 passed, 0 failed |
| Isolated enabled Doris-module validate | PASS |
| Isolated enabled Doris-module mock test | PASS — 1 passed, 0 failed |
| TFLint `0.61.0` recursive scan | PASS |
| Trivy `0.69.3` infrastructure scan | PASS — 0 HIGH/CRITICAL |
| Trivy `0.69.3` Doris-module scan | PASS — 0 HIGH/CRITICAL |
| `git diff --check` | PASS |

The focused pytest invocation used `-o addopts=''` because this host has
`pytest` but not the repository-configured `pytest-cov` plugin. Two existing
non-failing cache-write warnings were emitted. Pydantic-dependent platform
tests remain outside Goal 6 acceptance as already approved and documented.

The direct module directory currently pins AWS provider `6.60.0`, which was
not present in the offline cache. The enabled module test therefore ran from
an exact temporary source copy using cached provider `6.56.0`, which satisfies
the module's declared `>= 5.0, < 7.0` constraint. The authoritative development
root used its checked-in lock versions: AWS `6.56.0`, Databricks `1.122.0`, and
Random `3.9.0`.

## Security and architecture impact

- No secret value is introduced or rendered in disabled mode.
- No IAM, KMS, network, EC2, EBS, ECS, Databricks, or S3 behavior changes.
- Doris remains a rebuildable serving layer; S3/Iceberg and Unity Catalog
  authority are unchanged.
- No accepted ADR and no Goal 7+ scope changed.

## Next approval boundary

The offline blocker is resolved. Creating a saved connected development plan
for the two task-definition image revisions requires a separate approval. The
expected plan remains exactly two ECS task-definition replacements/new
revisions and zero other AWS/Databricks action. This report does not authorize
that plan or any apply/task execution.
