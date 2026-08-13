# Project status

This file is a checkpoint index, not evidence by assertion. `VERIFIED` is
allowed only when the row identifies the exact reviewed commit and durable
verification evidence. A plan or implementation commit alone is not
verification.

## Current snapshot

- Reconstruction baseline reviewed: `ec025e18666daac5c1979a2aad6f34a141c2351d`
- Current Goal 3B connected-execution evidence:
  `docs/verification/GOAL-03B-CONNECTED-EXECUTION-2026-08-05.md`. Its
  Terraform remediation and report are committed at
  `634c67104d67e17d3bcd9747acbdbdc8ffc928a3`.
- Reconstruction date: `2026-08-05`
- Last verified commit: `9c0d67b30db96a24d015c9cb79821b2fbb107f23`
- Goal 4 evidence commit: `a778cfdfceaf6c704f98d83752c54c73a7d9208f`
  (`goal-04: record connected lakehouse verification`). It contains the
  reviewed Goal 4 implementation, durable verification reports, the final
  zero-drift evidence, and the current bundle-validation evidence; ignored
  local inputs and credentials are not tracked.
- Goal 5 evidence commit: `9c0d67b30db96a24d015c9cb79821b2fbb107f23`
  (`goal-05: complete synthetic ingestion MVP verification`). It contains the
  reviewed Goal 5 implementation, contracts, neutral synthetic fixtures,
  Terraform/bundle configuration, tests, runbooks, and durable connected
  verification reports; ignored local inputs and credentials are not tracked.
- Goal 5 MVP Phase 5-0 read-only preflight completed on `2026-08-12`; no
  Databricks or AWS mutation occurred. The durable report is
  `docs/verification/GOAL-05-PHASE-5-0-PREFLIGHT-2026-08-12.md`. The existing
  seven Goal 4 tables remain managed Delta UniForm according to the
  authoritative Tables API, which is an accepted Goal 5 interoperability
  profile and is not native Iceberg.
- Goal 5 Phase 5-1 minimal ingestion design is recorded in
  `docs/plans/GOAL-05-MVP-INGESTION-PLAN.md`. The offline implementation
  checkpoint is now complete and is recorded in
  `docs/verification/GOAL-05-PHASE-5-2-OFFLINE-IMPLEMENTATION-2026-08-12.md`;
  no connected plan, bundle operation, SQL/job run, AWS mutation, or
  Databricks mutation occurred.
- The implementation includes typed contracts/adapters, neutral fixtures,
  nine managed-table SQL definitions, one existing-warehouse bundle workflow,
  deterministic quality/provenance/idempotency assertions, three optional
  Terraform-managed SSE-KMS source objects, and offline format-policy tests.
  At this offline implementation checkpoint, the exact
  `read_files`/parameterized-path capability, connected table creation, and
  live output evidence were still unverified; their later connected evidence
  is recorded below and committed in the Goal 5 evidence commit.
- Goal 5 Phase 5-3 connected read-only revalidation passed for the approved
  development workspace, metastore, warehouse, AWS account, and region. The
  saved development plan was generated from the repository root with the
  source-object flag enabled only through a transient `-var`; it contains
  exactly three S3 object creates and zero update/replace/destroy actions. Its
  durable report is
  `docs/verification/GOAL-05-PHASE-5-3-CONNECTED-PLAN-2026-08-12.md`, and its
  saved-plan SHA-256 is
  `457d6f7a50be5b7cca1ed6240b9cab7c5e16bb9c0ef4242d67d520e21f1b8474`.
  The approved plan then applied exactly three source objects; immediate
  read-only S3 inspection and fixture hash comparison passed. Durable evidence
  is `docs/verification/GOAL-05-PHASE-5-4-SOURCE-OBJECT-APPLY-2026-08-12.md`.
- The separately approved strict connected bundle validation then stopped
  before deployment with one warning: the required explicit
  `sql/goal_04/remediation/**` exclusion matched no files because the
  remediation directory is intentionally empty. Strict mode converted that
  warning into exit `1`; no deployment or execution occurred. Durable
  evidence is
  `docs/verification/GOAL-05-PHASE-5-5-BUNDLE-VALIDATION-2026-08-12.md`.
