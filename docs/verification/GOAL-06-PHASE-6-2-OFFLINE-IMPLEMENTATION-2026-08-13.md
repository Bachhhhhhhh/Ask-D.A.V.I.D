# Goal 6 Phase 6-2 — offline implementation evidence

Date: `2026-08-13`
Scope: repository source, tests, documentation, and local offline validation only
Cloud mutation: **none**

## Implemented source boundary

The repository now contains disabled-by-default Goal 6 configuration only:

- one private `m7i.xlarge` FE and one private `m7i.xlarge` BE, with IMDSv2,
  no public IP, encrypted gp3 data volumes (20 GiB FE / 50 GiB BE), dedicated
  security groups, TLS-enabled FE configuration, and CloudWatch-agent log
  collection from the encrypted host-mounted Doris log paths;
- a private immutable ECR verifier image definition plus separate one-off ECS
  Fargate admin and read-only verifier task definitions, roles, and security
  groups;
- exact KMS-encrypted Secrets Manager containers and sensitive secret versions;
  no literal secret, token, password, or static AWS key is committed;
- a Databricks external-read service principal, bounded OAuth secret lifetime,
  and an extension of the existing authoritative Unity Catalog grants resource:
  `USE CATALOG`, `USE SCHEMA` + `EXTERNAL USE SCHEMA` only on
  `green_sm_business`, and `SELECT` only on
  `goal5_structured_business_metrics`;
- a short-lived Unity Catalog Iceberg REST/vended-credential catalog contract
  for controlled refresh into internal, disposable Doris objects only, plus a
  deterministic migration manifest, one-replica serving DDL, a bounded
  read-only workload group, Doris audit logging, refresh-state recording, and
  a separately approved internal-only rebuild runner;
- one Terraform-managed SSE-KMS neutral increment and a Serverless SQL bundle
  that demonstrates its governed Raw -> Curated -> Business path.

`goal_6_enabled` remains `false` by default. No AMI, image digest, subnet, or
secret value was placed in Git. No resource is created merely by this source.
The separate `goal_6_verifier_tasks_enabled` gate also remains `false`: the
foundation plan creates its private ECR repository without task definitions,
then a separately approved image push and second saved plan supply the final
immutable verifier image digest.

## Passed offline evidence

| Command | Result |
| --- | --- |
| `terraform fmt -check -recursive infrastructure` (Terraform `1.15.8`) | PASS |
| `terraform -chdir=infrastructure/environments/development init -backend=false` using a temporary local cache | PASS; no remote backend initialized |
| `terraform -chdir=infrastructure/environments/development validate` | PASS |
| `terraform -chdir=infrastructure/environments/development test -test-directory=tests` | PASS — 7 passed, 0 failed |
| `terraform providers schema -json` local inspection | PASS — confirms `databricks_service_principal_secret` has `service_principal_id`, `lifetime`, `secret`, and `provider_config` |
| `python3 scripts/validate_goal4.py` | PASS |
| `PYTHONPATH=packages/ingestion-framework/src python3 scripts/validate_goal5.py` | PASS — including the shared-bundle Goal 6 regression guard |
| `python3 scripts/validate_goal6.py` | PASS |
| Ruff `format --check` and `check` across `packages`, `scripts`, and `tests` | PASS — 29 files formatted; no lint findings |
| focused pytest, no cache/coverage plugin: Goal 4/5/6 static suites | PASS — 50 passed |
| full pytest with the checked-in markers, branch coverage, and XML written under `/tmp` | PASS — 134 passed, 97.16% coverage (minimum 90%) |
| Mypy across the checked-in configured source set with temporary cache | PASS — no issues in 13 source files |
| Bandit on `packages` and `scripts` | PASS |
| `detect-secrets-hook --baseline .secrets.baseline` | PASS |
| `sh -n` for admin-refresh, readonly-verifier, and rebuild runner | PASS |
| `python3 -m py_compile scripts/validate_goal6.py tests/unit/test_goal6_static.py` | PASS |
| `git diff --check` | PASS |
| focused credential/key-pattern source scan | PASS — no literal AWS key, Databricks PAT, or private key found |
| local Docker build and image inspection | PASS — `ask-david/doris-verifier:goal6-offline`, non-root user `65532:65532`; no ECR push |
| TFLint `0.60.0`, recursive source lint | PASS — after adding provider bounds and removing unused verifier inputs |
| Trivy `0.69.3` `config --severity HIGH,CRITICAL --exit-code 1 infrastructure` | PASS — 0 misconfigurations |

Terraform initialization used `-backend=false` and a `TF_DATA_DIR` under
`/tmp`; it did not initialize the S3 backend, authenticate to AWS, or execute a
plan. Provider schema inspection used the local provider cache only.

## Validation notes and remaining unverified checks

The local quality gates relevant to the Goal 6 source are complete. The
following checks remain **UNVERIFIED**, not failed:

- direct `uv run pre-commit run --all-files`: the checked-in local virtual
  environment points to an unavailable `/workspace/.venv` interpreter and no
  trusted `uv` executable is available on this host. Its constituent formatter,
  Ruff, mypy, detect-secrets, Terraform-format, and pytest gates were run
  directly and passed as listed above.
- locked dependency audit: attempted temporary installation of `uv` stopped on
  a hash mismatch before execution. The mismatch was not bypassed. No claim is
  made for `pip-audit` against the project lockfile.
- any Databricks bundle validation/deployment, SQL execution, service-principal
  creation, Unity Catalog grant, OAuth request, AWS plan/apply, ECR push, EC2,
  ECS task, Secrets Manager, KMS, S3, or Doris operation.

## Current stop condition

This is not a Goal 6 verification claim. Review the resulting repository diff
and the two explicitly unverified tool-orchestration/audit checks, then request
a separate approval for exactly one saved connected development plan. Do not
use this implementation checkpoint as permission to plan, apply, push an
image, deploy a bundle, or run SQL/tasks.
