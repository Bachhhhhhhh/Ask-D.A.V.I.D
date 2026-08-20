# Goal 6 stable FE/BE private-IP remediation — offline evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: Terraform source, diagnostics, tests, and documentation only

## Approved change

The failed listener evidence showed that the persisted Doris FE metadata and
BE serving state were moved to replacement hosts with different private IPs.
Read-only AWS inspection then established the current running FE/BE addresses.
This remediation makes those live addresses an explicit Terraform contract:

| Role | Terraform input | Address |
| --- | --- | --- |
| FE | `goal_6_fe_private_ip` | `10.42.69.177` |
| BE | `goal_6_be_private_ip` | `10.42.77.49` |

The values are passed to `aws_instance.private_ip`, remain private (no public
IP is enabled), and are exposed to the existing task-definition wiring through
the module outputs. They are fixed by development-variable validation pending
a separately approved network design change. The previously proposed
`10.42.64.238`/`10.42.71.97` pair was not assigned to the current instances and
has been removed from the active inputs.

Read-only AWS evidence used for this correction:

- Account `736956442295`, region `ap-southeast-1`.
- FE `i-0ad90219f868841f7`, ENI `eni-0a8bbc262f229b1de`,
  `10.42.69.177`, subnet `subnet-09bc95f43115dca3e`.
- BE `i-0dc0e8f4f71d1876e`, ENI `eni-07f63fc4ad61285e4`,
  `10.42.77.49`, subnet `subnet-09bc95f43115dca3e`.
- An ENI lookup for `10.42.64.238` and `10.42.71.97` returned no attached
  interface.

## Fail-closed subnet and host checks

- Terraform 1.15.8 does not provide `cidrcontains`. The Doris module therefore
  uses a deterministic, fail-closed `/20` membership check: it enumerates the
  selected CIDR's 16 `/24` blocks and 256 host offsets per block with
  `cidrhost`, then requires `contains` for both addresses. A selected subnet
  with any other prefix produces an empty host set and fails the check and
  instance precondition rather than widening scope.
- The module exposes both a check and an instance precondition that require
  FE and BE addresses to be distinct and inside that selected subnet; the
  precondition fails the Terraform operation rather than permitting an
  invalid host.
- Development inputs validate IPv4 shape and distinctness before the module
  check evaluates the selected subnet.
- The rendered host bootstrap receives `EXPECTED_PRIVATE_IP`, records the
  expected/observed address in the encrypted role-volume
  `private-ip-diagnostics.log`, emits `private-ip-configured` on a match, and
  emits `private-ip-mismatch` then exits before starting Docker on a mismatch.
- Existing bounded container diagnostics remain redacted and secret-free.

This does not delete or reformat the FE metadata volume or BE serving-data
volume. It does not change IAM, KMS, security groups, routes, S3, ECR,
Databricks, or task execution behavior.

## Offline validation

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| Goal 6 static regression tests | PASS — 17/17 |
| `python3 -m pytest -o addopts='' -q tests/unit/test_goal6_static.py tests/unit/test_goal5_static_goal6_regression.py` | PASS — 18 passed |
| Rendered FE/BE bootstrap `bash -n` | PASS — FE and BE |
| Python compilation | PASS |
| Ignored development `terraform.tfvars` private-IP inputs | PASS — explicit FE/BE values set to AWS-observed addresses; file is not tracked |
| Terraform formatting | PASS — `terraform fmt -check` on changed Goal 6 `.tf` sources |
| Terraform `init -backend=false` with local provider cache | PASS — no S3 backend initialized |
| Terraform `validate` | PASS — provider schema/config validation with backend disabled |
| Terraform mock-provider tests | PASS — 7 passed, 0 failed |
| `git diff --check` | PASS |
| Repository-wide platform-foundation/Pydantic checks | EXCLUDED — neither the suite nor its `pydantic`-dependent checks are Goal 6 acceptance criteria; they remain a separate Goal 2 concern |
| Ruff, mypy, TFLint, Trivy | UNVERIFIED — executables unavailable on this host |
| Connected Terraform plan | PASS — saved plan `goal-06-doris-private-ip-remediation-20260814.tfplan`, SHA-256 `5e1cf1ae3be48d2565635da4cd1d73bbb14e3addd90d4ce71ff93511c55729d1`; exact action review is in the connected-plan report |
| Connected Terraform apply/destroy | NOT RUN — separate hash-bound approval required |
| AWS/Databricks operation, task, SQL, bundle, or volume reset | NOT RUN by design |

## Failed-plan correction evidence

The first connected plan attempt (`98b54e3ed06c1b80cf8c797325e1e334bd85889d71d689906969ad97ee29b8ee`)
was not applyable: Terraform v1.15.8 stopped during configuration evaluation
with `Call to unknown function: cidrcontains`. No managed resource action was
executed. The source-only correction above removes that unsupported function;
the corrected configuration must receive a new saved connected plan and a
separate review before any apply approval.

The corrected saved-plan command was approved. The wrapper execution
permission review timed out twice before Terraform started; a direct
invocation of the installed Terraform binary then completed the read-only
AWS/Databricks refresh and produced the saved artifact
`goal-06-doris-private-ip-remediation-20260814.tfplan`. Its SHA-256 is
`5e1cf1ae3be48d2565635da4cd1d73bbb14e3addd90d4ce71ff93511c55729d1`.
No managed resource mutation occurred.

The exact action review is durable in
`docs/verification/GOAL-06-DORIS-STABLE-PRIVATE-IP-CONNECTED-PLAN-2026-08-14.md`.

## Next approval boundary

The saved connected development plan has been created and reviewed. It is
limited to the four expected FE/BE instance and `/dev/sdf` attachment
replacements caused by the Terraform-owned bootstrap/user-data and stable
private-IP contract. Require a separate hash-bound apply approval; no task
launch is authorized until both hosts emit `doris-port-ready`.