- The approved offline remediation added only the non-executable
  `databricks/sql/goal_04/remediation/README.md` marker, retained the explicit
  sync exclusion, and added static regression coverage. No connected retry or
  bundle deployment occurred after this remediation. Full offline evidence is
  `docs/verification/GOAL-05-PHASE-5-6-OFFLINE-REMEDIATION-2026-08-12.md`.
- The separately approved remediated strict connected bundle validation then
  passed with `Validation OK!`, no warning, error, or recommendation, using
  the unchanged full source aggregate
  `eb4c7e6db55d9ec5aedf63480ecf00bb5cd404b9b64ddc1f4930d87ab1060368`.
  Durable evidence is
  `docs/verification/GOAL-05-PHASE-5-7-BUNDLE-VALIDATION-2026-08-12.md`.
  No deployment or job/SQL execution occurred.
- The separately approved exact-source bundle deployment then completed with
  `Deployment complete!`. Read-only inspection confirmed new Goal 5 job
  `382877731318442`, all six byte-matched Goal 5 SQL workspace files, correct
  workflow-SP run-as and ACLs, unchanged five Goal 4 job identities, no active
  Goal 5 run, and the existing warehouse still stopped. Durable evidence is
  `docs/verification/GOAL-05-PHASE-5-8-BUNDLE-DEPLOYMENT-2026-08-12.md`.
- The first separately approved Goal 5 workflow run `1025066514456351` stopped
  fail-closed on `2026-08-13`. `create_goal5_tables` succeeded; the three
  `read_files` ingestion tasks failed with `INSUFFICIENT_PERMISSIONS` / "User
  does not have permission SELECT on any file", and the two verification tasks
  were skipped upstream. No retry ran and no source data was written. The
  durable analysis and offline declarative remediation are recorded in
  `docs/verification/GOAL-05-SOURCE-ACCESS-REMEDIATION-2026-08-13.md`.
- The separately approved strict connected validation of the corrected CDC
  source set passed with `Validation OK!`, exit `0`, and no warning, error, or
  recommendation. It used aggregate
  `bd4cd49ee07147f9f240a10b936c78dad76b9dca62622b10f0fb62f6318eb3cd` and is
  recorded in `docs/verification/GOAL-05-CDC-BUNDLE-VALIDATION-2026-08-13.md`.
  No deployment, job/SQL execution, table/data mutation, compute creation,
  Terraform operation, or AWS operation occurred.
- The separately approved corrected bundle deployment completed with
  `Deployment complete!`. Read-only inspection confirmed the existing Goal 5
  job `382877731318442`, six SQL tasks, workflow service-principal run-as,
  existing warehouse `757e0335c6efb51e`, and deployed CDC SQL hash
  `9ce80b73ec48bf0a7568fad81faf791f286dbfbae4c66ca0a9af84fe013f66fd`.
  Run history showed no new run from deployment. Durable evidence is
  `docs/verification/GOAL-05-CDC-BUNDLE-DEPLOYMENT-2026-08-13.md`.
- The separately approved single corrected workflow retry ran as
  `149148676670509`. Table creation, structured ingestion, document ingestion,
  and CDC ingestion succeeded, but `verify_goal5_outputs` failed its CDC
  current-state assertion; idempotency was skipped upstream. No further run
  or connected operation was performed. Durable evidence is
  `docs/verification/GOAL-05-WORKFLOW-RETRY-2026-08-13.md`.
- The approved offline CDC output-assertion remediation replaced the brittle
  text comparison of a `DOUBLE` JSON value with numeric `TRY_CAST` semantics,
  preserved the UPDATE/tombstone assertions, and added fail-closed static
  regression coverage. Goal 4/Goal 5 static validation, 124 pytest tests
  (97.15% coverage), Ruff, mypy, Bandit, detect-secrets, and `git diff --check`
  passed. Its durable report is
  `docs/verification/GOAL-05-CDC-OUTPUT-ASSERTION-REMEDIATION-2026-08-13.md`.
- The separately approved strict connected validation for that remediation
  passed with `Validation OK!`, exit `0`, and no warning, error, or
  recommendation for aggregate
  `e06e5e26ac83aa0ea30c93f12b747686cef67e3d80f9cb862998f931477dd507`.
  Evidence is
  `docs/verification/GOAL-05-CDC-OUTPUT-ASSERTION-BUNDLE-VALIDATION-2026-08-13.md`.
  No deployment, job/SQL execution, Terraform, or AWS operation occurred.
