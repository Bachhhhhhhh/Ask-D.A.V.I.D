# Goal 4 final verification

## Status

**NOT VERIFIED — approved Iceberg-compatible format profile accepted; final evidence commit remains.**

This report consolidates the durable Goal 4 evidence already present in the
repository. It is deliberately not a completion assertion. Acceptance
criteria 17–19 are evaluated under the approved project compatibility profile:
the raw live Tables API reports every synthetic table as managed Delta
UniForm (`data_source_format = DELTA` plus `delta.*` UniForm properties), with
Iceberg-compatible metadata in approved S3 storage. This is not native
Iceberg and is disclosed rather than relabeled. Criteria 20–26 remain valid
for the retained table identities because no drop/recreation occurred.
Criteria 37 and 38 are now supported by the final connected plan and immediate
read-only compute inspection recorded below. The report remains `NOT VERIFIED`
only because the reviewed Goal 4 change set still requires an immutable evidence
commit and a separately reviewed status-only checkpoint update.

The complete correction and remediation boundary is recorded in
`GOAL-04-NATIVE-ICEBERG-FORMAT-BLOCKER-2026-08-11.md`.

The first blocker-remediation deployment also exposed a bundle-sync leak: the
destructive nested remediation SQL file was present in the workspace despite
the non-recursive include pattern. It was not referenced or executed. The
current source adds explicit `sync.exclude`, and the separately approved
redeployment of aggregate SHA-256
`49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027`
completed successfully. Read-only inspection confirmed the remediation path
is absent and exactly 13 top-level SQL files remain. Durable evidence is in
`docs/verification/GOAL-04-BUNDLE-SYNC-EXCLUDE-VERIFICATION-2026-08-12.md`.

The connected checks above require separate approval. This draft does not
authorize or record a Terraform plan/apply/destroy, AWS mutation, Databricks
mutation, bundle operation, SQL statement, or job run.

## Approved development identity

| Item | Verified value |
| --- | --- |
| AWS account | `736956442295` |
| AWS Region | `ap-southeast-1` |
| Databricks workspace ID | `7474644358733471` |
| Databricks workspace profile | `ask-david-development` |
| Reused metastore ID | `3a7f7e7a-680b-4bd6-907a-6d5e77b43178` |
| Metastore global ID | `aws:ap-southeast-1:3a7f7e7a-680b-4bd6-907a-6d5e77b43178` |
| Existing SQL warehouse | `757e0335c6efb51e` (`Small`, `PRO`, serverless, 10-minute auto-stop) |
| Project catalog | `ask_david_development` |

The exact commercial SKU label was not exposed by the workspace-level API.
Premium-capable functionality is established operationally by the attached
Unity Catalog metastore, serverless SQL, workspace binding support, and the
successful governed SQL workflows. This statement is not native-Iceberg format
evidence. No exact SKU label is inferred.

## Declarative resource and execution evidence

- The existing metastore and its workspace assignment were reused; Goal 4
  declares no metastore or metastore-assignment resource.
- The active-stage saved plan SHA-256
  `c4a81b50ef40531b38a1f785f861d281db02b9e20bc391b209b4c906dafe8502`
  applied as `54 added, 1 changed, 0 destroyed`, with zero AWS action and no
  metastore, assignment, warehouse, cluster, production, or Goal 5+ action.
- Storage-credential validation passed role assumption plus all S3/KMS
  operations, including `READ`, `LIST`, `WRITE`, `DELETE`, and `PATH_EXISTS`.
- Seven zero-byte managed-root markers are encrypted with the approved storage
  KMS key. Seven external locations and the project catalog bind read-write
  only to workspace `7474644358733471`.
- The currently deployed bundle has exactly five jobs and 13 top-level SQL
  workspace files while reusing warehouse `757e0335c6efb51e`; it declares no
  cluster or warehouse. The explicit-exclude redeployment removed the
  previously leaked nested remediation path; the path is absent from the
  deployed workspace.
- The authorization comment-only bundle source aggregate SHA-256 was
  `fb31ecadd9add4b4f5984812a17b4ae3a88344b836e7b4d547a3058c0874e437`.
  Its strict connected validation returned `Validation OK!` without a warning,
  error, or recommendation, and its approved redeployment completed
  successfully. The later `sync.exclude` remediation changed the bundle source
  to the current final aggregate recorded below.
- Exported SQL 11 and SQL 12 match their local sources byte for byte. Their
  executable-only SHA-256 values remain respectively
  `739b582c05dc7c7797dac11b737bb989ff2a5451ae48ae9dd02096c3b6750337`
  and `a02c465782a4a5038b1b76a1d625211bdc8829ae12720ea97c5a661072c259ac`.

