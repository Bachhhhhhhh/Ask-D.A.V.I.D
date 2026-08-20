# Goal 6 Phase 6-5 reconciliation offline implementation

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: declarative Terraform import configuration and offline validation only

## Objective

The approved foundation apply left the FE instance and both data-volume
attachments outside Terraform state. This remediation introduces exactly three
configuration-driven imports, all gated by `goal_6_enabled`:

| Destination address | Existing AWS identity |
| --- | --- |
| `module.doris_serving.aws_instance.fe[0]` | `i-074e456efa350b444` |
| `module.doris_serving.aws_volume_attachment.fe[0]` | `/dev/sdf:vol-012bc3410278ed85e:i-074e456efa350b444` |
| `module.doris_serving.aws_volume_attachment.be[0]` | `/dev/sdf:vol-01e9b0ed05f7b92b9:i-05b409f7992294844` |

The configuration has no import for an already state-owned volume or BE
instance. It does not modify topology, AWS permissions, networking, or
Databricks configuration. It does not run `terraform import`; Terraform will
show the imports in a normal saved plan for review before any state change.

## Validation boundary

| Check | Result |
| --- | --- |
| Terraform fmt, `init -backend=false`, validate, and tests | PASS — 7 Terraform tests passed |
| Goal 4/5/6 static validators | PASS |
| Python tests and coverage | PASS — 136 tests; 97.16% coverage |
| Ruff and mypy | PASS |
| Bandit and detect-secrets | PASS |
| TFLint and Trivy | PASS |
| Whitespace check | PASS |

Terraform's mock-provider tests explicitly set `goal_6_enabled=false` because
Terraform test cannot execute import requests against a mock provider. The
three import blocks themselves are parsed by Terraform validation and covered
by static regression checks. No connected plan, apply, import, cleanup, ECR
push, bundle deployment, SQL/job run, or AWS/Databricks operation occurred in
this offline remediation.

## Connected-plan outcome

The separately approved connected reconciliation plan was subsequently
generated. Its ignored local artifact has SHA-256
`318a8b1d8b7693d002e8019c3db82fdca2ee7abe93473112a0e20f056da54481`.
Terraform decoded 245 `no-op` resource changes and zero imports, create,
update, replace, or destroy actions. Read-only remote-state inspection showed
all three planned import destinations already state-owned with the expected
resource identities. Therefore no reconciliation apply was requested or run.

This establishes only state ownership. It does not supersede the separate
host-bootstrap health blocker documented in
`GOAL-06-PHASE-6-5-PARTIAL-APPLY-2026-08-13.md`.

## Superseded next checkpoint

The state-reconciliation plan is complete and is a no-op. A different,
explicitly approved bootstrap-remediation design is now required before any
further connected plan or apply.