- The separately approved redeployment of that exact aggregate completed with
  `Deployment complete!`. Immediate read-only inspection confirmed the
  existing Goal 5 job, six tasks, workflow-SP run-as, warehouse bindings, and
  byte-matched output-verification SQL. No job run was triggered. Evidence is
  `docs/verification/GOAL-05-CDC-OUTPUT-ASSERTION-BUNDLE-DEPLOYMENT-2026-08-13.md`.
- The separately approved single workflow retry after that redeployment ran as
  `172279846311777` and terminated `SUCCESS`: all three ingestion tasks,
  output assertions, and idempotency assertions passed. Its durable evidence
  is `docs/verification/GOAL-05-NUMERIC-ASSERTION-WORKFLOW-SUCCESS-2026-08-13.md`.
- Read-only post-run verification confirmed all three SSE-KMS synthetic source
  objects, all nine Goal 5 Tables API entries as managed Delta UniForm with
  Iceberg metadata, the existing metastore/bundle/Goal 4 table health, and no
  classic cluster. Evidence is
  `docs/verification/GOAL-05-CONNECTED-SYNTHETIC-VERIFICATION-2026-08-13.md`.
- Last repository-wide executable verification: `VERIFIED BY PROJECT OWNER`
- Verification provenance: the project owner confirmed on `2026-08-05` that
  the Goal 2 and Goal 3A acceptance checks passed on the previous development
  machine and that the GitHub Actions failures were corrected. Raw historical
  logs are not committed in this repository.
- Current pre-3B offline verification:
  `docs/verification/GOAL-03-PRE-3B-READINESS-2026-08-05.md`
- Final Goal 3B offline blocker review: `2026-08-10`; all commit-candidate
  validation gates passed without an AWS operation.
- Goal 4 Phase 4-0 read-only preflight date: `2026-08-10`.
- Goal 4 Phase 4-1 design approval: `2026-08-10`; approved hierarchy is one
  `ask_david_development` catalog with six `green_sm_*` schemas and staged
  `initial role -> self-trust -> validation -> active` rollout.
- Goal 4 implementation status: the first approved bootstrap apply partially
  succeeded, then the approved two-step IAM remediation completed. Initial-role
  saved-plan SHA-256
  `2ddc27a4336db94dbb9b159af1b4d2389752e017f0260635c0e5bfa4b6cb0d6d`
  applied as `2 added, 1 changed, 0 destroyed`; self-assumption saved-plan
  SHA-256
  `395828d28b26aae401dae740c69f9b20693dae7a5c34d0764278c12c797d5c59`
  applied as `0 added, 1 changed, 0 destroyed`.
- The first Goal 4 storage-credential validation passed `READ`, `LIST`,
  `WRITE`, and `DELETE`, but failed `PATH_EXISTS`. The approved marker plan
  SHA-256
  `fd0b05d7125c7074a822b89487463a831791cb860424b6de3f0fbe703c8a223e`
  then applied exactly seven zero-byte SSE-KMS S3 markers. The second approved
  one-shot validation passed every operation, including `PATH_EXISTS`.
- The active-stage saved plan SHA-256
  `c4a81b50ef40531b38a1f785f861d281db02b9e20bc391b209b4c906dafe8502`
  applied as `54 added, 1 changed, 0 destroyed`; immediate read-only inspection
  passed for the intended Databricks foundation. Its AWS action count was zero,
  and no replacement, destroy, metastore/assignment, warehouse/cluster,
  production, or Goal 5+ action occurred.
- The first strict connected bundle validation ran once and exited `1` before
  deployment because the unresolved `${var.workspace_host}` bundle mapping
  could not be reconciled with the named profile. Inspection confirmed no
  deployment, job, SQL, compute, or bundle-state side effect.
- The second strict validation confirmed the host/profile remediation, then
  exited `1` on one inherited-folder permission warning and one target-root
  recommendation. It created only an ignored local `.databricks/.gitignore`;
  no deploy or execution occurred at that checkpoint. The later approved
  target-root/permission remediation remained uncommitted.
- The third separately approved strict connected validation used bundle
  SHA-256
  `a3c4d178fc44afe19691403dd3a746822e24f88e53782432f2f51f0ae6c394e7`
  and resources SHA-256
  `8ce89a428d0521344b279a767afaf02051fcdffaeae85ea2f13662745505f919`.
  Databricks CLI `1.11.0` exited `0` with `Validation OK!`, no warning, and no
  recommendation. No deploy or SQL/job execution occurred.