## Workflow evidence

| Purpose | Job ID | Successful/evidence run | Result |
| --- | --- | --- | --- |
| Synthetic Raw -> Curated -> Business pipeline | `967410491586823` | `347925882630202` | `SUCCESS`; all eight tasks attempt 0 |
| Managed-Iceberg detail/history/time travel | `695423086105630` | `966938583513350` | `SUCCESS`; seven detail checks, Raw history, version-1 read |
| Deterministic table lineage | `825751066015430` | `764855862302905` | `SUCCESS`; exact Raw -> Curated and Curated -> Business edges |
| Denied protected-table access | `187789722076444` | `231413013546726` | Expected failure: `INSUFFICIENT_PERMISSIONS`, SQLSTATE `42501` |
| Denied direct managed-storage path | `992194321630936` | `791479735507837` | Structural rejection: `LOCATION_OVERLAP` |

The direct-path result is not described as a principal-specific permission
error. Criterion 28 relies on that managed-storage structural guard together
with the separately approved live Unity Catalog and AWS policy inspection.
That inspection found no denied-principal data/storage grant or AWS identity,
only the intended Unity Catalog master-role/self-role trust, one prefix-scoped
inline IAM policy, KMS access limited to account root and the storage role, and
no bucket-policy `Allow` principal.

## Final acceptance matrix

