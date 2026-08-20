# Goal 6 Phase 6-5 root-bootstrap remediation — offline evidence

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: Terraform source, static tests, documentation, and offline validation only

## Trigger and evidence

The approved Goal 6 foundation apply created the intended private EC2
foundation but stopped before a healthy Doris cluster existed. Read-only EC2
console evidence showed that the BE Docker image unpack failed on the AMI root
filesystem:

```text
failed to register layer ... no space left on device
```

Both encrypted `gp3` root volumes were 8 GiB. The separate 20 GiB FE metadata
and 50 GiB BE serving-data EBS volumes are healthy and are not Docker's root
filesystem. The state-reconciliation plan subsequently proved a complete no-op:
all three previously missing resource addresses are now Terraform state-owned.
Its SHA-256 is
`318a8b1d8b7693d002e8019c3db82fdca2ee7abe93473112a0e20f056da54481`.

## Declarative remediation

The repository now declares the following, with no connected action taken:

| Concern | Declarative control |
| --- | --- |
| Root storage capacity | FE and BE each declare a 30 GiB encrypted `gp3` root block device. |
| Failed BE first boot | A BE-only `goal_6_be_bootstrap_generation = 2` marker is appended to rendered user data. |
| Controlled retry semantics | `user_data_replace_on_change = true` exists only on the BE. The changed generation intentionally makes the BE replacement explicit in the future saved plan so cloud-init runs again. |
| Serving-state preservation | The separate 50 GiB BE EBS serving-data volume remains an `aws_ebs_volume` plus attachment; its size, KMS key, network, IAM, source allowlist, and topology are unchanged by this remediation. |
| FE behavior | The future plan must disclose the provider's exact behavior. The source does not assert that the FE 8 → 30 GiB root-volume expansion will be in-place. |

The exact connected plan is deliberately not inferred here. In particular, the
next reviewed plan must show all create/update/replace/destroy/attachment
actions and must not be applied unless separately approved.

## Offline validation evidence

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| `terraform fmt -check -recursive infrastructure` | PASS |
| Isolated `terraform init -backend=false`, validate | PASS |
| `terraform test -test-directory=tests` | PASS — 7 passed, 0 failed |
| `pytest` project default suite | PASS — 137 passed; 97.16% coverage (XML written only to `/tmp`) |
| Ruff | PASS |
| mypy, edited Goal 6 validator/tests | PASS — 2 source files, no issues |
| Bandit | PASS |
| detect-secrets scan | PASS — no findings emitted |
| TFLint, edited `doris-serving` module | PASS |
| Trivy, infrastructure and `doris-serving` module | PASS — 0 HIGH/CRITICAL findings |
| `git diff --check` | PASS |

The existing checked-in `.venv` is stale (`/workspace/.venv/bin/python3` does
not exist), so validation used the already-existing temporary Goal 6 validation
environment and placed generated coverage/cache/secret-scan artifacts only
under `/tmp`. Pytest emitted one non-failing warning because the existing
worktree `.pytest_cache` is not writable.

Repository-wide `mypy packages scripts tests` is **UNVERIFIED for this
checkpoint**: its temporary environment reports 61 diagnostics in existing
Goal 5 adapter and platform-settings tests. The edited Goal 6 validator and
test type-check cleanly; no unrelated typing source was changed to mask those
diagnostics. This does not authorize a connected plan until the remediation
review accepts the stated limitation.

## Explicit non-actions

This checkpoint did not run a connected Terraform plan/apply/destroy/import,
AWS mutation, Databricks mutation, ECR push, ECS task launch, bundle deployment,
SQL/job run, or source-data mutation. No secret value was retrieved or written.

## Next approval boundary

After review, request approval to reverify account/region/workspace read-only
and create exactly one saved development Terraform plan for this remediation.
The plan must stop for review if it has any unexpected action, public exposure,
production action, Databricks action, source-data action, IAM/KMS/network scope
change, or a replacement other than the explicitly designed BE recovery.
