# Goal 7 connected-plan blocker remediation — 2026-08-21

## Status

**OFFLINE REMEDIATION IMPLEMENTED — NEW CONNECTED PLAN NOT CREATED**

This checkpoint fixes only planability defects discovered by the failed
connected plan. It does not retry Terraform connected planning, apply/destroy
resources, run ECS tasks, create an AOSS index, or call Databricks SQL.

## Remediations

### Goal 6 subnet metadata isolation

The Doris module previously resolved the selected subnet through a module-local
`data.aws_subnet` while the module had dependency edges on secret versions.
Adding the Goal 7 workflow secret caused that data source to be deferred until
apply, making the four protected EBS volume availability zones unknown and
producing false replacements.

The selected subnet's CIDR and availability zone are now read by a root-level
data source and passed as explicit module inputs. The module no longer owns a
deferred subnet data source. Existing `goal_6_rebuild_serving_state=true`,
volume IDs, `prevent_destroy`, attachments, and rebuild semantics are
unchanged.

### Goal 7 IAM policy count

The Goal 7 task-execution policy previously used
`count = length(var.goal7_secret_arns) > 0 ? 1 : 0`. Secret ARNs are resource
outputs and were unknown during plan. The count now uses the explicit,
plan-known task gate `goal7_secrets_enabled`; the policy still receives only
the exact workflow-OAuth and Doris query secret ARNs required by the enabled
tasks.

Offline test fixtures explicitly disable Goal 6/7 gates so ignored local
tfvars cannot contaminate mock-provider tests.

## Offline evidence

| Check | Result |
| --- | --- |
| Infrastructure preflight | PASS |
| Terraform configuration validation | PASS |
| Terraform mock-provider tests | PASS — 7 passed, 0 failed |
| Goal 7 static validator | PASS |
| Ruff | PASS |
| Focused Goal 7 tests | PASS — 13 tests |
| Terraform format / diff check | PASS |
| Connected retry | NOT RUN — requires separate approval |

## Next boundary

The separately approved retry created and reviewed a new saved connected
development plan. It shows zero Goal 6 EBS replacement/destroy actions, zero
unexpected replacement/destroy/public/production changes, and only the exact
Goal 7 task-boundary resources. Its durable evidence is
`docs/verification/GOAL-07-CONNECTED-PLAN-2026-08-21.md`.

The next boundary is separate hash-bound approval to apply that exact plan.
If the artifact hash or action set differs, stop. Do not run an ECS task,
create an AOSS index, or execute Databricks SQL before apply and post-apply
read-only inspection are complete.

The durable implementation plan now records these safeguards in
`docs/plans/GOAL-07-INTEGRATED-AI-DEMO-PLAN.md`, and the checkpoint index in
`docs/PROJECT_STATUS.md` records that no connected retry has occurred.
