# Project status

This file is a checkpoint index, not evidence by assertion. `VERIFIED` is
allowed only when the row identifies the exact reviewed commit and durable
verification evidence. A plan or implementation commit alone is not
verification.

## Current snapshot

- Reconstruction baseline reviewed: `ec025e18666daac5c1979a2aad6f34a141c2351d`
- Current Goal 3B connected-execution evidence:
  `docs/verification/GOAL-03B-CONNECTED-EXECUTION-2026-08-05.md`. Its
  Terraform remediation and report are currently uncommitted and therefore
  are not immutable verification provenance.
- Reconstruction date: `2026-08-05`
- Last repository-wide executable verification: `VERIFIED BY PROJECT OWNER`
- Verification provenance: the project owner confirmed on `2026-08-05` that
  the Goal 2 and Goal 3A acceptance checks passed on the previous development
  machine and that the GitHub Actions failures were corrected. Raw historical
  logs are not committed in this repository.
- Current pre-3B offline verification:
  `docs/verification/GOAL-03-PRE-3B-READINESS-2026-08-05.md`
- Final Goal 3B offline blocker review: `2026-08-10`; all commit-candidate
  validation gates passed without an AWS operation.

| Checkpoint | Status | Implementation evidence | Verification evidence |
| --- | --- | --- | --- |
| Goal 1 — Architecture contract | VERIFIED | `f89fa1f5552b774f1c2a5e4472b0b8a7e12efa9a`; reviewed through `ec025e18666daac5c1979a2aad6f34a141c2351d` | Static consistency review of the governance documents and all accepted ADRs, recorded by this status snapshot. ADR-006 has a Markdown completeness defect but its accepted decision is unambiguous. |
| Goal 2 — Repository and development foundation | VERIFIED | `f89fa1f5552b774f1c2a5e4472b0b8a7e12efa9a`, `2881e23ece07f790e4fadf477580fb75ab5639b4`, `f5e3e8345ce7e96a751697fed212c90c18775d63`; source snapshot reviewed through `ec025e18666daac5c1979a2aad6f34a141c2351d` | Project-owner attestation dated `2026-08-05`: Goal 2 acceptance checks passed on the previous development machine. Raw test, coverage, local-service, lint, type-check, and security reports were not retained in the repository. |
| Goal 3A — AWS Terraform implementation and offline validation | PARTIALLY VERIFIED — all current offline gates pass; durable commit pending | `a70d806da9b7df6d9218537062bf8670c817b662` plus CI fixes `9cc3104`, `fdca7c8`, and `2a9abfe`; the uncommitted Goal 3B change set extends the foundation with isolated synthetic validation resources and the accepted base-alarm remediation. | On `2026-08-10`, Terraform formatting, bootstrap/development validation, 9 Terraform contract runs, TFLint, Trivy, strict preflight, Ruff, mypy, 15 pytest tests with 96.67% coverage, Bandit, detect-secrets, environment validation, dependency audit, pre-commit file-integrity hooks, and `git diff --check` passed. Terraform/Ruff/mypy/detect-secrets/pytest hooks were validated directly rather than duplicated inside pre-commit. |
| Goal 3B — Connected AWS deployment and smoke testing | PARTIALLY VERIFIED — connected and offline acceptance passed; durable commit pending | Bootstrap, development, VPC Flow Logs, static smoke-task foundations, dedicated NAT fallback, Redis revision 4, and the base RDS CPU alarm remediation were applied from separately approved saved plans. Alarm plan SHA-256 `db143549fe551a397afac6b88248b8be74b48b689fa8a685c6868af43816f331` applied as `1 added, 1 changed, 0 destroyed`. | `docs/verification/GOAL-03B-CONNECTED-EXECUTION-2026-08-05.md` records all three passing dynamic smoke checks, deterministic connected SG/AOSS unauthorized-path enforcement, VPC Flow Log ingestion, successful alarm apply, read-only CloudWatch/KMS verification, and final post-remediation zero-drift plan SHA-256 `db9ec9f069bf03d724689d1cf2a3347a43dd63c18df81f99463f18bf649d78be` exiting `0` with zero non-no-op resource/output changes. Current source and evidence are uncommitted, so the freshness rule prevents a `VERIFIED` label. |
| Goal 4 — Databricks, Unity Catalog, and Iceberg | PLANNED — NOT STARTED | `docs/ROADMAP.md` and placeholder `databricks/README.md` | No implementation or verification evidence. |

## Current next checkpoint

Obtain explicit approval to commit the reviewed Goal 3B source, tests,
documentation, and verification evidence as an isolated durable checkpoint.
After that immutable SHA exists, promote Goal 3A/3B to `VERIFIED` in a separate
status-only commit that references it. Do not begin Goal 4, apply, destroy, run
another task, launch an arbitrary ECS task, or reuse the smoke roles for a
service.

## Freshness rules

- A commit that changes files owned by a checkpoint invalidates that
  checkpoint's `VERIFIED` status until its required checks are rerun.
- Update this file in the same reviewed change that adds the durable
  verification report or links to an immutable CI result.
- Never infer `VERIFIED` from a commit message, roadmap label, plan, or the
  existence of test configuration.
- When raw verification reports are unavailable, record the project owner's
  explicit attestation, its date, and the exact source commit it covers.
- If the evidence cannot be reconstructed, use `UNVERIFIED` and state what is
  missing.
- Durable evidence must be committed before Goal 3A/3B is restored to
  `VERIFIED`.