- The separately approved deployment of aggregate source SHA-256
  `022cebf1d12e8a22d5e9f7f57b1a5d9d4ca28dede7f71666b09ea1bfc318ec7e`
  completed with exit `0`. Read-only inspection verified exactly five jobs and
  12 SQL files, correct run-as identities and warehouse references, no active
  runs, warehouse `STOPPED`, and an empty cluster inventory. At that deployment
  checkpoint, no job or SQL task had run.
- The separately approved one-time authorized pipeline run
  `347925882630202` completed `TERMINATED/SUCCESS`. All eight tasks used the
  existing warehouse and succeeded at attempt `0`; final SQL assertions covered
  Raw, Curated, Business, quality, and seven managed-Iceberg tables. No active
  run remained. The warehouse was `RUNNING` only inside its 10-minute auto-stop
  window.
- The first separately approved history verification run `952431524488579`
  failed at attempt `0` before inspection because Serverless SQL rejected
  concatenation inside `DESCRIBE DETAIL IDENTIFIER(...)`. It was not retried.
  The approved read-only SQL remediation is implemented and offline validated;
  history/time-travel was UNVERIFIED at that checkpoint.
- The remediated aggregate source SHA-256
  `9714d971417979d131d23f051519f10cb83392b9aa7927a33af4d68840691c4e`
  then passed one strict connected bundle validation with exit `0`, no warning,
  and no recommendation. At that validation checkpoint it had not been
  redeployed, and no history retry had run.
- The separately approved redeployment then completed with exit `0`; all five
  job IDs/names/task counts remained unchanged. The exported deployed history
  file SHA-256
  `7b521c1f5d4a24d55a0c6658a87c7d0703b35994ee58bc98f01e1062cdfa3927`
  matches local source. No job ran during redeployment or inspection.
- The remediated one-time history run `966938583513350` then completed
  `TERMINATED/SUCCESS` at attempt `0`. Seven table-detail inspections, Raw
  history, and the version-1 assertion executed successfully. No active run
  remained; the warehouse was in its 10-minute auto-stop window.
- Review of the still-unexecuted lineage job found that its SQL could succeed
  with zero matching rows and did not cover Curated-to-Business. The approved
  offline remediation now requires two deterministic, directed assertions in
  `system.access.table_lineage`: Raw synthetic events to Curated synthetic
  events, and Curated synthetic events to Business synthetic metrics. Static
  validation and regression evidence are recorded in
  `docs/verification/GOAL-04-LINEAGE-ACCEPTANCE-REMEDIATION-2026-08-11.md`.
  The separately approved strict connected validation of aggregate SHA-256
  `fc68749ff6f26741212ea9a4763844c5ad7c91bdaf26cf3084070103366ee257`
  and lineage SQL SHA-256
  `0be1b989978af4bb467fde8e336ef15a2b9cad78be62ae76c1d4fb5ad81f6a4e`
  exited `0` with `Validation OK!`, no warning, and no recommendation. No
  lineage SQL/job run occurred at that checkpoint.
- The separately approved lineage-source redeployment then completed with
  `Deployment complete!`. Read-only inspection confirmed the same five job
  IDs, names, task counts, run-as identities, existing warehouse reference,
  and lineage file path. The exported deployed lineage SQL matches reviewed
  source SHA-256
  `0be1b989978af4bb467fde8e336ef15a2b9cad78be62ae76c1d4fb5ad81f6a4e`.
  No job or SQL task ran during deployment or inspection.
- The separately approved one-time lineage run `764855862302905` completed
  `TERMINATED/SUCCESS`; task `inspect_table_lineage` succeeded at attempt `0`
  and no active run remained. Its fail-closed SQL proves both exact
  Raw-to-Curated and Curated-to-Business edges in
  `system.access.table_lineage`. The existing warehouse was `STOPPED` before
  the run and `RUNNING` only inside its 10-minute auto-stop window afterward.
