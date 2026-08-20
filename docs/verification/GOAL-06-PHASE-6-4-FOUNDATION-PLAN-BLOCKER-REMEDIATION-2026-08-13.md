# Goal 6 Phase 6-4 foundation-plan blocker remediation

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: offline source, test, documentation, and ignored-local-input remediation only

## Triggering evidence

The approved saved foundation-plan attempt was read-only and stopped before
approval or apply. Its Terraform output proposed three unintended deletes of
the already verified Goal 5 S3 source objects because the ignored local input
`goal_5_source_objects_enabled` was absent. Terraform then stopped with an
invalid `count` argument for the `databricks_grants.doris_source_table` grant:
the cardinality depended on the application ID of a service principal being
created in the same plan.

No resource was applied, replaced, destroyed, or otherwise mutated during that
attempt. The resulting saved-plan artifact is not valid for approval or use.

## Remediation

- Set `goal_5_source_objects_enabled = true` in the ignored development tfvars
  so the three verified Goal 5 source objects remain managed and retained.
- Add `doris_external_read_enabled`, a known Boolean module input driven by the
  existing `goal_6_enabled` development gate.
- Use that known Boolean for every optional Doris Unity Catalog grant and
  resource count. The service-principal application ID remains only the value
  of a resource field, where Terraform may resolve it during apply.
- Add static validator and regression-test assertions that reject future
  use of an unknown application ID to decide resource cardinality.

This does not change the reviewed intended scope: the first Goal 6 foundation
plan remains task-definition-free, creates no public exposure, and requires a
fresh saved connected plan plus separate explicit approval before any apply.

## Offline validation

The remediation requires the repository's Terraform, static, test, lint, type,
and security validation sequence to pass before a new connected plan is
requested. Results are recorded below after execution.

| Check | Result |
| --- | --- |
| Terraform formatting, `init -backend=false`, validation, and tests | PASS — 7 Terraform tests passed |
| Goal 4/5/6 static validators | PASS |
| Python tests and coverage | PASS — 134 tests; 97.16% coverage |
| Ruff and mypy | PASS |
| Bandit and detect-secrets | PASS — no detected repository secrets after excluding ignored state/cache artifacts |
| TFLint | PASS |
| Trivy | PASS — source scan excluding ignored local saved-plan artifacts and direct Doris-module scan both passed. The reviewed inline `AVD-AWS-0104` annotations are scoped only to the two private TCP/443 NAT-egress rules; static tests prevent scope expansion. |
| Whitespace check | PASS |

## Next checkpoint

Do not reuse the failed saved plan. The approved private-NAT HTTPS-egress
exception is resource-scoped and does not authorize any network change. After
the full offline validation passes, request separate approval to create and
review one fresh connected development foundation plan. The plan must retain
the Goal 5 source objects and must stop for review if it proposes any destroy,
replacement, public exposure, production change, task definition, or scope
outside the reviewed foundation.