| # | Acceptance criterion | Result | Durable evidence |
| --- | --- | --- | --- |
| 1 | Approved existing Databricks development workspace verified | PASS | OAuth preflight resolved workspace `7474644358733471` and the approved administrator principal. |
| 2 | Workspace is Premium-capable for required serverless functionality | PASS | Unity Catalog, serverless DBSQL, workspace bindings, and approved governed SQL workflows operated successfully; exact commercial SKU label remains unavailable and native format is evaluated separately. |
| 3 | Workspace Region is correct | PASS | Attached metastore global ID is in `ap-southeast-1`, matching the AWS development Region. |
| 4 | Unity Catalog is enabled | PASS | Metastore API and `current_metastore()` returned the same metastore. |
| 5 | Existing metastore was verified and reused | PASS | Metastore ID before and after Goal 4 is `3a7f7e7a-680b-4bd6-907a-6d5e77b43178`; Terraform declares no metastore. |
| 6 | No duplicate metastore was created | PASS | Preflight inventory, Terraform action inventory, and source ownership contain no metastore create. |
| 7 | Unity Catalog remains primary governance authority | PASS | Project catalog, schemas, grants, storage credential, locations, lineage, and authorization use Unity Catalog; Glue inventory was empty and no competing catalog was implemented. |
| 8 | Existing Serverless SQL Warehouse is usable | PASS | Pipeline, history, lineage, and negative checks used warehouse `757e0335c6efb51e`. |
| 9 | Managed Iceberg-compatible tables operate without an unnecessary classic cluster | PASS WITH DISCLOSURE | Existing Serverless SQL executed the governed workflow; no classic cluster exists. Tables API format is disclosed as managed Delta UniForm. |
| 10 | AWS IAM-based storage credential works | PASS | Credential validation passed role assumption and every labeled S3/KMS operation; managed-table I/O succeeded. |
| 11 | External locations use only approved S3 paths | PASS | Seven location URLs and the live prefix-scoped IAM policy match only approved Goal 3 buckets and `unity-catalog/development/*` roots. |
| 12 | KMS access works | PASS | Markers use the approved KMS key and credential validation plus governed table write/read succeeded. |
| 13 | Required namespaces exist | PASS | Active-stage inspection found catalog `ask_david_development` and all six `green_sm_*` schemas. |
| 14 | Least-privilege grants exist | PASS | Live UC inspection matched the governance-admin, data-engineer, workflow, and denied-principal grant contract. |
| 15 | Service principals are correctly scoped | PASS | SCIM, membership, entitlement, run-as, UC grant, and AWS-policy inspection matched the two-purpose principal model. |
| 16 | All six generic Iceberg-compatible test-table categories exist | PASS WITH DISCLOSURE | All six semantic categories and seven managed tables exist; Tables API format is Delta UniForm with Iceberg-compatible S3 metadata. |
| 17 | Managed Iceberg-compatible tables | PASS WITH DISCLOSURE | All seven are `MANAGED`; raw Tables API truth is `DELTA` UniForm, not native Iceberg. |
| 18 | No unapproved format substitution | PASS WITH DISCLOSURE | Delta UniForm is the explicitly accepted development representation; no external or unmanaged table is present. |
| 19 | Approved S3-backed Iceberg-compatible metadata | PASS WITH DISCLOSURE | Managed storage and Iceberg-compatible metadata are in approved S3; the underlying transaction format remains Delta. |
| 20 | Raw synthetic flow succeeds | PASS | Run `347925882630202` succeeded on the retained table identities. |
| 21 | Curated synthetic flow succeeds | PASS | Run `347925882630202` produced the deterministic Curated assertions. |
| 22 | Business synthetic flow succeeds | PASS | Run `347925882630202` produced the deterministic Business assertions. |
| 23 | Quality checks succeed | PASS WITH DISCLOSURE | The recorded checks passed; raw Tables API format is disclosed separately as Delta UniForm. |
| 24 | Lineage is recorded | PASS | Run `764855862302905` proved both directed lineage edges for the retained identities. |
| 25 | Iceberg-compatible snapshots/history are inspectable | PASS WITH DISCLOSURE | Run `966938583513350` passed history/time-travel assertions; Tables API identifies the underlying Delta UniForm representation. |
| 26 | Authorized access succeeds | PASS | Governed workflow writes/reads succeeded for the retained managed tables. |
| 27 | Unauthorized table access is rejected | PASS | Denied-principal run `231413013546726` reached SQL and failed with `INSUFFICIENT_PERMISSIONS`, SQLSTATE `42501`. |
| 28 | No direct S3 governance bypass exists | PASS | Managed-path `LOCATION_OVERLAP` plus clean live UC/IAM/KMS/S3 policy inspection. |
| 29 | No unmanaged Iceberg table exists | PASS | Seven live detail checks identify managed tables and executable DDL contains no explicit table `LOCATION`. |
| 30 | Development isolation is enforced | PASS | Credential, seven locations, and catalog bind only to development workspace `7474644358733471`. |
| 31 | Existing Databricks system catalogs were not modified | PASS | Before/after catalog inspection and Terraform ownership/action inventory exclude `workspace`, `ml`, `ml_model_store`, `samples`, and `system`. |
| 32 | No production resource was modified | PASS | All approved inputs, bindings, plans, bundle target, and resource names are development-only. |
| 33 | No real Green SM business data was introduced | PASS | SQL fixtures and live assertions contain neutral synthetic technical identifiers and values only. |
| 34 | No Goal 5+ implementation was introduced | PASS | Repository scope review finds only Goal 4 lakehouse foundation; later-goal directories remain unchanged placeholders. |
| 35 | No accepted ADR changed | PASS | Current accepted-ADR diff is empty. |
| 36 | No secret, token, state, or plan is tracked by Git | PASS | Candidate scan passed; tracked-file review is empty; local tfvars, backend, state, and plan files resolve through `.gitignore`. This must be rerun after final report edits. |
| 37 | Second Terraform plan shows no unexpected drift | PASS | Final saved plan SHA-256 `2fe6fd3eeeea72b703d27d10bba2cf5b0fcbdc27933ee2fb2857030ecab0edaa` reported `No changes`; decoded action set was 189 `no-op`, 0 non-no-op. |
| 38 | No unnecessary compute remains running | PASS | Immediate final inspection found warehouse `757e0335c6efb51e` stopped with zero active sessions and an empty cluster inventory. |

## Phase 4-7 repository audit snapshot

The pre-final local audit on `2026-08-11` established:

- `git diff --check` passed;
- accepted ADR diff is empty;
- the deployed bundle-source aggregate remains
  `fb31ecadd9add4b4f5984812a17b4ae3a88344b836e7b4d547a3058c0874e437`;
- the bundle-sync remediation aggregate
  `49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027`
  was deployed under separate approval and its excluded workspace path was
  absent on read-only inspection;
- ignored local `terraform.tfvars`, `backend.hcl`, Terraform state, and saved
  plans are not tracked;
- no Goal 5+ implementation appeared in the change set; and
- the Goal 4 working tree remains uncommitted.

This snapshot is not the final offline gate because this report and the later
status update must themselves be included in the final exact-source audit.

## Pre-final offline validation

The following checks were rerun on the current Goal 4 source and this draft
report without contacting AWS or Databricks:

| Gate | Result |
| --- | --- |
| Ruff format | PASS — 74 files |
| Ruff lint | PASS |
| Strict mypy | PASS — 6 source files |
| Pytest | PASS — 55 tests |
| Branch coverage | PASS — 96.67%, threshold 90% |
| Goal 4 deterministic static validator | PASS |
| Bandit | PASS |
| detect-secrets over tracked and untracked candidates | PASS |
| Safe environment example | PASS |
| Ignored-input infrastructure preflight | PASS |
| Terraform recursive format | PASS |
| Bootstrap Terraform validation | PASS |
| Development Terraform validation | PASS |
| Terraform mock-provider contracts | PASS — 7 runs, 0 failed |
| `git diff --check` | PASS |