- The first separately approved protected-table negative run
  `401673129115320` failed at attempt `0` before SQL execution with
  `INTERNAL_ERROR`: denied principal could not fetch synchronized
  `11_denied_table_access.sql` from the user-scoped bundle root. This is not
  Unity Catalog rejection evidence, so criterion 27 was UNVERIFIED at that
  checkpoint. The approved offline remediation gives that principal exactly
  top-level bundle
  `CAN_VIEW` so it can read the neutral SQL file, while validator regression
  tests reject missing, `CAN_RUN`, or `CAN_MANAGE` access. Exact aggregate
  source SHA-256
  `26a6b65951f39e5bf9dcdb53f21d5ddc9c493d0346d60e3b68657e5f576508c1`
  passed strict connected validation with `Validation OK!`, no warning, and no
  recommendation. Its exact-source redeployment then completed; read-only
  inspection proved unchanged five-job configuration, denied-principal
  `CAN_VIEW`, inherited workspace-file `CAN_READ`, and exact exported negative
  SQL hashes.
- The protected-table retry ran once as job run `231413013546726`, task run
  `210727807599395`, attempt `0`. The SQL file loaded successfully and Unity
  Catalog returned `INSUFFICIENT_PERMISSIONS`, no `USE CATALOG` on
  `ask_david_development`, SQLSTATE `42501`. Criterion 27 is PASS even though
  Databricks correctly records this expected-failure job as
  `ERROR/RUN_EXECUTION_ERROR`.
- The direct-path job ran once as job run `791479735507837`, task run
  `263272690337919`, attempt `0`. `CheckPathAccess` rejected the approved
  managed-storage URL with `INVALID_PARAMETER_VALUE.LOCATION_OVERLAP`. This is
  structural managed-path enforcement, not principal-specific authorization.
  The separately approved live UC/IAM/KMS/S3 inspection found no denied-SP
  storage/data grant or AWS identity, exact development-only bindings, exactly
  one prefix-scoped IAM inline policy with no attached policy, matching
  UC-master/self-role trust plus external-ID condition, a KMS policy limited to
  account root and the storage role, and TLS-deny-only bucket policies. The
  combined evidence satisfies criterion 28.
- The authorization evidence-contract remediation changed only comments in
  synchronized SQL 11/12 plus validators, tests, and documentation. Aggregate
  bundle source SHA-256
  `fb31ecadd9add4b4f5984812a17b4ae3a88344b836e7b4d547a3058c0874e437`
  passed one strict connected validation with `Validation OK!`, no warning,
  error, or recommendation. Its separately approved redeployment completed
  successfully. Read-only summary retained the same five job IDs, task graphs,
  run-as identities, and existing warehouse. Exported SQL 11/12 matched local
  source byte for byte; their executable-only hashes remained unchanged. No
  job, SQL, compute, Terraform, or AWS operation ran during that redeployment
  checkpoint.
- The approved native-Iceberg blocker bundle deployment exposed a separate
  sync-boundary defect: despite the non-recursive top-level SQL include, the
  nested destructive remediation file was present in the deployed workspace.
  It was not referenced by a job and was not executed. The offline fix added
  explicit `sync.exclude = sql/goal_04/remediation/**`, static enforcement,
  regression tests, and durable incident documentation. The separately
  approved redeployment of aggregate SHA-256
  `49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027`
  completed successfully; read-only inspection found exactly 13 top-level SQL
  files and no deployed remediation path. Durable evidence is recorded in
  `docs/verification/GOAL-04-BUNDLE-SYNC-EXCLUDE-VERIFICATION-2026-08-12.md`.
- The approved grant-remediation plan
  `764771e24915aedc9a311e3622d8f2b778ed5782f6945408c62f2f9a7be534c1` applied
  as `0 added, 2 changed, 0 destroyed`, removing only the redundant direct
  catalog/schema grants for `bachvxuan@gmail.com`. Immediate read-only
  inspection confirmed the existing Serverless warehouse was stopped with no
  active sessions and cluster inventory was empty.
- The final approved connected development plan
  `goal4-final-zero-drift-20260812b.tfplan` has SHA-256
  `2fe6fd3eeeea72b703d27d10bba2cf5b0fcbdc27933ee2fb2857030ecab0edaa`.
  Terraform reported `No changes`; decoded actions were 189 `no-op` and zero
  non-no-op actions. No apply or destroy followed that plan.
- The final approved strict connected bundle validation ran from `databricks/`
  with profile `ask-david-development`, target `development`, reviewed
  Terraform-derived variables, and no `workspace_host`. The current source
  aggregate (bundle YAML, resource manifest, and 13 top-level SQL files) was
  `49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027`.
  It returned `Validation OK!` with no warning or error. No deployment,
  job/SQL execution, compute creation, Terraform operation, or AWS mutation
  occurred.

