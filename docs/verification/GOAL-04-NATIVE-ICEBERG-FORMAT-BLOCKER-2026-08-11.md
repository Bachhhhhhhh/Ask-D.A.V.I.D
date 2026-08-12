# Goal 4 Iceberg-compatible managed-table format decision

## Status

**NATIVE FORMAT NOT USED; PROJECT ICEBERG-COMPATIBILITY PROFILE ACCEPTED.**

This report corrects the earlier acceptance interpretation and records the
approved project compatibility profile. The seven existing tables
remain in place. The earlier source-only remediation was followed by the
separately approved redeployment of aggregate source SHA-256
`49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027`.
Read-only inspection confirmed that the excluded remediation directory is
absent from the workspace and that the five existing jobs remain in place.
No SQL or job was run, no Terraform operation was performed, and no AWS
resource was mutated in that deployment checkpoint. Durable evidence is in
`docs/verification/GOAL-04-BUNDLE-SYNC-EXCLUDE-VERIFICATION-2026-08-12.md`.

## Contradictory live evidence

The final read-only Unity Catalog inventory found all seven expected tables and
reported each as `MANAGED`. The raw Tables API representation also reported,
for every table:

- `data_source_format = DELTA`;
- `delta.enableIcebergCompatV2 = true`;
- `delta.universalFormat.enabledFormats = iceberg`;
- Delta protocol/history properties; and
- the capability `HAS_DELTA_AND_ICEBERG_WRITE_SUPPORT`.

Those values identify Delta Lake tables publishing Iceberg-compatible metadata
through UniForm. They do not identify native Iceberg, even though
`_iceberg/metadata` exists. The live Tables API therefore overrides the earlier
SQL-level inference from
`USING ICEBERG`, `information_schema`, successful `DESCRIBE HISTORY`, and the
successful workflow runs.

The durable effect on acceptance is:

The project owner approved the following Goal 4 acceptance profile. It records
the actual table format and accepts the governed
Iceberg-compatible S3 metadata without claiming native Iceberg or changing the
fixed architecture/ADR contract:

| Criterion | Compatibility-profile result | Reason |
| --- | --- | --- |
| 17 — managed Iceberg-compatible tables | PASS WITH DISCLOSURE | All seven are `MANAGED`; Tables API truth is Delta UniForm with Iceberg-compatible metadata. Native Iceberg is not claimed. |
| 18 — no unapproved format substitution | PASS WITH DISCLOSURE | Delta UniForm is the explicitly accepted development representation; no external or unmanaged table is present. |
| 19 — approved S3-backed Iceberg metadata | PASS WITH DISCLOSURE | Managed storage and Iceberg-compatible metadata are in approved S3; the underlying transaction format remains Delta. |
| 20–26 — flow, quality, lineage, history, authorized access | PASS FOR RETAINED TABLE IDENTITIES | The existing successful runs remain applicable because no tables are dropped or recreated; their format limitation is disclosed above. |
| 29 — no unmanaged Iceberg | PASS | The current tables are managed and no explicit table `LOCATION` is used. |
| 37 — zero unexpected Terraform drift | UNVERIFIED | No final connected plan has been created. |
| 38 — no unnecessary compute running | PASS AT LAST INVENTORY | The existing warehouse was stopped and cluster inventory was empty. Recheck at final acceptance. |

## Root-cause analysis

The immediate cause of the current mismatch is a pre-existing set of Delta
UniForm tables combined with idempotent `CREATE TABLE IF NOT EXISTS`: the DDL
does not replace or convert those objects. The exact historical server-side or
earlier-source event that originally created those seven objects as Delta
UniForm cannot be reconstructed from offline repository evidence. No claim is
made about an undocumented engine rewrite.

The acceptance-contract failure is deterministic and proven:

1. `CREATE TABLE IF NOT EXISTS` preserves an existing table and cannot repair
   its format.
2. The original pipeline had no fail-closed metadata gate between table
   creation and data writes.
3. The quality SQL trusted `information_schema.tables`; it did not compare the
   raw Tables API format and Delta properties.
4. The history job emitted `DESCRIBE DETAIL`/`DESCRIBE HISTORY` operations but
   did not assert raw API `data_source_format = ICEBERG` or the absence of
   `delta.*` properties.
5. Final acceptance initially treated successful SQL and an Iceberg metadata
   path as proof of native format. Delta UniForm can provide both, so that
   inference was invalid.

## Retained safeguards and compatibility boundary

The repository now defines three complementary safeguards:

1. `13_assert_native_iceberg_metadata.sql` remains a diagnostic fail-closed
   gate and documents what native format would require; it is not used to
   relabel the live Delta UniForm tables.
2. `scripts/verify_goal4_table_inventory.py` remains a diagnostic verifier for
   a native-Iceberg migration. Its native-only failure is expected and is not
   an acceptance predicate for the fixed compatibility profile.
