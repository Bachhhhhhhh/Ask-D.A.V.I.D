# Goal 6 rebuild/audit admin-operation wrapper — offline implementation

Date: `2026-08-18`

Status: `OFFLINE VALIDATED — NO TASK RUN`

## Purpose and privilege boundary

`infrastructure/scripts/run-goal6-admin-operation.sh` provides the guarded
private execution path for exactly two later operations that cannot use the
query-only verifier task definition:

| Operation | Fixed command | Scope |
| --- | --- | --- |
| `rebuild` | `/app/doris-rebuild-serving` | Drop only the version-controlled internal disposable Doris database objects |
| `audit` | `/app/doris-audit-verify` | Read the internal Doris audit log for one exact prior query ID |

Admin refresh remains in its existing dedicated wrapper. RBAC, query-limit,
and representative read-only verification remain in the query-only wrapper.

## Independent confirmations

- `rebuild` requires `--confirm-goal6-rebuild`, rejects the audit confirmation,
  and rejects any query-ID input;
- `audit` requires `--confirm-goal6-audit`, rejects the rebuild confirmation,
  and requires one syntactically valid expected query ID.

These switches are intentionally non-interchangeable. Neither authorizes the
other operation.

## Fail-closed controls

The wrapper binds the exact account, `ap-southeast-1`, development family,
revision, immutable image, admin/execution roles, FE/BE/workspace values,
three existing secret references, CloudWatch configuration, two private
application subnets, admin SG, and `assignPublicIp=DISABLED`. It verifies the
task definition before applying the one allowlisted command override.

For audit only, the override adds `EXPECTED_QUERY_ID`; no credential or other
environment value is overridden. The wrapper launches exactly one task, never
retries, requires exit zero and private ENI evidence, and returns only parsed
Goal 6 JSON records with a completed marker. It does not print raw logs or
retrieve secret values.

## Rebuild sequencing boundary

The rebuild command only drops the internal disposable serving objects. It
does not automatically reload them. A future connected rebuild proof requires
four separately controlled checkpoints:

1. record the expected result through the read-only wrapper;
2. obtain explicit destructive confirmation and run one rebuild task;
3. obtain separate approval and run one admin refresh to recreate/reload from
   the authoritative lakehouse source;
4. obtain separate approval and rerun the read-only verifier for equivalence.

No Unity Catalog, S3, or source table is a rebuild target.

## Offline validation

| Check | Result |
| --- | --- |
| Bash parse | PASS |
| Rebuild missing-confirmation fail closed before AWS | PASS |
| Audit missing-confirmation fail closed before AWS | PASS |
| Goal 6 static validator | PASS |
| Goal 6 plus Goal 5 regression tests | PASS — 37 tests |
| `git diff --check` | PASS |

Two non-failing pytest cache warnings reflect the existing non-writable cache
directory.

## Reviewed hashes

- admin-operation wrapper:
  `a761635b156c6f8f1f16dea60e9175f8645e7171fc3b4ecdc27b7a9c176b4f39`;
- static validator:
  `4dc6b5f864790c00cd44ee19a5a622a603f6453f5ca84ee0e4bb2aea21840ee5`;
- static tests:
  `9218e33d841a1f655c4277645e0e1ff5e1e218cb57e29fa4e758b394b93b99cd`.

The final combined focused suite contains 38 passing tests after the Phase 6-9
increment audit was added; the admin-operation wrapper itself remains
unchanged at the hash above.

This host-side wrapper is outside the verifier image aggregate and does not
change the pushed ECR digest.

## Boundary

No tfvars edit, Terraform operation, AWS/Databricks/Doris mutation, ECR push,
or ECS task occurred. The next connected boundary remains the separately
approved saved task-definition plan.