| Checkpoint | Status | Implementation evidence | Verification evidence |
| --- | --- | --- | --- |
| Goal 1 — Architecture contract | VERIFIED | `f89fa1f5552b774f1c2a5e4472b0b8a7e12efa9a`; reviewed through `ec025e18666daac5c1979a2aad6f34a141c2351d` | Static consistency review of the governance documents and all accepted ADRs, recorded by this status snapshot. ADR-006 has a Markdown completeness defect but its accepted decision is unambiguous. |
| Goal 2 — Repository and development foundation | VERIFIED | `f89fa1f5552b774f1c2a5e4472b0b8a7e12efa9a`, `2881e23ece07f790e4fadf477580fb75ab5639b4`, `f5e3e8345ce7e96a751697fed212c90c18775d63`; source snapshot reviewed through `ec025e18666daac5c1979a2aad6f34a141c2351d` | Project-owner attestation dated `2026-08-05`: Goal 2 acceptance checks passed on the previous development machine. Raw test, coverage, local-service, lint, type-check, and security reports were not retained in the repository. |
| Goal 3A — AWS Terraform implementation and offline validation | VERIFIED | `a70d806da9b7df6d9218537062bf8670c817b662` plus CI fixes `9cc3104`, `fdca7c8`, and `2a9abfe`; the isolated synthetic validation resources and accepted base-alarm remediation are committed at `634c67104d67e17d3bcd9747acbdbdc8ffc928a3`. | On `2026-08-10`, Terraform formatting, bootstrap/development validation, 9 Terraform contract runs, TFLint, Trivy, strict preflight, Ruff, mypy, 15 pytest tests with 96.67% coverage, Bandit, detect-secrets, environment validation, dependency audit, pre-commit file-integrity hooks, and `git diff --check` passed. Terraform/Ruff/mypy/detect-secrets/pytest hooks were validated directly rather than duplicated inside pre-commit. The reviewed source and durable evidence are committed at `634c67104d67e17d3bcd9747acbdbdc8ffc928a3`. |
| Goal 3B — Connected AWS deployment and smoke testing | VERIFIED | Bootstrap, development, VPC Flow Logs, static smoke-task foundations, dedicated NAT fallback, Redis revision 4, and the base RDS CPU alarm remediation were applied from separately approved saved plans. The reviewed implementation is committed at `634c67104d67e17d3bcd9747acbdbdc8ffc928a3`. Alarm plan SHA-256 `db143549fe551a397afac6b88248b8be74b48b689fa8a685c6868af43816f331` applied as `1 added, 1 changed, 0 destroyed`. | `docs/verification/GOAL-03B-CONNECTED-EXECUTION-2026-08-05.md`, committed at `634c67104d67e17d3bcd9747acbdbdc8ffc928a3`, records all three passing dynamic smoke checks, deterministic connected SG/AOSS unauthorized-path enforcement, VPC Flow Log ingestion, successful alarm apply, read-only CloudWatch/KMS verification, and final post-remediation zero-drift plan SHA-256 `db9ec9f069bf03d724689d1cf2a3347a43dd63c18df81f99463f18bf649d78be` exiting `0` with zero non-no-op resource/output changes. |
| Goal 4 — Databricks, Unity Catalog, and Iceberg | VERIFIED — PROJECT ICEBERG-COMPATIBILITY PROFILE | Evidence commit `a778cfdfceaf6c704f98d83752c54c73a7d9208f` contains the reviewed staged Terraform, verified storage credential, development UC foundation, five-job bundle, durable reports, final zero-drift evidence, and current strict bundle-validation evidence. Tables API truth is seven managed Delta UniForm tables with Iceberg-compatible metadata in approved S3; the project owner approved retaining them as the fixed project representation without destructive recreation. Native Iceberg is no longer planned. | `docs/verification/GOAL-04-FINAL-VERIFICATION-2026-08-11.md`, `docs/verification/GOAL-04-NATIVE-ICEBERG-FORMAT-BLOCKER-2026-08-11.md`, and `docs/verification/GOAL-04-BUNDLE-SYNC-EXCLUDE-VERIFICATION-2026-08-12.md`; final Terraform plan SHA-256 `2fe6fd3eeeea72b703d27d10bba2cf5b0fcbdc27933ee2fb2857030ecab0edaa` reported 189 no-op and zero non-no-op actions, and the current bundle aggregate `49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027` returned `Validation OK!`. |
| Goal 5 MVP — Structured + Unstructured + CDC synthetic ingestion | VERIFIED — APPROVED DELTA UNIFORM ICEBERG-COMPATIBILITY PROFILE | Evidence commit `9c0d67b30db96a24d015c9cb79821b2fbb107f23` contains the reviewed typed ingestion framework, Terraform/bundle configuration, neutral fixtures, tests, runbooks, and all durable Goal 5 verification reports. | [Final verification](verification/GOAL-05-FINAL-VERIFICATION-2026-08-13.md), committed at `9c0d67b30db96a24d015c9cb79821b2fbb107f23`, maps all 44 criteria. Final plan SHA-256 `d2d57ef74c713f3e83349b225a87c48a2d2e7ac1cbbc4c3898c59f4ebcd0d6f1` exited `0` with `No changes`; all nine tables are accurately recorded as Unity Catalog managed Delta UniForm Iceberg interoperability, not native Iceberg. |

