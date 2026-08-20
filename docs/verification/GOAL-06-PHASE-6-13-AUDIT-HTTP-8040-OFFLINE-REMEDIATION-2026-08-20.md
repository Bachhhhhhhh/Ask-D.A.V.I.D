# Goal 6 Phase 6-13 AuditLoader HTTP/8040 — offline remediation

Date: `2026-08-20`

Status: **PASS — OFFLINE VALIDATED; NO CONNECTED PLAN/APPLY OR RETRY**

## Connected evidence that identified the blocker

The owner-provided read-only inspection of the current FE established:

| Check | Result |
| --- | --- |
| FE bootstrap marker | PASS — `doris-port-ready` on `9030`; diagnostics listener state `ready` |
| `enable_audit_plugin` | `true` |
| Built-in `AuditLoader` | `INSTALLED` |
| Built-in `AuditLogBuilder` | `INSTALLED` |
| `audit_log` row count | `0` |
| `audit_log` replication | `replication_allocation = "tag.location.default: 1"` |
| `audit_log` replica health | All returned replicas `NORMAL` / `OK` |
| FE log | `AuditStreamLoader.loadBatch` raised `java.net.SocketTimeoutException: Connect timed out` |

The exact result-contract query was successful, but its query ID was absent
from `audit_log`. The failure is therefore in the audit batch delivery path,
not in FE query-port readiness, plugin installation, audit-table readability,
or table replica health.

## Root-cause determination

Doris AuditLoader sends an HTTP stream-load request through FE and follows the
FE redirect to the selected BE HTTP webserver. The selected Doris configuration
uses BE `webserver_port = 8040`. The current Terraform FE-to-BE rule set had
only `9050`, `9060`, and `8060`; it did not authorize FE-to-BE TCP `8040`.

This is consistent with the observed `AuditStreamLoader` connect timeout and
with the source-managed private network contract. The existing rules are
security-group-to-security-group only; no CIDR or public exposure is added.

## Minimal declarative remediation

The offline source change adds `8040` to the existing paired
`fe_to_be` ingress/egress rule set. It does not add a new security group,
change instance/user-data/EBS/IAM/KMS/ECS resources, or broaden any verifier
path. The resulting rule set is:

- FE egress → BE TCP `8040`, `9050`, `9060`, `8060`;
- BE ingress from FE TCP `8040`, `9050`, `9060`, `8060`.

No connected Terraform plan, apply, ECS task, SQL retry, or AWS mutation was
performed as part of this offline remediation.

## Offline validation contract

The offline checks produced the following results:

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| Focused Goal 6 static regression tests (`pytest -q -o addopts='' ...`) | PASS — `46 passed` |
| `git diff --check` | PASS |
| `terraform fmt -check -diff infrastructure/modules/doris-serving/main.tf infrastructure/modules/doris-serving/tests/doris_serving.tftest.hcl` | PASS |
| `terraform test` in `infrastructure/modules/doris-serving` | PASS — `1 passed, 0 failed` |

The first connected plan exposed six description-only updates on the existing
rules, so the source was corrected to preserve their descriptions. Offline
validation was rerun. The replacement saved plan
`goal-06-audit-http-8040-20260820-r2.tfplan` has SHA-256
`2af16e7950852755d85e23fcdda5009673d7e39dddd0db5903a52d855bdbe661` and
contains exactly two development-only SG-to-SG creates:

- FE egress → BE TCP `8040`;
- BE ingress ← FE TCP `8040`.

It reports `2 to add, 0 to change, 0 to destroy`; no replacement, public,
production, EC2, EBS, IAM, KMS, ECS, Databricks, or unrelated action is present.
The plan has not been applied and remains pending separate hash-bound approval.

Phase 6-13 remains **UNVERIFIED** until a fresh approved audit execution
produces the exact query-ID evidence contract.