3. The deprecated `remediation/01_drop_delta_uniform_synthetic_tables.sql` was
   removed from the repository and must not be recreated or run under this
   profile. No deletion or recreation is required for current Goal 4
   acceptance.

The quality result and final pipeline assertion now require exactly ten checks
and the explicit seven-table managed-Iceberg check. A zero-row or partial
result set can no longer pass.

The reviewed offline source identifiers are:

| Source | SHA-256 |
| --- | --- |
| Bundle source aggregate (bundle YAML, resource manifest, 13 top-level SQL files; relative path, NUL, bytes, NUL in sorted order) | `49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027` |
| `databricks.yml` | `4f8f038137ba72bc955493b77fa08ec1bbb9469a04b02228b4bdb8f286d176b5` |
| Resource manifest | `36156bb228c815545f84cba9c6fbc7d8dc969d94aa07c7492b42ba853e7f3f34` |
| Native metadata SQL 13 | `e2f2fa6c1e7fbb01c5bd56ede8d26ae718eb30d1c0baf34aa539f8a8c70ef0d1` |
| Deprecated seven-table drop remediation | Removed; no executable remediation file remains |
| Raw Tables API inventory verifier | `82edb5486b1920905b23dc091b1615f2a6728cf958b1ab47e45bcfaa264b739f` |

The previous connected deployment exposed a second contract gap: the
non-recursive `sync.include` pattern did not act as an allowlist, so the nested
destructive file was synchronized anyway. Read-only inspection found 13
top-level SQL files plus `/sql/goal_04/remediation/01_drop_delta_uniform_synthetic_tables.sql`.
The drop script was not referenced by any job and was not executed, but its
presence violated the reviewed deployment boundary. The approved offline fix
adds an explicit `sync.exclude` for `sql/goal_04/remediation/**`. The static
validator now requires the exact include/exclude block and rejects recursive
include patterns. Regression tests cover both a missing exclusion and a
recursive include. The subsequent approved redeployment proved the exclusion
effective: the remediation path does not exist in the deployed workspace and
exactly 13 top-level SQL files remain.

## Offline validation result

The exact source after this edit passed Ruff format for 74 files, Ruff lint,
strict mypy for six source files, 55 pytest tests with 96.67% branch coverage,
the Goal 4 static validator, Bandit, detect-secrets over tracked/untracked
candidates, safe example configuration validation, infrastructure preflight,
YAML parsing, and `git diff --check`.

Terraform, TFLint, and Trivy executables were unavailable in the current
offline environment, so Terraform recursive format/validate/mock tests and
the two IaC scans were not rerun in this remediation. The last durable
Terraform validation and seven mock runs remain PASS; no Terraform source,
provider lockfile, or dependency declaration changed here. `pip-audit` was
also not rerun because it requires unavailable dependency-index access. No
connected validation or mutation occurred.

## Remaining connected boundary — approvals required

The sync-exclusion validation and redeployment are complete and recorded in
`docs/verification/GOAL-04-BUNDLE-SYNC-EXCLUDE-VERIFICATION-2026-08-12.md`.
Every remaining connected boundary below requires its own explicit approval:

1. Reinspect authorization, table inventory, warehouse, clusters, bundle, and
   source hashes. Existing UC/IAM/KMS/S3 negative-access evidence remains valid
   only if the policies, grants, identities, bindings, and approved paths are
   unchanged; otherwise rerun the affected negative acceptance check.
2. Create a separately approved final connected development Terraform plan and
   require zero unexpected managed-resource change.
3. Rerun all offline gates, finish the 38-row durable report, review the full
   change set, and request a separate evidence-commit approval.

No managed-table deletion is required under this compatibility profile. The
seven existing tables contain only neutral deterministic synthetic data and
remain the governed development assets. The deprecated drop script was removed
from the repository and is not an execution instruction.

## Stop conditions

Stop without retry or ad-hoc repair if:

- any target is not one of the seven exact synthetic development tables;
- the current tables cease to be exactly the seven managed Delta UniForm tables
  with approved Iceberg-compatible metadata;
- a direct location is introduced;
- an existing catalog, metastore, warehouse, cluster, production resource, or
  Goal 5+ resource would change;
- a native-format claim is made without Tables API evidence;
- any connected step lacks separate approval for its exact source/hash and
  mutation scope.

## Authoritative format references

- [Unity Catalog managed Apache Iceberg](https://docs.databricks.com/aws/en/iceberg/)
- [Delta UniForm](https://docs.databricks.com/aws/en/delta/uniform)
- [Unity Catalog Tables API](https://docs.databricks.com/api/workspace/tables/get)
- [Unity Catalog managed tables](https://docs.databricks.com/aws/en/tables/managed)

Goal 4 remains in progress until the compatibility-profile acceptance matrix,
final zero-drift evidence, offline gates, and evidence commit are complete.
The profile explicitly records that native managed Iceberg is no longer used
and that Delta UniForm with Iceberg-compatible metadata is the fixed project
representation going forward.