## Current next checkpoint

Goal 3 is complete: Goal 3A and Goal 3B are `VERIFIED` against immutable commit
`634c67104d67e17d3bcd9747acbdbdc8ffc928a3`.

Goal 4 is `VERIFIED` against immutable evidence commit
`a778cfdfceaf6c704f98d83752c54c73a7d9208f` under the approved project
Iceberg-compatibility profile. The authoritative Tables API inventory proves
that all seven live synthetic tables are managed Delta UniForm with
Iceberg-compatible metadata in approved S3. The approved project profile
retains these identities and does not execute the destructive drop/recreate
remediation; native Iceberg is no longer planned or required. The revised
acceptance profile and evidence are documented in
`docs/verification/GOAL-04-NATIVE-ICEBERG-FORMAT-BLOCKER-2026-08-11.md`.

The sync.exclude deployment checkpoint is complete and recorded in
`docs/verification/GOAL-04-BUNDLE-SYNC-EXCLUDE-VERIFICATION-2026-08-12.md`.
The connected identity/resource inspection, grant remediation, final
zero-drift plan, strict bundle validation, and durable evidence commit are
complete. No table drop/recreate is required.

Goal 5 is `VERIFIED` against immutable evidence commit
`9c0d67b30db96a24d015c9cb79821b2fbb107f23` under the approved Delta UniForm
Iceberg-compatibility profile. Goal 5 technical acceptance is complete.
The final saved development Terraform plan used transient
`goal_5_source_objects_enabled=true`, has SHA-256
`d2d57ef74c713f3e83349b225a87c48a2d2e7ac1cbbc4c3898c59f4ebcd0d6f1`, exited
`0`, and reported `No changes`. It caused no apply, destroy, bundle deployment,
job/SQL execution, AWS mutation, or Databricks mutation. The final evidence
matrix is `docs/verification/GOAL-05-FINAL-VERIFICATION-2026-08-13.md`; it
records the successful all-task workflow `172279846311777`, S3 preservation,
nine authoritative managed Delta UniForm Iceberg-compatible tables, Goal 4
health, scope controls, and cost controls. The explicit Delta UniForm/native
Iceberg distinction is retained.

Goal 5 IMPLEMENTED: synthetic structured CSV ingestion; minimal Markdown/TXT
document metadata ingestion; deterministic synthetic CDC INSERT/UPDATE/DELETE
semantics; typed contract validation; provenance; basic data quality;
idempotency; auditable ingestion runs; and Unity Catalog managed Delta UniForm
Iceberg-compatible lakehouse output.

Goal 5 DEFERRED: real database connectors; production CDC; Debezium;
Kafka/MSK/Kinesis; REST ingestion; production streaming; PDF/OCR; document
chunking; embeddings; OpenSearch indexing; generalized replay/backfill;
advanced schema evolution; and advanced watermark management. Those are not
production-readiness claims and do not form Goal 5 MVP acceptance criteria.

No further Goal 5 connected operation is required or authorized. The next
roadmap checkpoint is Goal 6 only after a separately approved goal request;
the existing Goal 5 evidence does not authorize it.

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
