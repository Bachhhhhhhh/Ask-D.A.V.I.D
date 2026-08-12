# Goal 4 bootstrap IAM self-assumption remediation

## Result

**PASS — declarative remediation and offline validation only.**

Goal 4 remains not verified. This report does not authorize or claim a new
connected plan, Terraform apply, AWS or Databricks mutation, storage-credential
validation, bundle deployment, or SQL execution.

## Subsequent execution

This report is the immutable record of the `2026-08-10` offline checkpoint,
not the current stopping condition. The initial-role and trust-policy plans
were subsequently applied successfully under separate approvals. The first
credential validation then failed only `PATH_EXISTS`. Current evidence and the
next approval boundary are recorded in
`GOAL-04-STORAGE-CREDENTIAL-PATH-EXISTS-REMEDIATION-2026-08-11.md`.

## Incident and partial state

The approved bootstrap saved plan had SHA-256
`d7ee6ac5e85b2d067210798dc1e9462d21747c505befeb5e26a6352c9d4bd735`.
Its apply created the Terraform-owned Databricks storage credential
`ask-david-development-managed-iceberg`, then AWS rejected IAM role creation
with `MalformedPolicyDocument: Invalid principal`. The trust document named
the deterministic storage-role ARN before that role existed.

Read-only post-failure inspection established:

- the storage credential exists in Terraform state and Databricks;
- the Goal 4 IAM storage role does not exist;
- the inline storage policy was not created;
- the storage KMS policy update was not applied;
- no catalog, schema, external location, identity, grant, binding, bundle,
  SQL table, workflow, warehouse, or cluster was created.

The failed saved plan is stale after the partial apply and must never be
reused. Its hash is retained only as forensic evidence.

## Approved two-step remediation

The implementation enforces all seven approved conditions:

1. `goal_4_storage_role_self_assumption_enabled` exists as a bootstrap
   sub-step flag and defaults to `false` in both the root and storage module.
2. With the flag false, the initial-role trust contains only the Databricks
   Unity Catalog principal and exact storage-credential external ID. The next
   reviewed plan may create only the missing IAM role, inline policy, and
   in-place KMS policy update; the existing credential must be a no-op.
3. Only after that apply succeeds may the ignored development tfvars set the
   flag to `true` while retaining `goal_4_stage = "bootstrap"`.
4. A new saved plan must then contain only an in-place IAM trust-policy update
   adding the role's own ARN.
5. That exact saved plan requires a separate apply approval.
6. Storage-credential validation is forbidden until the trust-policy-only
   apply succeeds.
7. Cross-variable Terraform validation and the offline infrastructure
   preflight both hard-fail `goal_4_stage = "active"` unless self-assumption is
   enabled.

The inline role policy may grant `sts:AssumeRole` on the role from the initial
step, but the trust relationship does not permit self-assumption until the
second reviewed apply. No direct user or service-principal S3 permission was
added.

## Files changed by the remediation

- `infrastructure/modules/databricks-aws-storage/main.tf`
- `infrastructure/modules/databricks-aws-storage/variables.tf`
- `infrastructure/modules/databricks-aws-storage/outputs.tf`
- `infrastructure/environments/development/goal4.tf`
- `infrastructure/environments/development/goal4_variables.tf`
- `infrastructure/environments/development/outputs.tf`
- `infrastructure/environments/development/terraform.tfvars.example`
- `infrastructure/environments/development/tests/development.tftest.hcl`
- `infrastructure/environments/development/tests/goal4.tftest.hcl`
- `scripts/dev.py`
- `scripts/validate_goal4.py`
- `tests/unit/test_goal4_static.py`
- `tests/unit/test_infrastructure_preflight.py`
- Goal 4 plan, runbook, infrastructure/security/status documentation, and this
  verification report.

## Offline validation evidence

No command below initialized a connected backend, created a real Terraform
plan, applied infrastructure, authenticated to a cloud, deployed a bundle, or
ran SQL.

| Check | Result |
| --- | --- |
| Terraform recursive format check | PASS |
| bootstrap Terraform validate | PASS |
| development Terraform validate | PASS |
| Terraform mock-provider contracts | PASS — 6 passed, 0 failed |
| self-assumption default-off regression | PASS |
| explicit self-trust bootstrap regression | PASS |
| active-stage hard-rejection regression | PASS |
| TFLint recursive scan | PASS — zero findings |
| Trivy HIGH/CRITICAL IaC scan | PASS — zero findings, embedded offline checks |
| Goal 4 static contract validator | PASS |
| Ruff format and lint | PASS — 61 files formatted, zero lint findings |
| strict mypy | PASS — 5 source files |
| pytest with branch coverage | PASS — 24 passed, 96.67% coverage |
| Bandit | PASS |
| detect-secrets baseline check | PASS |
| environment configuration validation | PASS |
| strict ignored-input infrastructure preflight | PASS |
| YAML parsing | PASS — 10 candidate files |
| local Databricks bundle-schema generation | PASS |
| `git diff --check` | PASS |
| accepted ADR diff | PASS — no accepted ADR modified |

The session's checked-in virtual-environment launchers and existing tool caches
were owned by a different environment path/UID. Python tools were therefore
invoked with the same installed site packages through `/usr/bin/python3`, and
Ruff/Mypy/Terraform caches were isolated under `/tmp`. Terraform and TFLint
provider/worker processes required execution outside the filesystem sandbox;
they still ran strictly offline with existing binaries and mock providers.
Initial tooling-path failures are not represented as source-test failures.

`pip-audit` was not repeated because this approval allowed offline validation
only and vulnerability-database refresh is connected. No dependency or lock
version changed in this remediation; the preceding Phase 4-2 report records
the last passing dependency audit.

## Scope and security review

- Unity Catalog remains the primary governance authority.
- S3 plus managed Apache Iceberg remain the intended system of record.
- No metastore, assignment, classic cluster, SQL warehouse, Glue catalog,
  Doris, OpenSearch retrieval, Goal 5 ingestion, agents, or real Green SM data
  was introduced.
- The KMS/S3 permission scope and seven approved managed roots are unchanged.
- Accepted ADRs were not modified.
- Ignored local tfvars/backend files, Terraform state, saved plans, OAuth
  material, external IDs, and credentials are not tracked by Git.

## Historical stopping condition

Stop before all connected activity. The next permissible checkpoint requires
explicit approval to create a new saved connected development **initial-role
plan** with the self-assumption flag false. Expected managed-resource actions
are exactly two creates (IAM role and inline policy), one in-place storage KMS
policy update, and no-op for the existing storage credential. Any replacement,
destroy, namespace, identity, compute, bundle, SQL, production, or other action
must stop for review.