The session's `uv` binary was unavailable and the retained virtualenv scripts
contained stale absolute shebangs. The checks therefore used the retained
Python 3.12 site packages with `/usr/bin/python3`; pytest cache and coverage
artifacts were redirected to `/tmp`. A focused diagnostic invocation initially
failed because its fixture created the nested remediation parent twice; that
test-only defect was corrected with idempotent directory creation. The clean
default invocation then passed all 55 tests.

Terraform provider schema execution was blocked by the filesystem sandbox's
plugin handshake. The exact offline `validate` and mock-test commands were
rerun outside that sandbox with the existing provider cache and without
`init`, backend access, plan, apply, or cloud credentials; both validations and
all seven mock runs passed.

TFLint and Trivy were not rerun because their temporary binaries are no longer
present. `pip-audit` was not rerun because the gate is offline and the audit
requires dependency-index access. The last durable Goal 4 runs for all three
remain PASS. This blocker remediation changed no Terraform/IaC source,
dependency version, or lockfile; its Python additions passed Ruff, strict
mypy, pytest, Bandit, and detect-secrets. These limitations remain explicit.

## Final connected verification — 2026-08-12

The approved final connected checkpoint revalidated AWS account `736956442295`,
Region `ap-southeast-1`, and Databricks workspace `7474644358733471` in
`RUNNING`/`PREMIUM` state. The existing Unity Catalog metastore and Serverless
SQL Warehouse were reused; no metastore, warehouse, cluster, production, or
Goal 5+ resource was created.

The hash-verified grant-remediation plan
`764771e24915aedc9a311e3622d8f2b778ed5782f6945408c62f2f9a7be534c1` applied as
`0 added, 2 changed, 0 destroyed`. It removed only the two redundant direct
grants for `bachvxuan@gmail.com`; immediate read-only inspection confirmed the
catalog/schema grant sets, warehouse `757e0335c6efb51e` stopped with zero active
sessions, and an empty cluster inventory.

The subsequent final saved development plan
`goal4-final-zero-drift-20260812b.tfplan` has SHA-256
`2fe6fd3eeeea72b703d27d10bba2cf5b0fcbdc27933ee2fb2857030ecab0edaa`.
Terraform reported `No changes`; local JSON decoding found 189 `no-op`
resource actions and zero non-no-op actions. No apply or destroy followed that
plan.

The separately approved strict connected bundle validation ran from the
`databricks/` bundle root with profile `ask-david-development`, target
`development`, the Terraform-derived warehouse/service-principal/S3-probe
variables, and no `workspace_host` variable. It returned `Validation OK!` with
no warning or error. No deployment, job/SQL execution, compute creation,
Terraform operation, or AWS mutation occurred.

The current source set used for this final validation is the exact bundle YAML,
resource manifest, and 13 top-level SQL files whose repository-relative/NUL
aggregate is
`49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027`.
The current `databricks.yml` SHA-256 is
`49c31de9b18fe350b660ea2821e3413982a637e36bcfca158e1e9e5bdd63ab97`; the
resource manifest SHA-256 remains
`36156bb228c815545f84cba9c6fbc7d8dc969d94aa07c7492b42ba853e7f3f34`.

The post-report offline gate on `2026-08-12` reran the Goal 4 static validator,
the complete pytest suite, coverage, `git diff --check`, accepted-ADR diff
inspection, and tracked-sensitive-artifact inspection. The static validator
passed; pytest passed all 55 tests with 96.67% coverage; the diff check and ADR
diff were clean; and no local tfvars, backend configuration, state, saved plan,
credential, or token was tracked.

## Remaining approval boundaries

1. Approve a dedicated Goal 4 evidence commit. Do not include local tfvars,
   backend configuration, state, saved plans, credentials, or tokens.
2. Record the immutable evidence commit SHA in a separately reviewed
   status-only commit before changing Goal 4 to `VERIFIED`.

## Current conclusion

Goal 4 is not yet verified. The approved project compatibility profile retains
the seven managed Delta UniForm tables and accepts their governed
Iceberg-compatible S3 metadata; native Iceberg is no longer a planned or
required format. Final zero drift, refreshed resource inspection, offline
gates, and bundle validation now pass. An immutable evidence commit and a
status-only checkpoint commit remain required.
