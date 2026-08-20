# Project status

This file is a checkpoint index, not evidence by assertion. `VERIFIED` is
allowed only when the row identifies the exact reviewed commit and durable
verification evidence. A plan or implementation commit alone is not
verification.

## Current snapshot

- Goal 6 — Apache Doris serving layer is **VERIFIED** across FE/BE readiness, governed refresh, result contract, RBAC, query limits, audit, increment, rebuild, post-rebuild comparison, and final zero-drift. Immutable evidence commit: `d1bd8783dfe308db8d0165503ac06c31b043bd98`. Phase 6-0 read-only
  preflight completed on `2026-08-13` and is recorded in
  `docs/verification/GOAL-06-PHASE-6-0-PREFLIGHT-2026-08-13.md`. It
  reverified the approved development account `736956442295`, region
  `ap-southeast-1`, workspace `7474644358733471`, and attached metastore
  `3a7f7e7a-680b-4bd6-907a-6d5e77b43178`. The metastore has external access
  enabled. The nine Goal 5 sources remain managed Delta UniForm with
  Iceberg-compatible metadata and direct-external-engine-read capability; they
  are not native Iceberg. The approved saved foundation plan was applied on
  `2026-08-13` but stopped with partial Terraform-state ownership. The durable
  inventory is
  `docs/verification/GOAL-06-PHASE-6-5-PARTIAL-APPLY-2026-08-13.md`: both
  private instances and both data-volume attachments are now state-owned. The
  separately generated reconciliation plan
  (`318a8b1d8b7693d002e8019c3db82fdca2ee7abe93473112a0e20f056da54481`)
  was a 245-resource no-op, so it was not applied. Both instances are
  cost-bearing, EC2 system/instance checks are `ok`, and no public IP or public
  database/admin ingress exists. At the initial foundation checkpoint, the
  BE's 8 GiB encrypted root volume ran out of space while Docker unpacked the
  pinned Doris image; the root-bootstrap remediation below corrected that
  condition. The FE has no CloudWatch Doris log stream yet, so Doris remains
  not application-verified. The scanned private ECR image and Goal 6 ECS task
  definitions now exist; revision-2 registration and the no-running-task
  inspection are recorded below. The existing Goal 3B private Fargate
  smoke mechanism is intentionally not reusable as a Doris verifier. The
  approved Phase 6-1 design is
  `docs/plans/GOAL-06-APACHE-DORIS-SERVING-LAYER-PLAN.md`: self-hosted Doris
  `4.0.1`, one private EC2 FE plus one private EC2 BE with encrypted EBS, and
  a separate Terraform-managed ephemeral Fargate verifier. Phase 6-2 source
  implementation is recorded in
  `docs/verification/GOAL-06-PHASE-6-2-OFFLINE-IMPLEMENTATION-2026-08-13.md`.
  Its Terraform/static, full Python test/coverage, lint/type/security, local
  Docker build, TFLint, and Trivy gates passed. Direct `uv` pre-commit
  orchestration and locked dependency audit remain **UNVERIFIED** because the
  host's checked-in virtual environment is stale and a temporary `uv` install
  stopped on a hash mismatch that was not bypassed. Current checkpoint:
  A prior approved saved foundation-plan attempt stopped before approval because
  the ignored Goal 5 source-object gate was unset (three existing source objects
  would have been deleted) and an unknown Databricks service-principal ID was
  used as a Terraform resource-count gate. The offline remediation retains those
  source objects locally and uses the known `goal_6_enabled` Boolean for the
  grant gate; it is recorded in
  `docs/verification/GOAL-06-PHASE-6-4-FOUNDATION-PLAN-BLOCKER-REMEDIATION-2026-08-13.md`.
  The reviewed remediation uses a source-level `AVD-AWS-0104` Trivy annotation
  scoped only to the FE/BE HTTPS egress resource, with static regression
  coverage of its private-NAT rationale. The re-run offline validation is
  recorded in
  `docs/verification/GOAL-06-PHASE-6-4-FOUNDATION-PLAN-BLOCKER-REMEDIATION-2026-08-13.md`.
  The saved connected development foundation plan is recorded in
  `docs/verification/GOAL-06-PHASE-6-4-CONNECTED-PLAN-2026-08-13.md`. It has
  47 creates, 3 in-place updates, no replacement, no destroy, no Goal 6 ECS
  task definition, and no metastore, workspace assignment, warehouse, or
  production change. The plan retained all three Goal 5 source objects. The
  exact apply was approved and attempted. The approved offline remediation
  introduced three import blocks, but its connected plan was a no-op because
  state ownership had already converged. The approved minimal Terraform-managed
  bootstrap remediation now declares 30 GiB encrypted root storage for both
  hosts and an explicit BE-only generation-2 replacement trigger; it preserves
  the BE serving-data volume, IAM/KMS, network, and topology. Its offline
  evidence is
  `docs/verification/GOAL-06-PHASE-6-5-ROOT-BOOTSTRAP-REMEDIATION-OFFLINE-2026-08-13.md`:
  Terraform/static, 137-test/97.16%-coverage, targeted mypy, lint/security,
  TFLint, and Trivy gates passed; repository-wide mypy remains unverified due
  to 61 existing Goal 5/platform-test diagnostics. No further Terraform, AWS,
  Databricks, ECR, ECS, SQL, or bundle mutation is authorized until its
  separate saved connected change set is reviewed. The reviewed saved remediation
  artifact is
  `goal-06-root-bootstrap-remediation-20260813.tfplan` with SHA-256
  `81943eb2c58097e074b87f96d57b736767e9ab105c9b8997d3eb7576a28bfe30`.
  Its evidence is
  `docs/verification/GOAL-06-PHASE-6-5-ROOT-BOOTSTRAP-REMEDIATION-CONNECTED-PLAN-2026-08-13.md`.
  It contains exactly one FE root-volume update (`8 → 30 GiB`), one intended
  BE replacement due only to the explicit bootstrap generation, and one
  replacement of the BE attachment that reuses the same 50 GiB serving-data
  volume; all other 242 resources are no-op. It has no Databricks, IAM/KMS,
  network, public-exposure, source-data, ECS/ECR, production, destroy-only, or
  unexpected replacement action. The hash-bound apply completed on `2026-08-13`.
  It retained FE `i-074e456efa350b444`, created replacement BE
  `i-0118ff6e619268859`, terminated only the old BE
  `i-05b409f7992294844`, expanded both roots to 30 GiB, and reattached the
  same encrypted 50 GiB BE data volume `vol-01e9b0ed05f7b92b9` at `/dev/sdf`.
  Both current instances have passing EC2 platform checks and no public IP.
  Replacement BE cloud-init mounted/recovered the data volume, pulled the
  digest-pinned image, started a Docker container, and completed without the
  previous root-space error. Application health remains UNVERIFIED because no
  Doris CloudWatch stream, private verifier task, or SQL operation has run.
  Durable evidence is
  `docs/verification/GOAL-06-PHASE-6-5-ROOT-BOOTSTRAP-REMEDIATION-APPLY-2026-08-13.md`.
  The subsequent local verifier-image build passed for aggregate source SHA-256
  `ac041bb3aaea7266adf4006f73544c4f1e48abb7ca88c7c71931eaae973838e7`,
  producing local digest
  `sha256:167912392ef3276123ec32b021083bd1b7dec02e12af12730cd702ad7143bea6`.
  Its image vulnerability scan is **PASS**: after Docker bridge DNS prevented
  initial DB download, a host-networked temporary scanner downloaded the DB and
  Trivy `0.69.3` found zero HIGH/CRITICAL vulnerabilities. Following a
  hash-bound approval, the immutable tag `goal6-ac041bb3a` was pushed to the
  Terraform-created private ECR repository and immediate inspection confirmed
  the same local/remote OCI digest. The separately approved connected saved
  task-definition plan was applied as exactly two ECS task-definition creates,
  zero other AWS/Databricks, replacement, destroy, public-exposure, or
  production actions, and no task run. Immediate inspection confirms both
  revision-1 definitions are private Fargate definitions using the exact
  scanned digest, and no Doris ECS task is running. Pre-run source review then
  found a double-`https://` workspace-origin bug in the admin runner, so no
  task may be launched until a reviewed offline remediation produces a new
  scanned image and replacement task definitions. The approved offline
  remediation is now implemented: it normalizes one trailing slash, accepts
  only a single HTTPS Databricks workspace origin, composes OAuth/REST paths
  from that origin, and fails closed before secret parsing or network access on
  invalid input. Static, shell, local image-build, and Trivy image-scan
  validation pass; focused pytest remains unverified because the stale
  checked-in virtual environment cannot execute and no dependency bypass was
  used. Following hash-bound approval, the new scanned image was pushed to the
  immutable private ECR tag `goal6-workspace-origin-ef83572c` and remote digest
  inspection matched exactly. The separately approved saved plan
  `ffca04bb20e5fa81d34704b57e2b33ea16dec61241d4a9b615df330109967f13`
  then registered both private Fargate revision-2 task definitions with that
  digest. Terraform reports this registration as two state replacements
  (`2 added, 0 changed, 2 destroyed`); no ECS task, service, IAM, KMS, network,
  security-group, ECR, Databricks, or S3 change occurred. Immediate read-only
  inspection confirms both revision-2 definitions are ACTIVE, remain `awsvpc`
  Fargate (`512` CPU / `1024` MiB), and use the exact immutable digest; the
  cluster has no RUNNING task. The dedicated Goal 6 RunTask wrapper is now
  implemented and statically validated at
  `infrastructure/scripts/run-goal6-admin-refresh.ps1`; the existing Goal 3B
  smoke wrapper remains restricted to its three smoke definitions and is not
  reused. One approved private admin-refresh attempt was made once; it reached
  `STOPPED` with `TaskFailedToStart` because ECS could not retrieve the admin
  secret from Secrets Manager over the private task network. The container did
  not start, no retry was made, and CloudWatch returned no stream metadata.
  The host lacked a PowerShell runtime, so the wrapper guards were reproduced
  by read-only checks before the single control-plane launch; this is not
  treated as wrapper execution. That earlier checkpoint is superseded by the
  current readiness-marker apply checkpoint below. Evidence:
  `docs/verification/GOAL-06-VERIFIER-IMAGE-BUILD-SCAN-2026-08-13.md`.
  Plan evidence: `docs/verification/GOAL-06-PHASE-6-6-TASK-DEFINITIONS-CONNECTED-PLAN-2026-08-13.md`.
  Apply evidence: `docs/verification/GOAL-06-PHASE-6-6-TASK-DEFINITIONS-APPLY-2026-08-13.md`.
  Remediation evidence: `docs/verification/GOAL-06-WORKSPACE-ORIGIN-REMEDIATION-OFFLINE-2026-08-13.md`.
  Revision-2 apply evidence:
  `docs/verification/GOAL-06-WORKSPACE-ORIGIN-REMEDIATION-TASK-DEFINITIONS-APPLY-2026-08-13.md`.
  Wrapper evidence:
  `docs/verification/GOAL-06-PRIVATE-ADMIN-TASK-WRAPPER-OFFLINE-2026-08-13.md`.
  Task-run evidence:
  `docs/verification/GOAL-06-PRIVATE-ADMIN-TASK-RUN-2026-08-13.md`.
  The prior
  offline remediation introduced three `goal_6_enabled`-gated Terraform import
  blocks for the then-unmanaged FE and two volume attachments, recorded in
  `docs/verification/GOAL-06-PHASE-6-5-RECONCILIATION-OFFLINE-2026-08-13.md`.
  Its Terraform/static, 136-test/97.16%-coverage, lint/type/security, TFLint,
  and Trivy gates passed.
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

Goal 6 is currently `BLOCKED — FE/BE READINESS MARKERS FAILED; NO TASK RETRY`.
The self-hosted private Doris FE/BE foundation, encrypted storage, scanned
verifier image, and revision-3 ECS task definitions are deployed in
development. The single approved task attempt failed before container startup
because of a Secrets Manager network timeout. Read-only inspection proved the
existing interface-endpoint SG omits the Goal 6 admin SG, and the shared ECS
execution role lacks exact Secrets Manager/KMS secret-injection grants; route,
NACL, endpoint availability, and private DNS are healthy. The approved
offline remediation declares one Goal 6 admin-SG-to-interface-endpoint TCP/443
rule and one exact-ARN ECS execution-role Secrets Manager/KMS policy. Its saved
connected plan was reviewed as exactly `2 to add, 0 to change, 0 to destroy`,
with SHA-256
`2e84c69e612d0c229e7eb916a42c59cd0d475648278dfca104543d585405586a`, and the
user-approved apply completed as exactly `2 added, 0 changed, 0 destroyed`.
Read-only inspection confirmed the endpoint rule and exact execution-role
policy. The one approved post-remediation retry then stopped with container
exit code `7`; redacted CloudWatch evidence reports MariaDB `mysql: unknown
variable 'ssl-mode=REQUIRED'`. No retry followed. This is a verifier-image
client-option compatibility blocker. The approved offline remediation changed
all three runners to MariaDB-compatible `--ssl --protocol=TCP`, updated static
validation/regression coverage and documentation, and passed offline checks;
the replacement image was then built and scanned locally with source aggregate
`ab6bc4dceabf86134ac526707b592d1e95137076ecbf55343b12eabfcee5b142`, local
image ID `sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6`,
and zero HIGH/CRITICAL Trivy findings. The exact image was then pushed under
immutable tag `goal6-mariadb-ssl-ab6bc4d`, and read-only ECR inspection returned
the same digest. The separately approved saved task-definition plan
`7f4de065ecae0de13d97954bc97314306af7a09b50831c2cf85048ea00b39aa0` was then
applied as the expected two ECS task-definition revision replacements; no
other resource changed. One separately approved revision-3 private
admin-refresh task was then launched
exactly once. It reached `STOPPED` with container exit code `1` and no
completion marker. The private ENI was `10.42.35.84` in
`subnet-0a1aad220d82ef879`; sanitized CloudWatch output was `ERROR 2002
(HY000): Can't connect to server on '10.42.76.67' (115)`. No retry or repair
was performed. The separately approved read-only diagnosis then confirmed the
admin-to-FE SG peer rules, local VPC route, and NACL allow the path; VPC Flow
Logs show `ACCEPT` packets in both directions and no matching `REJECT`. The
FE/BE console output proves cloud-init completed and Docker pulled/launched
the pinned images, but no FE/BE application log stream exists. The blocker is
therefore narrowed to FE query-port listener/process unavailability. The
approved offline remediation now supplies the official FE/BE Docker discovery
variables (`FE_SERVERS`, `FE_ID`, and `BE_ADDR`), adds private listener
readiness guards, and introduces explicit FE generation `2` replacement
wiring. The new saved connected plan is
`goal-06-fe-listener-remediation-20260813.tfplan` with SHA-256
`90c504a9e54529d3d4d82e61088455573ab0d02d9ff287df47bc0b6ca7bf83a0`.
It contains 243 no-op resources and six delete/create replacements: FE and BE
instances, both metadata/serving-data attachments, and both Goal 6 ECS task
definitions whose private-host inputs become unknown during host replacement.
It has no standalone volume deletion, IAM/KMS, network, Databricks, ECR,
source-data, production, or public-exposure action. The exact plan was applied
successfully as `6 added, 0 changed, 6 destroyed`; FE `i-01415e2378d0e2ca8`
and BE `i-0e17d80269bc0f208` are running privately, the existing FE/BE data
volumes are reattached at `/dev/sdf`, and task-definition revision 4 is active.
  No Goal 6 task was running at the initial inspection. A separately approved
  revision-4 admin-refresh task then reached `STOPPED` with exit code `1` and
  no completion marker; private ENI `10.42.46.3` was healthy, but sanitized
  CloudWatch output again reported `ERROR 2002 (HY000): Can't connect to
  server on '10.42.78.72' (115)`. No retry followed. Doris health, Unity
Catalog interoperability, serving refresh, rebuild, and read-only verification
remain `UNVERIFIED`. Details are in
`docs/verification/GOAL-06-SECRET-ENDPOINT-EXECUTION-ROLE-REMEDIATION-OFFLINE-2026-08-13.md`
,
`docs/verification/GOAL-06-SECRET-ENDPOINT-EXECUTION-ROLE-REMEDIATION-APPLY-2026-08-13.md`,
and
`docs/verification/GOAL-06-SECRET-ENDPOINT-EXECUTION-ROLE-CONNECTED-PLAN-2026-08-13.md`,
and
`docs/verification/GOAL-06-PRIVATE-ADMIN-TASK-RETRY-2026-08-13.md`.
The remediation evidence is
`docs/verification/GOAL-06-MARIADB-TLS-OPTION-REMEDIATION-OFFLINE-2026-08-13.md`.
The local image evidence is
`docs/verification/GOAL-06-MARIADB-TLS-IMAGE-BUILD-SCAN-2026-08-13.md`.
The ECR push evidence is
`docs/verification/GOAL-06-MARIADB-TLS-IMAGE-PUSH-2026-08-13.md`.
The saved task-definition plan evidence is
`docs/verification/GOAL-06-MARIADB-TLS-TASK-DEFINITIONS-CONNECTED-PLAN-2026-08-13.md`.
The task-definition apply evidence is
`docs/verification/GOAL-06-MARIADB-TLS-TASK-DEFINITIONS-APPLY-2026-08-13.md`.
The failed revision-3 task evidence is
`docs/verification/GOAL-06-PRIVATE-ADMIN-TASK-REVISION-3-2026-08-13.md`.
The offline FE listener remediation evidence is
`docs/verification/GOAL-06-FE-LISTENER-REMEDIATION-OFFLINE-2026-08-13.md`.
The saved connected-plan evidence is
`docs/verification/GOAL-06-FE-LISTENER-REMEDIATION-CONNECTED-PLAN-2026-08-13.md`.
The apply and immediate inspection evidence is
`docs/verification/GOAL-06-FE-LISTENER-REMEDIATION-APPLY-2026-08-13.md`.
The revision-4 task evidence is
`docs/verification/GOAL-06-PRIVATE-ADMIN-TASK-REVISION-4-2026-08-13.md`.
The follow-up offline readiness-marker remediation evidence is
`docs/verification/GOAL-06-FE-READINESS-MARKER-REMEDIATION-OFFLINE-2026-08-13.md`.
The saved connected plan was then created and reviewed without mutation. It is
`goal-06-fe-readiness-marker-remediation-20260813.tfplan` with SHA-256
`07a9efc1f932b2eabc48216aef89cc476f0f6cfbc582a5a3d83b13b69f5349a6`. It
contains 243 no-op resources and exactly six delete/create replacements: the
FE and BE instances, their two volume attachments, and the two Goal 6 task
definitions whose private-host inputs propagate during host replacement. No
IAM/KMS/network/S3/ECR/Databricks/production/public-exposure action is present.
The durable plan evidence is
`docs/verification/GOAL-06-FE-READINESS-MARKER-REMEDIATION-CONNECTED-PLAN-2026-08-13.md`.
A separate approval is required before applying this exact saved plan.
The exact plan was subsequently approved and applied successfully as `6 added,
0 changed, 6 destroyed`. New private FE `i-0fe26c51fd499b7de`
(`10.42.64.238`) and BE `i-07d1e1eddfec1c9eb` (`10.42.71.97`) were created;
the existing encrypted role volumes remain attached at `/dev/sdf`, and admin
and verifier task definitions are active at revision 5. Immediate inspection
found no running Goal 6 task and both EC2 health checks eventually became
`ok/ok`. The persisted console markers then showed `doris-port-unavailable`
for FE `9030` and BE `9050`; neither host reached `doris-port-ready`, and no
CloudWatch marker stream appeared. No task was launched or retried. Apply evidence:
`docs/verification/GOAL-06-FE-READINESS-MARKER-REMEDIATION-APPLY-2026-08-13.md`.

The approved offline listener diagnosis/remediation is recorded in
`docs/verification/GOAL-06-DORIS-LISTENER-DIAGNOSIS-OFFLINE-2026-08-14.md`.
It adds the documented Doris host prerequisites (`vm.max_map_count=2000000`
and `nofile=1000000`), an explicit Docker ulimit, and bounded redacted
container diagnostics. Goal 6 static validation, all 17 manual static
regression tests, rendered FE/BE `bash -n`, Python compilation, and
`git diff --check` pass. Terraform, pytest/coverage, Ruff, mypy, Bandit,
detect-secrets, TFLint, and Trivy remain unverified. Terraform v1.15.8 was
restored from the local `/tmp` cache; source formatting and
`init -backend=false` with a local provider mirror pass. Running the provider
schema checks in the offline runtime also passes `validate` and all seven
Terraform mock-provider tests. No connected operation occurred. A new saved
connected plan is the next boundary; no task launch is allowed until both
hosts emit `doris-port-ready`.

The saved connected plan for the host-prerequisite remediation was created and
reviewed read-only on `2026-08-14`. Its artifact is
`goal-06-doris-listener-host-prereq-remediation-20260814.tfplan` with SHA-256
`bbe5e504b136fd639995c033d90afecf3a557fb430dbd3a1f194f29e5b7a0bbd`.
It contains exactly six reviewed replacements (FE/BE `user_data`, their
volume attachments, and the two propagated ECS task definitions), 243
no-op resources, zero in-place changes, and no IAM/KMS/network/S3/ECR/
Databricks/production/public-exposure action. The durable review is
`docs/verification/GOAL-06-DORIS-LISTENER-HOST-PREREQ-CONNECTED-PLAN-2026-08-14.md`.
A separate hash-bound apply approval is required; no task launch is authorized
until both hosts emit `doris-port-ready`.

The exact plan was subsequently approved and applied on `2026-08-14` as
`6 added, 0 changed, 6 destroyed`. New private FE
`i-0ad90219f868841f7` (`10.42.69.177`) and BE
`i-0dc0e8f4f71d1876e` (`10.42.77.49`) replaced the prior hosts; the existing
encrypted 20 GiB and 50 GiB role volumes remain attached at `/dev/sdf`, and
both Goal 6 task definitions are active at revision 6. EC2 checks are `ok/ok`
and no Goal 6 task is running. Both hosts emitted `host-prerequisites-ready`
and pulled their pinned Doris images, but both later emitted
`doris-port-unavailable` (`9030`/`9050`) and cloud-init `scripts-user` failed.
No `doris-port-ready` marker or host log stream exists. No task was launched or
retried. Durable apply evidence is
`docs/verification/GOAL-06-DORIS-LISTENER-HOST-PREREQ-APPLY-2026-08-14.md`.
Goal 6 remains blocked at Doris application readiness.

An approved offline remediation now adds Terraform-managed stable private-IP
inputs for the persisted Doris pair (`10.42.69.177` FE and `10.42.77.49` BE),
validates both addresses against the selected data-subnet CIDR, and records a
fail-closed host diagnostic when the observed address differs. Terraform
v1.15.8 does not support `cidrcontains`; the source now uses deterministic
nested `range`/`cidrhost` enumeration for the approved `/20` subnet and
`contains` assertions, with a non-`/20` subnet failing closed. The first
connected plan artifact (`98b54e3ed06c1b80cf8c797325e1e334bd85889d71d689906969ad97ee29b8ee`)
stopped before any managed action because of that unsupported function; it is
not applyable. The correction changes no AWS/Databricks state and does not
reset either encrypted role volume or run a task. Offline evidence is
`docs/verification/GOAL-06-DORIS-STABLE-PRIVATE-IP-OFFLINE-2026-08-14.md`;
static/source validation, Terraform formatting, backend-disabled provider
validation, and the seven Terraform mock-provider tests are PASS after
Terraform was installed and run from the local provider cache. The Goal 6
  static/regression pytest subset now passes 18 tests. The repository-wide
  platform-foundation suite, its `pydantic` dependency, and all
  Pydantic-dependent checks are explicitly excluded from Goal 6 acceptance;
  they remain a separate Goal 2 development concern and do not block Doris
  verification. Ignored development tfvars explicitly carry the observed
values without becoming tracked. The saved connected plan is now created and
reviewed as `goal-06-doris-private-ip-remediation-20260814.tfplan`, SHA-256
`5e1cf1ae3be48d2565635da4cd1d73bbb14e3addd90d4ce71ff93511c55729d1`. It has
exactly four expected replacements (FE/BE instances and their existing `/dev/sdf`
attachments), zero other actions, and no managed mutation. Durable review is
`docs/verification/GOAL-06-DORIS-STABLE-PRIVATE-IP-CONNECTED-PLAN-2026-08-14.md`.
The exact hash-bound apply completed successfully on `2026-08-14` as
`4 added, 0 changed, 4 destroyed`. New FE `i-0ce389278aecaf8a6` and BE
`i-07c6ec23f7cb40476` are running at the approved private IPs
`10.42.69.177` and `10.42.77.49` in `subnet-09bc95f43115dca3e`, with no public
IP. The existing encrypted role volumes remain attached at `/dev/sdf`:
`vol-012bc3410278ed85e` (FE) and `vol-01e9b0ed05f7b92b9` (BE). Immediate
read-only inspection confirmed the expected instance, health, and attachment
states; no task or other Goal 6 operation was run. FE emitted
`doris-port-ready` on 9030. BE later emitted `doris-port-unavailable` on 9050
and cloud-init reported `scripts-user` failure, so the checkpoint remains
`BLOCKED` pending a reviewed declarative remediation. Durable apply evidence is
`docs/verification/GOAL-06-DORIS-LISTENER-DIAGNOSTICS-APPLY-2026-08-14.md`.

Post-apply read-only console inspection now provides the current failure
evidence: the new FE reached `doris-port-ready` on 9030, while the new BE
`i-07c6ec23f7cb40476` later emitted `doris-port-unavailable` on 9050 and
cloud-init reported `scripts-user` failure. No FE/BE host CloudWatch stream
appeared, so encrypted-volume container diagnostics are not independently
observable through the current log-delivery path. EC2 platform checks remain
`ok/ok`, the private IPs and `/dev/sdf` attachments are correct, and no Goal 6
task was launched or retried. Durable diagnosis is
`docs/verification/GOAL-06-DORIS-LISTENER-POST-DIAGNOSTICS-2026-08-14.md`.
The offline persisted-IP remediation is implemented and validated in
`docs/verification/GOAL-06-DORIS-PERSISTED-IP-OFFLINE-REMEDIATION-PLAN-2026-08-14.md`:
the untracked development input contract now uses `10.42.64.238` (FE) and
`10.42.71.97` (BE), with Goal 6 static validation, 18 pytest tests, Terraform
validation, and seven mock-provider tests passing. The saved connected plan
for this remediation is
`goal-06-doris-persisted-ip-remediation-20260814.tfplan`, SHA-256
`c7d1368001470bff744d38eb50e6dfb77e6b1f40a7a1a10a1d70c33112cca83e`; it has
exactly six replacements (`6 added, 0 changed, 6 destroyed`) for FE/BE
instances, their volume attachments, and the two task-definition revisions
whose host values change. It has no other action. Durable review is
`docs/verification/GOAL-06-DORIS-PERSISTED-IP-CONNECTED-PLAN-2026-08-14.md`.
No apply, task, SQL/job, bundle, or other mutation has occurred for this
remediation. The next boundary is separate hash-bound approval to apply this
exact plan; no volume reset or task run is authorized.
Goal 6 remains `BLOCKED` at the Doris application listener; the offline-only
declarative diagnostics/startup remediation is now implemented and validated
in
`docs/verification/GOAL-06-DORIS-LISTENER-DIAGNOSTICS-OFFLINE-2026-08-14.md`.
It preserves the image default FE/BE configs through custom overlays, bounds
Docker launch, and uses deterministic diagnostic log paths. The saved connected
plan was applied as
`goal-06-doris-listener-diagnostics-remediation-20260814.tfplan`, with SHA-256
`8f8c674bce1fe23141c7aedf376c93e484c0fc3d1a2f3a2d571c584c72285cd6` with
exactly four reviewed replacements (FE/BE `user_data` and their existing
`/dev/sdf` attachment instance IDs), zero in-place changes, zero unrelated
actions, and no task definition change. Durable plan evidence is
`docs/verification/GOAL-06-DORIS-LISTENER-DIAGNOSTICS-CONNECTED-PLAN-2026-08-14.md`.
The apply completed with `4 added, 0 changed, 4 destroyed`; FE reached
`doris-port-ready`, while BE later failed its listener guard. Durable apply
evidence is
`docs/verification/GOAL-06-DORIS-LISTENER-DIAGNOSTICS-APPLY-2026-08-14.md`.
The persisted-IP remediation was then explicitly approved and applied from the
exact saved plan above as `6 added, 0 changed, 6 destroyed`. New FE
`i-0086c691d5d975ba0` (`10.42.64.238`) and BE `i-029fd9a3bed8fe2e7`
(`10.42.71.97`) are running privately; the existing encrypted role volumes
remain attached at `/dev/sdf`, and the admin/verifier task definitions are
ACTIVE at revision 7 with the new host values. The old instances were
terminated and no data volume was deleted. The first immediate snapshot showed
checks `initializing`; a later single read-only snapshot shows both checks
`ok/ok` and both hosts emit `host-prerequisites-ready`, but neither emits a
durable `doris-port-ready` marker. Listener readiness therefore remains
**UNVERIFIED**. No verifier task was launched or retried. Durable apply evidence is
`docs/verification/GOAL-06-DORIS-PERSISTED-IP-APPLY-2026-08-14.md`. Goal 6
remains `BLOCKED` until both Doris listeners and all later acceptance phases
are verified.

The current remediation checkpoint remains `BLOCKED` at Doris listener
readiness. A new offline-only bootstrap change adds the safe
`container-diagnostics-summary` status record so launch state, exit code, and
listener state remain observable even when raw container log delivery is
delayed. Raw logs stay redacted and encrypted-volume-only. Offline evidence is
`docs/verification/GOAL-06-DORIS-PORT-DIAGNOSTICS-OFFLINE-2026-08-14.md`.
No connected plan/apply, AWS/Databricks mutation, ECS task, SQL/job, bundle
operation, ECR operation, volume reset, or metadata deletion has occurred for
this checkpoint. The next boundary is a separately reviewed saved connected
Terraform plan restricted to FE/BE bootstrap replacement and then a separate
hash-bound apply approval.

The saved connected diagnostics plan is now available at
`infrastructure/environments/development/goal-06-doris-port-diagnostics-20260814.tfplan`
with SHA-256
`0ea48ac9cf50a38a6b83879b5419ed58798528231fb77acba040c9b6e99db86b`.
Read-only plan review reports exactly four replacements (`4 added, 0 changed,
4 destroyed`): FE/BE instances for the new bootstrap user-data and their two
existing volume attachments following the instance IDs. It contains no data
volume deletion, IAM/KMS/network/S3/ECR/Databricks/task/public/production
action. Durable evidence is
`docs/verification/GOAL-06-DORIS-PORT-DIAGNOSTICS-CONNECTED-PLAN-2026-08-14.md`.
The plan has not been applied; Goal 6 remains `BLOCKED` pending separate
hash-bound approval.

The exact approved plan was subsequently applied successfully as `4 added, 0
changed, 4 destroyed`. New FE `i-0c8d9d95e7d635a21` (`10.42.64.238`) and BE
`i-03a9c64f31b368055` (`10.42.71.97`) are private, healthy `ok/ok`, and the
existing encrypted FE/BE serving volumes remain attached at `/dev/sdf` with
`DeleteOnTermination=false`. Both task definitions remain ACTIVE at revision
7 and no Goal 6 task is running. The new diagnostic summary proves both
containers remain running with exit code 0 and no Docker-reported error, but
both listener guards ended with `doris-port-unavailable` (9030/9050) after
their bounded windows. Durable apply evidence is
`docs/verification/GOAL-06-DORIS-PORT-DIAGNOSTICS-APPLY-2026-08-14.md`.
Goal 6 remains `BLOCKED` at Doris application readiness; no volume reset or
metadata deletion is authorized by this result.

An additional offline-only diagnostic improvement now classifies redacted
container-log signals as `bind`, `metadata`, `configuration`, `exception`,
`other`, or `none`, without exposing raw logs. Offline evidence is
`docs/verification/GOAL-06-DORIS-LOG-SIGNAL-OFFLINE-2026-08-14.md`; static
validation and 18 regression tests pass. This source change has not been
planned or applied to AWS. A new saved plan and separate approval are required
before it can be deployed. Goal 6 remains `BLOCKED` and no task may run until
both listeners emit `doris-port-ready`.

The offline log-signal source change has a new saved connected development
plan at
`infrastructure/environments/development/goal-06-doris-log-signal-20260814.tfplan`
with SHA-256
`52ec78fc93cc6ada79ed2404a9a04433785022c70817b6b3585738a160f970b0`.
The plan contains exactly four replacements (`4 added, 0 changed, 4
destroyed`) for the two FE/BE instances and their existing volume attachments,
with zero volume-resource deletion and zero unrelated/IAM/KMS/network/task/
public/production actions. Durable review is
`docs/verification/GOAL-06-DORIS-LOG-SIGNAL-CONNECTED-PLAN-2026-08-14.md`.
It is awaiting a separate exact-plan approval and has not been applied.

The exact log-signal plan was then applied with `4 added, 0 changed, 4
destroyed`. New FE `i-0fd40482113ec99a0` and BE `i-0cc6353584df5a9d4` remain on
the approved private IPs; the two encrypted serving volumes remain attached
without delete-on-termination. Both containers run to the end of the guard,
but FE terminates with `log_signal=metadata` and `doris-port-unavailable` on
9030, while BE terminates with `log_signal=configuration` and
`doris-port-unavailable` on 9050. Durable evidence is
`docs/verification/GOAL-06-DORIS-LOG-SIGNAL-APPLY-2026-08-14.md`.
This is evidence for a persisted-metadata/configuration blocker, not an
authorization to rebuild or delete either volume. Goal 6 remains `BLOCKED`;
no task or retry may run until both listeners are ready.

The approved offline follow-up now adds a default-off
`goal_6_rebuild_serving_state` Terraform gate for a disposable serving-state
rebuild. It creates fresh encrypted FE/BE data volumes only when explicitly
enabled, protects the old Terraform-managed volumes with `prevent_destroy`,
and leaves them detached for later review. It does not use Doris metadata
recovery, format/delete volumes, launch tasks, or mutate AWS. Offline evidence
is `docs/verification/GOAL-06-DORIS-SERVING-STATE-REBUILD-OFFLINE-2026-08-14.md`.
A new saved connected plan and separate hash-bound approval are required;
Goal 6 remains `BLOCKED` until both new hosts emit `doris-port-ready`.

The saved connected serving-state rebuild plan was created read-only with CLI
input `goal_6_rebuild_serving_state=true`. Its artifact was
`goal-06-doris-serving-state-rebuild-20260814.tfplan`, SHA-256
`ce05eb8cd3b1a90b3c80b424bdae8bf99bc6a909e9a7e55dd27b3cd0c976da6c`. It had
exactly two new encrypted EBS volume creates, two FE/BE instance replacements,
and two volume-attachment replacements; it had zero old-volume deletes,
zero updates, and zero unrelated IAM/KMS/network/S3/ECR/Databricks/task/
production/public-exposure actions. The exact artifact was subsequently
approved and applied with `6 added, 0 changed, 4 destroyed`. The new FE/BE
hosts use the approved private IPs and fresh encrypted 20/50 GiB data volumes;
the old data volumes remain detached and preserved. Durable apply evidence is
`docs/verification/GOAL-06-DORIS-SERVING-STATE-REBUILD-APPLY-2026-08-14.md`.
FE readiness is evidenced, but BE's bounded guard now reports
`listener_state=unavailable` with `doris-port-unavailable` on 9050 and
`log_signal=configuration`; cloud-init reports the expected scripts-user
failure from that non-zero bootstrap result. Goal 6 remains `BLOCKED` and no
task or cleanup may run.
The failure occurred with a newly created empty BE serving-state volume, so
the prior-volume metadata hypothesis is not sufficient; the next remediation
must address the declarative BE entrypoint/configuration/FE-registration path,
not perform another implicit volume reset.

The current offline bootstrap-marker remediation adds an early root/console
`bootstrap-invoked` marker and an EXIT-trap `bootstrap-failed` marker before
volume, package, Docker, or CloudWatch-agent setup. Once available, the
CloudWatch agent also collects `/var/log/goal6-doris-bootstrap.log` through a
dedicated `{instance_id}/<role>/bootstrap-root` stream. This change is
diagnostic only: it does not assert listener readiness, create a task, alter a
volume, or perform AWS mutation. Offline evidence is
`docs/verification/GOAL-06-BOOTSTRAP-MARKER-OFFLINE-2026-08-17.md`; Goal 6
remains `BLOCKED` pending a new exact saved connected plan and separate
approval before any FE/BE replacement. Offline static validation and 19
targeted regression tests pass; the Make wrapper was not runnable because
`uv` is not installed, while its underlying Goal 6 validator passed directly.

Offline review on `2026-08-17` then identified a deterministic private
FE/BE security-group contract defect. The saved rebuild plan proves that both
host groups had only HTTPS `443` egress, while Doris BE must initiate FE
membership inspection/registration through FE `9030` and FE must initiate
heartbeat/RPC traffic to BE `9050`, `9060`, and `8060`. Source now adds the
five missing private SG-to-SG rules and regression coverage. The ignored
development tfvars explicitly retains `goal_6_rebuild_serving_state = true`
to preserve the fresh rebuild volumes and prevent a plan from selecting the
old detached volumes. BE bootstrap now also waits through a bounded,
credential-free private TCP probe for FE `9030` before launching its container,
eliminating the concurrent first-boot registration race and recording an
explicit ready/unavailable marker. This is offline remediation only: no connected plan,
apply, instance replacement, SG mutation, ECS task, or SQL operation has run.
The official branch-4.0 BE image source confirms that its entrypoint connects
to FE `9030` for inspection/registration before starting the BE process; this
accounts for a running container with no `9050` listener when that path is
blocked. The earlier `log_signal=configuration` value remains only a broad
classifier and is not treated as root-cause proof.
Goal 6 remains `BLOCKED`; the next boundary is a saved connected plan with
zero EBS volume delete/replace actions, followed by separate hash-bound apply
approval and durable `doris-port-ready` evidence from both hosts.

The separately approved connected plan checkpoint completed on `2026-08-17`.
AWS identity/account/region and Databricks workspace authentication were
reverified immediately before Terraform refreshed the development state. The
saved plan
`goal-06-doris-intra-cluster-connectivity-20260817.tfplan`, SHA-256
`9697f83adeced4944cc9011d7b8b39a8c675d42cfffd7859430e3ba4ecafbb7e`, is
exactly `9 to add, 0 to change, 4 to destroy`: five private SG-to-SG rule
creates, replacement of only the FE/BE EC2 hosts, and replacement of their two
attachments to reattach the same fresh data volumes. Filtered plan JSON proves
zero `aws_ebs_volume`, IAM, KMS, task-definition, Databricks, public-exposure,
production, old-volume, or unexpected action. Durable evidence is
`docs/verification/GOAL-06-DORIS-INTRA-CLUSTER-CONNECTIVITY-CONNECTED-PLAN-2026-08-17.md`.
Goal 6 is now `AWAITING APPROVAL` for the exact saved-plan apply; no apply,
instance replacement, SG mutation, ECS task, or SQL operation has run.

The exact saved plan was separately approved and applied on `2026-08-17` after
its SHA-256, AWS identity/account/region, and Databricks development identity
were reverified. Terraform completed as `9 added, 0 changed, 4 destroyed` with
only the reviewed five private SG-to-SG rules, two FE/BE EC2 replacements, and
two attachment replacements. New FE `i-0d7b971ba56dc2395`
(`10.42.64.238`) and BE `i-0dd28df1b1b2c7923` (`10.42.71.97`) are private,
running, and `ok/ok`. The same encrypted fresh data volumes remain attached:
FE `vol-0e8c9175fe79619be` (20 GiB) and BE
`vol-0b4799bdf2215d397` (50 GiB). Instance-bound serial-console evidence proves
FE `doris-port-ready` on `9030`, BE `fe-registration-port-ready` to FE `9030`,
and BE `doris-port-ready` on `9050`, with ready/running/exit-zero diagnostics,
completed cloud-init, and zero terminal failure markers. No ECS task or SQL ran.
Immediate inspection did not find dedicated host CloudWatch file streams, so
that channel remains explicitly unverified; readiness evidence comes from EC2
serial-console output. Durable evidence is
`docs/verification/GOAL-06-DORIS-INTRA-CLUSTER-CONNECTIVITY-APPLY-2026-08-17.md`.
Goal 6 is `IN PROGRESS`; the next boundary is separately approved Phase 6-6
private ECS verifier execution and CloudWatch task evidence.

The separately approved Phase 6-6 health task then launched exactly once from
task definition `ask-david-development-doris-verifier:7` using fixed client
token `goal6-phase6-6-health-20260817-v1`. Task
`f22d6afa1898454fa35ba670f9629253` received private ENI
`eni-0543caf7d0e865cb4`, private IP `10.42.22.243`, the exact verifier SG, and
no public association. It stopped before container start with
`TaskFailedToStart`: the ECS agent timed out retrieving the exact query secret
from Secrets Manager. No health command, SQL, admin refresh, or retry ran.
Read-only inspection proves the execution role already has exact secret-read
and KMS-decrypt permissions and the endpoint is available/private-DNS-enabled
in both application subnets. The deterministic blocker is that endpoint SG
`sg-09df4c29eba7991fa` lacks TCP `443` ingress from verifier SG
`sg-04eb1ebf613ceeadc`; it currently permits the admin/workload/smoke SGs only.
Durable evidence is
`docs/verification/GOAL-06-PHASE-6-6-PRIVATE-VERIFIER-HEALTH-FAILURE-2026-08-17.md`.
Goal 6 is `BLOCKED` at Phase 6-6 pending separately approved offline
remediation for exactly one Terraform-managed private endpoint ingress rule.

The approved Phase 6-6 offline endpoint remediation is now implemented. It
adds exactly one verifier-SG-to-existing-interface-endpoint-SG TCP/443 ingress
rule next to the existing admin-task rule; both are SG references only, with no
CIDR or public exposure. Goal 6 static validation, 20 targeted pytest tests,
Terraform formatting, and isolated backend-disabled Terraform validation plus
the Doris module mock-provider test passed. The durable report is
`docs/verification/GOAL-06-PRIVATE-VERIFIER-ENDPOINT-OFFLINE-2026-08-17.md`.
No AWS, Terraform connected plan/apply/destroy, ECS retry, SQL, ECR, or
Databricks operation ran. Phase 6-6 remains unverified; the next boundary is a
separately approved saved connected development plan limited to this one rule.

The separately approved saved-plan attempt then reverified the AWS development
account/region and the workspace profile, but Terraform could not complete
refresh because account-level profile `ask-david-account` has an invalid OAuth
refresh token. The local artifact
`goal-06-private-verifier-endpoint-remediation-20260817.tfplan` is not an
approval candidate: its inspectable partial result contains 149 no-ops and
omits the required verifier-to-endpoint rule. It must not be applied. No cloud
resource changed and no ECS retry ran. The project owner must perform
interactive OAuth reauthentication for the account profile before a newly
approved saved connected plan is created. Durable blocker evidence is
`docs/verification/GOAL-06-PRIVATE-VERIFIER-ENDPOINT-CONNECTED-PLAN-BLOCKER-2026-08-17.md`.

After the project owner reauthenticated the existing account profile, saved
plan `goal-06-private-verifier-endpoint-remediation-20260817-r2.tfplan` was
created and reviewed read-only. Its SHA-256 is
`02d3e4f351eac916fea81a0846537d500a697ff3380c576cf5dc0681049c0031`; plan JSON
proves exactly one AWS create:
`aws_vpc_security_group_ingress_rule.goal6_verifier_to_aws_endpoints[0]` for
private verifier SG `sg-04eb1ebf613ceeadc` to existing endpoint SG
`sg-09df4c29eba7991fa` on TCP/443. It has 256 no-op resources and zero update,
replacement, destroy, CIDR/public-exposure, IAM/KMS, ECS/task-definition,
Databricks, production, or Goal 7+ changes. It is Git-ignored and is now
`AWAITING APPROVAL` for exact saved-plan apply. Evidence:
`docs/verification/GOAL-06-PRIVATE-VERIFIER-ENDPOINT-CONNECTED-PLAN-2026-08-17.md`.

The exact approved saved plan was applied after identity/account/region, hash,
and plan-contract revalidation. Terraform completed `1 added, 0 changed, 0
destroyed`, creating only rule `sgr-0e3ed4747a11d3b1d`. Immediate read-only
inspection confirms ingress on existing endpoint SG `sg-09df4c29eba7991fa` from
existing verifier SG `sg-04eb1ebf613ceeadc`, TCP/443 only, with no IPv4/IPv6
CIDR. No ECS task was run. Phase 6-6 path validation remains unverified until
one separately approved bounded verifier health task reaches the private FE
listener. Evidence:
`docs/verification/GOAL-06-PRIVATE-VERIFIER-ENDPOINT-APPLY-2026-08-17.md`.

The next separately approved private FE health task launched exactly once as
`ee65c772bda64d76b74de112c456bedc`, in approved application subnet
`subnet-034f5f1c9bca753f1`, with verifier SG `sg-04eb1ebf613ceeadc` and no
public association. It stopped `EssentialContainerExited` with exit `2` before
running `mysqladmin`. Sanitized CloudWatch evidence is `/bin/sh: line 3:
syntax error: unexpected word (expecting ")")`. Read-only task-definition and
image inspection proves the deterministic cause: image entrypoint `/bin/sh`
was combined with an override that redundantly began `/bin/sh -c`, forming a
double-shell invocation. This is neither a listener result nor permission or
network evidence; it does demonstrate that the prior Secrets Manager injection
blocker is no longer the observed failure. No retry ran. The approved offline
remediation adds a fail-closed health wrapper that requires no ECS task-level
entrypoint override and passes only `-c <bounded MariaDB TLS health ping>` to
the digest-bound image entrypoint. The first pre-run inspection correctly found
that ECS reports null `entryPoint` when it does not override the Docker image,
but the initial wrapper treated that expected state as a mismatch; no task was
launched. The approved offline correction changes the guard to require null
task-level entrypoint and retains the immutable image/Docker entrypoint
contract. It does not create a new image, ECR artifact, task definition,
Terraform change, or cloud operation. Goal 6 static validation, 20 focused
regression tests, Terraform formatting, Python compilation, and diff integrity
all pass; PowerShell parser execution remains unverified because PowerShell is
absent locally. The separately approved corrected health task
`f90b1e0ac7c342bfa4fcb4473f33c7cb` then ran exactly once in approved private
subnet `subnet-0a1aad220d82ef879`, with no public association, and exited `0`.
Its MariaDB TLS ping received the expected authentication-denied response from
FE `10.42.64.238:9030`; that response proves the private listener is reachable
while anonymous access remains denied. The approved offline evidence-contract
correction accepts this non-sensitive listener proof (or `mysqld is alive`) but
not a timeout, refusal, missing evidence, or non-zero exit. Phase 6-6 private
verification-path reachability is **PASS**; query-identity and serving SQL
remain unverified. Durable evidence:
`docs/verification/GOAL-06-PRIVATE-VERIFIER-FE-HEALTH-COMMAND-FAILURE-2026-08-17.md`.

Phase 6-6 is now **PASS**. The approved execution path uses a static private
FE endpoint rather than a separately provisioned DNS name, so DNS resolution
is explicitly N/A and the connected private-IP listener result is the endpoint
proof. Read-only AWS inspection confirms verifier SG
`sg-04eb1ebf613ceeadc` can reach the FE SG only on TCP/9030; FE ingress on
that port names only the verifier, admin, and BE SGs, with no CIDR/prefix-list
rule. FE and BE remain private with no public IPv4, and the task ENI is
deleted after its stopped task. This deterministic policy evidence closes the
unrelated direct-Doris-path condition without launching another task. Phase
6-7/6-8 remains `AWAITING APPROVAL` for the private admin refresh; it is not
authorized by Phase 6-6 completion. Durable evidence:
`docs/verification/GOAL-06-PHASE-6-6-PRIVATE-PATH-CLOSURE-2026-08-17.md`.

The separately approved Phase 6-7 admin-refresh task was then launched once as
`8179ca7fd66343d597a283ba02877e7e`, using the active private Fargate task
definition `ask-david-development-doris-admin-refresh:7`, its reviewed
digest-pinned image, the admin task security group, an approved private
application subnet, and `assignPublicIp=DISABLED`. It stopped with
`EssentialContainerExited` and container exit code `1`; its ephemeral ENI was
deleted. No retry, Terraform operation, AWS infrastructure change, Databricks
control-plane operation, or serving claim followed. Safe CloudWatch inspection
found one generic `ERROR` signature. After explicit owner approval, only that
single error event was retrieved; it is a non-secret Doris diagnostic proving
the runner uses invalid two-level scope `*.*` for global-only `ADMIN_PRIV`,
which requires `*.*.*` in the deployed Doris 4.0.1 authorization model. The
task failed before external catalog/OAuth/lakehouse/serving activity. Goal 6 is
**IN PROGRESS — PHASE 6-7 BLOCKED** pending separately approved offline
source/test/documentation remediation of this exact SQL grant scope. That
offline remediation is now complete: the runner grants `ADMIN_PRIV` at global
`*.*.*` scope only, and shell syntax, the Goal 6 static validator, 21 focused
pytest tests, Python compilation, and diff integrity pass. The corrected image
has not been built, scanned, pushed, or deployed, and no retry is authorized.
Two standard local Docker build attempts for immutable source aggregate
`ad0056f26ac2901410075224e57ae1406c5cfe2405e6374280bf44dbb1dd423b` stopped
while fetching Alpine package indexes and produced no image; their cause is
unverified. A separately approved host-networked local build/scan then
completed: it produced image ID
`sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad`,
retained non-root and corrected-grant runtime contracts, and passed Trivy 0.69.3
with zero HIGH/CRITICAL findings. The separately approved ECR push then created
only immutable tag `goal6-admin-priv-ad0056f2`; immediate read-only inspection
returned matching digest
`sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad`.
The next boundary is approval to update only ignored development tfvars and
create/review a saved Terraform plan expected to register two new ECS task
definition revisions; no task run is authorized.
Durable evidence:
`docs/verification/GOAL-06-PHASE-6-7-ADMIN-REFRESH-FAILURE-2026-08-17.md`.

The separately approved ignored-tfvars update and saved connected development
plan then completed. Saved artifact
`goal-06-admin-priv-task-definitions-20260817.tfplan` has SHA-256
`1f4b654bce71c95beed62d2ca3dc39a08a8c6dbca7fdaeee6798450a65ce68ad` and is
Git-ignored. Its filtered JSON contains 255 no-ops and exactly two ECS task
definition replacements: admin-refresh and read-only verifier, both due solely
to the corrected immutable image digest. Commands, names, entrypoint behavior,
private runtime topology, IAM/KMS/secrets/network/S3/Databricks resources, and
all non-task-definition state are unchanged. Plan summary is `2 to add, 0 to
change, 2 to destroy`; the delete/create representation is registration of new
revisions and retirement of Terraform state ownership of revision 7, not an ECS
task, EC2, EBS, or persistent Doris-data deletion. Goal 6 is **AWAITING
APPLY APPROVAL** for this exact plan only. Evidence:
`docs/verification/GOAL-06-ADMIN-PRIV-GRANT-TASK-DEFINITIONS-CONNECTED-PLAN-2026-08-17.md`.

The exact saved plan was separately approved and applied after hash/account and
revision revalidation. Terraform completed `2 added, 0 changed, 2 destroyed`,
registering only `ask-david-development-doris-admin-refresh:8` and
`ask-david-development-doris-verifier:8`. Read-only inspection confirms both
remain private Fargate `awsvpc` (`512` CPU / `1024` MiB), retain their exact
reviewed commands and null task-level entrypoint, and use only digest
`sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad`.
There are no running ECS tasks. No IAM/KMS/secrets/network/ECR/S3/EC2/EBS/
Databricks/source-data/public/production change occurred. Goal 6 is **AWAITING
APPROVAL** for exactly one private revision-8 admin-refresh task; task
definition registration does not authorize task execution. Evidence:
`docs/verification/GOAL-06-ADMIN-PRIV-GRANT-TASK-DEFINITIONS-APPLY-2026-08-17.md`.

The approved one-time revision-8 admin refresh then ran as
`e7f51fa2d2994c8289b7c7ac00d035b6` and stopped with exit code `1`; no retry
ran. After explicit approval, the only retrieved error was the non-secret
Doris diagnostic that the single BE has empty HDD and SSD disk maps. The
internal serving DDL already declares `replication_num = 1`, so this is a
BE usable-storage blocker rather than a replica-count setting. Approved
offline remediation now makes the BE EBS bind source explicit, configures its
`storage_root_path` as `medium:hdd`, verifies path writability using the
container's configured runtime user, and requires private `SHOW BACKENDS`
evidence of live, non-decommissioned, non-zero total capacity before emitting
BE readiness. Static validation, focused tests, shell parsing, Python
compilation, and diff integrity must be rerun before any saved Terraform plan.
No cloud operation is authorized by this offline change. Evidence:
`docs/verification/GOAL-06-BE-STORAGE-CAPACITY-OFFLINE-REMEDIATION-2026-08-17.md`.

The first following connected-plan attempt then stopped before it produced a
saved artifact: AWS provider validation rejected the rendered FE/BE EC2
`user_data` for exceeding the 16,384-byte AWS limit. No apply, ECS task,
ECR, Databricks, or other AWS mutation occurred. The approved follow-up
offline remediation removes only redundant template comments and introduces a
fail-closed Terraform pre-plan size check using the fixed-length AWS EBS-volume
ID shape and the instance payload inputs. Shell/static/pytest (23 tests),
Python compilation, Terraform fmt, a mocked Doris module Terraform test, and
diff integrity passed; the development-root Terraform validate remains
UNVERIFIED because its checked-out `.terraform` directory is owner-blocked and
the temporary-copy provider initialization did not reach validate. Any
subsequent saved plan remains pending. Evidence:
`docs/verification/GOAL-06-EC2-USER-DATA-LENGTH-OFFLINE-REMEDIATION-2026-08-17.md`.

On `2026-08-18`, project-owner connected diagnostics established a narrower
current blocker without repeating a cloud diagnostic: FE is healthy and
listens on `10.42.64.238:9020`, BE is healthy and listens on
`10.42.71.97:9050`, and the dedicated BE data volume is healthy. BE logs show
continuous FE transport timeouts on `9020` from its report callbacks. Source
inspection confirms no BE-SG-to-FE-SG TCP `9020` path. The offline remediation
adds only paired SG-to-SG BE egress and FE ingress on `9020`, with regression
coverage and no host, user-data, volume, IAM, task, public, or production
change. Offline static/Python/Terraform module validation passed. Goal 6
remains **PARTIALLY VERIFIED** pending a separately approved saved connected
plan expected to contain exactly two rule creates, separately approved apply,
and post-apply callback/capacity evidence.
Evidence: `docs/verification/GOAL-06-BE-FE-RPC-9020-OFFLINE-REMEDIATION-2026-08-18.md`.

The separately approved connected plan was then created from a temporary
Terraform data directory because the repository-local `.terraform` cache is
not writable. Dependency-lock selections remained read-only. The saved plan
SHA-256 is
`2e5d7aaa4889fd90865f312c3659f6ce1f41cc6a82dde8d8a3faecb56fb9ae4b`.
Filtered plan JSON proves exactly two creates: BE SG egress to FE SG TCP
`9020`, and FE SG ingress from BE SG TCP `9020`; update, replacement, and
destroy are zero. EC2, user data, EBS/attachments, IAM/KMS, ECS/task
definitions, Databricks, public exposure, production, and unrelated planned
actions are zero. No apply or task ran. Evidence:
`docs/verification/GOAL-06-BE-FE-RPC-9020-CONNECTED-PLAN-2026-08-18.md`.

The exact saved plan was separately approved and applied after fail-closed
account, region, SHA-256, and filtered-action guards passed. Terraform
completed as `2 added, 0 changed, 0 destroyed`, creating only egress rule
`sgr-092a7ed0c879d5bea` and ingress rule
`sgr-09b2940215ba4691b`. Immediate inspection confirms both are paired
SG-to-SG TCP `9020` rules, both FE/BE instances remain `running` with `ok/ok`
platform checks, no public or unrelated change occurred, and no task ran.
VPC Flow Logs show the historical BE-to-FE attempts ending at `08:00:23Z`
were `REJECT`, while connections beginning at `08:24:25Z`—seven seconds after
the rules were created—are bidirectional `ACCEPT` with non-zero packets and
bytes. This proves the network blocker is remediated. The Doris log group has
no FE/BE host stream, so direct evidence that callback errors ceased and that
`SHOW BACKENDS` reports usable capacity remains **UNVERIFIED**. Evidence:
`docs/verification/GOAL-06-BE-FE-RPC-9020-APPLY-2026-08-18.md`.

Because the current FE/BE bootstrap processes have already completed and the
dedicated CloudWatch log group has no current host streams, those hosts cannot
retroactively emit the required readiness markers. The approved offline-only
follow-up adds paired PowerShell and Bash wrappers for exactly one private,
bounded diagnostic task. The runnable Bash path is required on this Linux
host because `pwsh` is unavailable. Both wrappers inspect the immutable
revision-8 admin task definition, retain its private subnets/security group
and digest-pinned image, override only its command, and execute only
`SHOW BACKENDS;`. They fail closed unless FE `10.42.64.238:9030` is queryable
and BE `10.42.71.97` is alive, not decommissioned, and has non-zero total
capacity. A success emits exactly the required sanitized `listener_state`,
`doris-port-ready`, and `be-storage-capacity-ready` evidence to the task's
CloudWatch stream; it does not run refresh, DDL, DML, Terraform, ECR,
Databricks, or any AWS control-plane mutation beyond the separately approved
one-off ECS task execution. Static validation, Bash parsing, and 26 focused
regression tests pass. No task has run yet, so all current runtime markers
remain **UNVERIFIED** pending a separate one-task approval. Evidence:
`docs/verification/GOAL-06-RUNTIME-READINESS-MARKERS-OFFLINE-2026-08-18.md`.

The separately approved diagnostic then ran exactly once as task
`221d070dc24b40b0a1144b573e137fac` from
`ask-david-development-doris-admin-refresh:8`. It used approved private subnet
`subnet-0a1aad220d82ef879`, private IP `10.42.44.26`, admin SG
`sg-07a0dd2e8af8aa178`, and no public-IP assignment. The task stopped with
container exit code `0` and its exact CloudWatch stream contains all five
required records: FE and BE `listener_state=ready`, FE `doris-port-ready` on
`9030`, BE `doris-port-ready` on `9050`, and BE
`be-storage-capacity-ready` with alive true, decommissioned false, and
non-zero total capacity. No unavailable marker exists. The task ran only the
bounded `SHOW BACKENDS;` diagnostic; no refresh, DDL/DML, Terraform, ECR, or
Databricks operation and no retry occurred. A post-stop EC2 ENI lookup returned
`InvalidNetworkInterfaceID.NotFound` because Fargate had already reclaimed the
ephemeral ENI; ECS task attachment metadata remains the durable private subnet
and address evidence. FE/BE listener and BE capacity readiness are therefore
**PASS**. Goal 6 itself remains partially verified; resuming Phase 6-7 admin
refresh and later acceptance phases requires separate approval. Evidence:
`docs/verification/GOAL-06-RUNTIME-READINESS-MARKERS-CONNECTED-2026-08-18.md`.

Phase 6-7 resumption is now prepared offline. Read-only revalidation confirms
AWS account `736956442295`, `ap-southeast-1`, no running Goal 6 admin task,
active private task definition `ask-david-development-doris-admin-refresh:8`,
the approved immutable image digest, FE/BE addresses, and Databricks workspace
origin. Databricks CLI revalidation confirms the intended AWS metastore
`3a7f7e7a-680b-4bd6-907a-6d5e77b43178` in `ap-southeast-1`, external access
enabled, and isolated catalog `ask_david_development`. Because `pwsh` is absent
on the Linux host, a paired Bash admin wrapper now implements the same guarded,
private, exactly-one-task/no-retry contract while additionally binding task and
execution roles, workspace origin, environment values, the three expected
secret-reference names, and CloudWatch configuration. Static validation and
27 focused regression tests pass. No admin task or mutation ran. Goal 6 is
**AWAITING SEPARATE PHASE 6-7 ADMIN-REFRESH TASK APPROVAL**. Evidence:
`docs/verification/GOAL-06-PHASE-6-7-ADMIN-REFRESH-BASH-WRAPPER-OFFLINE-2026-08-18.md`.

The separately approved Phase 6-7 admin refresh then ran exactly once from
Terraform-created task definition
`ask-david-development-doris-admin-refresh:8`. Task
`40f70181929648a6879ed973fb75bc57` ran on Fargate `1.4.0` in private subnet
`subnet-034f5f1c9bca753f1`, received only private address `10.42.25.231`, used
admin SG `sg-07a0dd2e8af8aa178`, stopped with exit code `0`, and emitted the
sanitized `admin-refresh/completed` marker. No admin task remains running and
no retry occurred. Because the fixed runner emits that marker only after the
temporary Unity Catalog Iceberg REST catalog successfully reads the allowlisted
Delta UniForm source, reloads the internal disposable serving table, records
refresh state, and drops the catalog, actual Doris/Unity Catalog interoperability
and initial refresh are now **PASS**. Source/destination count and representative
value parity remain **UNVERIFIED** until the separately approved read-only
verifier runs; they are not inferred from the completion marker. Evidence:
`docs/verification/GOAL-06-PHASE-6-7-ADMIN-REFRESH-CONNECTED-2026-08-18.md`.

The subsequent connected read-only privilege/source audit found the active
dedicated Doris external-read service principal and exactly the intended
least-privilege chain: `USE_CATALOG` on the development catalog,
`USE_SCHEMA` plus `EXTERNAL_USE_SCHEMA` on `green_sm_business`, and `SELECT`
on only `goal5_structured_business_metrics`. No source write/create/admin
grant appears for that principal. Live Tables API metadata classifies the
managed source as Delta with `delta.universalFormat.enabledFormats=iceberg`
and an approved Business-bucket `_iceberg/metadata` path; it is therefore
`DELTA_UNIFORM_ICEBERG`, not native Iceberg. Actual Doris interoperability
remains **UNVERIFIED** until the separately approved task completes a real
query. No Databricks or AWS mutation occurred during this audit.

An offline audit of later Phase 6 evidence found that the deployed read-only
verifier contract omitted the mandatory representative `query_result` and
queried `LAST_QUERY_ID()` through a separate MariaDB connection. The source
remediation now collects the representative row and its immediate query ID in
one TLS session and emits the complete typed result contract required by final
acceptance item 39. Static validation, POSIX shell parsing, a mocked execution,
and 28 focused regression tests pass. No image was built or deployed, so the
active revision-8 verifier task definition still uses the prior immutable
runner. This does not block the pending revision-8 admin-refresh task, but all
later read-only verification requires a newly built/scanned image, separately
approved ECR push, and separately planned/applied task-definition revisions.
Evidence:
`docs/verification/GOAL-06-RESULT-CONTRACT-OFFLINE-REMEDIATION-2026-08-18.md`.

The remaining Phase 6-11/6-12/6-13 executable evidence gaps are also
implemented offline. New source-only runners provide safe actual RBAC denial
probes against a dedicated disposable internal object, bounded
`query_timeout=30` enforcement through `SLEEP(31)`, and sanitized audit-log
correlation for query ID, identity, target, state, duration, and workload
group. Official Doris 4.x source/documentation was checked for these contracts.
All runner shell parses, static validation, mocked contracts, 35 focused tests,
and diff integrity pass. The exact source set was subsequently built into local
image ID
`sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510`
and scanned with zero HIGH/CRITICAL Trivy findings. It has not been pushed or
deployed, and the active revision-8 image does not include these runners. They
remain gated on Phase 6-7 success followed by a separately approved immutable
ECR push and Terraform-managed task-definition revisions. Evidence:
`docs/verification/GOAL-06-LATER-PHASE-VERIFIERS-OFFLINE-2026-08-18.md` and
`docs/verification/GOAL-06-LATER-PHASE-IMAGE-BUILD-SCAN-2026-08-18.md`.

After Phase 6-7 passed, the exact later-phase image was pushed under immutable
tag `goal6-later-ecbd7e31`. ECR digest
`sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510`
matches the approved local image ID. Docker logged out immediately. ECR Basic
scan findings are **NOT RUN** because the live registry has no scan-on-push
filter; no manual scan was authorized. The exact local image retains its zero
HIGH/CRITICAL Trivy result. Ignored tfvars and active revision-8 task
definitions remain unchanged on the prior digest. Goal 6 is now **AWAITING
SEPARATE TFVARS/PREFLIGHT/SAVED-PLAN APPROVAL** for only two task-definition
revisions. Evidence:
`docs/verification/GOAL-06-LATER-PHASE-IMAGE-ECR-PUSH-2026-08-18.md`.

The later non-destructive verifier execution boundary is also prepared
offline. `run-goal6-verifier.sh` allowlists only `readonly`, `rbac`, and
`query-limit`; binds the exact account, region, task revision, immutable image,
roles, query-only secret shape, two private subnets, verifier SG, FE address,
and CloudWatch configuration; and permits exactly one no-retry task only with
an explicit confirmation switch. Bash parsing, a pre-AWS missing-confirmation
failure, static validation, 36 focused tests, and diff integrity pass. No task
or cloud operation ran, and this host-side wrapper does not change the pushed
image digest. Evidence:
`docs/verification/GOAL-06-LATER-PHASE-VERIFIER-WRAPPER-OFFLINE-2026-08-18.md`.

The admin-only later-operation boundary is now prepared offline as well.
`run-goal6-admin-operation.sh` exposes only `rebuild` and `audit`, requires a
different non-interchangeable confirmation for each, binds the exact private
admin task-definition contract, and launches at most one no-retry task. The
rebuild wrapper cannot chain a reload; the required refresh and post-rebuild
comparison remain separately approved tasks. The audit wrapper accepts only a
specific prior query ID. Bash parsing, both pre-AWS missing-confirmation
failures, static validation, 37 focused tests, and diff integrity pass. No
cloud operation ran and the pushed image digest is unchanged. Evidence:
`docs/verification/GOAL-06-ADMIN-OPERATION-WRAPPER-OFFLINE-2026-08-18.md`.

Phase 6-9's controlled authoritative increment contract has also been audited
offline. The one neutral record uses idempotent layer-specific MERGE keys
through the existing Goal 5 Raw, Curated, and Business tables, with exact
one-row assertions and Business total `42.0`. The job reuses the existing
Serverless SQL Warehouse, disables concurrency queueing, and contains no Doris
operation; a future Doris refresh remains a separate task after the source
changes first. Static validation, 38 focused tests, and diff integrity pass.
No connected bundle validation/deploy, SQL/job, table mutation, refresh, or
cloud operation ran. Evidence:
`docs/verification/GOAL-06-PHASE-6-9-CONTROLLED-INCREMENT-OFFLINE-AUDIT-2026-08-18.md`.

The separately approved strict connected Phase 6-9 bundle validation then
passed exactly once on `2026-08-20` from the `databricks/` bundle root. The
development profile resolved workspace `7474644358733471`, and the CLI
returned `Validation OK!` with no warning, error, or recommendation. The
validation used the existing Serverless SQL Warehouse and Terraform-derived
development variables without passing `workspace_host`. No deployment, job or
SQL execution, table mutation, compute creation, Terraform operation, AWS
operation, or ECS task occurred. The controlled increment itself, Doris
refresh/comparison, Phase 6-10 rebuild, and Phase 6-14 final drift/cleanup
remain separate checkpoints. Evidence:
`docs/verification/GOAL-06-PHASE-6-9-BUNDLE-VALIDATION-2026-08-20.md`.

Read-only inspection then found the controlled-increment job already deployed
in the development workspace as job `227623174725080`. Its two synchronized
SQL files matched the reviewed repository hashes byte-for-byte. The job had
exactly one `ONE_TIME` run (`438156863255366`) with both apply and verify tasks
`TERMINATED / SUCCESS`, no repair history, the existing Serverless SQL
Warehouse, and no cluster specification. This supplies PASS evidence for the
authoritative Raw → Curated → Business increment; no deployment or run was
started by the current review. Doris refresh/comparison, Phase 6-10 rebuild,
and Phase 6-14 final drift/cleanup remain separate checkpoints. Evidence:
`docs/verification/GOAL-06-PHASE-6-9-INCREMENT-CONNECTED-2026-08-20.md`.

After the successful controlled increment, the separately approved private
admin-refresh task ran exactly once from revision `16`. Task
`b3314db778e84f47a5bdddaabdd599f0` stopped with container exit `0` in private
subnet `subnet-034f5f1c9bca753f1` at `10.42.22.219`; its CloudWatch stream
emitted the completed `admin-refresh` marker and no retry occurred. This
provides the post-increment governed Doris refresh evidence. The read-only
result comparison, Phase 6-10 rebuild, and Phase 6-14 final drift/cleanup
remain separate checkpoints. Evidence:
`docs/verification/GOAL-06-PHASE-6-7-ADMIN-REFRESH-POST-INCREMENT-2026-08-20.md`.

The separately approved post-refresh read-only verifier then ran exactly once
from revision `16`. Task `9e399737d999478d9f8713d13b2485be` exited `0` in
private subnet `subnet-034f5f1c9bca753f1` at `10.42.16.135`; its CloudWatch
marker reported `readonly-verify / completed` with source dataset,
representative result, serving row count `3`, source/serving timestamps,
query ID, and execution duration. Phase 6-8 read-only result-contract
acceptance is now PASS. Phase 6-10 rebuild and Phase 6-14 final drift/cleanup
remain separate checkpoints. Evidence:
`docs/verification/GOAL-06-PHASE-6-8-READONLY-POST-INCREMENT-2026-08-20.md`.

The saved connected development plan for the later-phase immutable verifier
image was generated after AWS identity revalidation for account `736956442295`
in `ap-southeast-1`. Saved-plan SHA-256
`66f28c1c5b646637dd70536238c8cb69db2cad84a7a378fe0f737769ac87dcb9`
contained exactly two task-definition revision replacements, both only because
of `container_definitions`; all other 257 managed resources were no-op. The
approved apply completed as `2 added, 0 changed, 2 destroyed`, registering
`ask-david-development-doris-admin-refresh:9` and
`ask-david-development-doris-verifier:9` on the exact immutable digest
`sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510`.
Immediate read-only ECS inspection confirms both revision-9 definitions are
ACTIVE, remain Fargate `512` CPU/`1024` MiB with `awsvpc`, preserve their
respective guarded command and secret-reference-name scopes, and have no
RUNNING task. No IAM, KMS, network, security-group, ECR, EC2/EBS, S3,
Databricks, public-exposure, or production change occurred. The next boundary
is one separately approved read-only verifier task; no task is authorized by
this apply. Evidence:
`docs/verification/GOAL-06-LATER-PHASE-TASK-DEFINITIONS-APPLY-2026-08-18.md`.

The separately approved revision-9 read-only verifier then ran exactly once as
task `dd97ba3989a24d40b19ee08df5c98b2a`. It launched with no public IP in
approved private application subnet `subnet-034f5f1c9bca753f1`, private address
`10.42.28.73`, and verifier SG `sg-04eb1ebf613ceeadc`; its ephemeral ENI was
deleted after task stop as expected. The only container exited `0`; no retry
ran and no verifier task remains RUNNING. The exact CloudWatch evidence has a
completed TLS query-only result contract: source dataset
`ask_david_development.green_sm_business.goal5_structured_business_metrics`,
representative neutral row (`2026-02-01`, `alpha`, event count `1`, total
`10.5`), serving row count `2`, source and serving refresh timestamps,
executed query ID, and execution duration. This proves the intended read-only
Doris query identity, serving-result provenance, and required result-contract
fields; it does not infer RBAC denials, timeout enforcement, incremental
refresh, rebuild, or audit correlation. Evidence:
`docs/verification/GOAL-06-PHASE-6-8-READONLY-VERIFIER-CONNECTED-2026-08-18.md`.

The separately approved revision-9 RBAC verifier ran exactly once as task
`be576a484aa6438a82cbc3509a4b8a00` and exited `1` on its first `insert`
negative probe with the sanitized marker `wrong-rejection-layer`. That is a
real **FAIL** for the required principal-specific RBAC evidence, not proof that
any probe was permitted. The prior runner deliberately did not export raw
database stderr, so the underlying Doris denial wording cannot be reconstructed
from the durable log. A source-only remediation now accepts only explicit
authorization language or a canonical Doris `*_PRIV` token and records a
sanitized `denial_evidence` class; it keeps non-authorization errors
fail-closed. The remediation has no connected execution evidence and does not
change the current result: Phase 6-11 remains unverified pending a separately
approved immutable-image promotion and one no-retry RBAC task. Its local
non-root Linux/amd64 image, `ask-david-doris-verifier:goal6-rbac-25b09566`,
was subsequently scanned by Trivy `0.69.3` with a current public DB and has
zero HIGH/CRITICAL findings. The scan itself ran network-disabled after the
approved DB download. A following read-only ECR preflight confirmed the exact
development account/region, immutable scan-on-push repository, and that tag
`goal6-rbac-25b09566` is absent. The separately approved push then created
only that immutable ECR tag with matching digest
`sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6`;
Docker logged out immediately. Although repository scan-on-push is enabled,
ECR returned `ScanNotFoundException`, so registry scan findings are explicitly
**NOT RUN**. No Terraform, ECS task, SQL, Databricks, or AWS resource mutation
occurred beyond the approved image/blob push. Evidence:
`docs/verification/GOAL-06-RBAC-REMEDIATION-IMAGE-ECR-PUSH-2026-08-18.md`.

The separately approved saved connected development plan for the RBAC
remediation image had SHA-256
`09a97fcdc9cacdbd82e69ea8157a7f74753fc8578d5280be8ce62433179ac7db`.
It contained exactly two ECS task-definition revision replacements—admin-refresh
and read-only verifier—solely because `container_definitions.image` changed
from immutable digest `sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510`
to `sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6`;
all other 257 managed resources were no-op. The approved apply completed as
`2 added, 0 changed, 2 destroyed`. Immediate read-only inspection confirms
`ask-david-development-doris-admin-refresh:10` and
`ask-david-development-doris-verifier:10` are ACTIVE on the exact reviewed
digest, retain Fargate `512` CPU/`1024` MiB and `awsvpc`, and have no RUNNING
task. No IAM, KMS, network, security-group, ECR, EC2/EBS, S3, Databricks,
public-exposure, or production change occurred. Goal 6 is now **AWAITING A
SEPARATELY APPROVED REVISION-10 RBAC VERIFIER TASK**. Evidence:
`docs/verification/GOAL-06-RBAC-REMEDIATION-TASK-DEFINITIONS-APPLY-2026-08-19.md`.

The separately approved revision-10 RBAC verifier then ran exactly once as
task `c91db7d52e2148c68d38b3d3cd7e07ce`. Pre-run inspection confirmed both
Doris hosts running, the exact ACTIVE task revision/image, and no existing
RUNNING verifier task. The private Fargate container exited `1` at the first
negative probe with sanitized marker `wrong-rejection-layer` for `insert`.
This is a real **FAIL**, not evidence that the statement was allowed: the
runner uses the distinct marker `unexpected-allow` for that case. Root-cause
analysis confirms a schema-application ordering gap. The disposable
`goal6_authorization_probe` was added after the last successful revision-8
admin refresh; revisions 9/10 were registered but no schema-bearing admin
refresh ran before the verifier. Doris resolves the missing target before its
`LOAD` privilege check, so the classifier correctly rejected the non-auth
failure. No classifier, image, Terraform, or privilege change is required.
No retry ran, the ephemeral ENI was deleted, and no verifier task remains
RUNNING. Goal 6 is now **AWAITING A SEPARATELY APPROVED REVISION-10 ADMIN
REFRESH TO APPLY THE VERSIONED DISPOSABLE SCHEMA**; Phase 6-11 and final
acceptance items 34–35 remain unverified. Evidence:
`docs/verification/GOAL-06-RBAC-REVISION-10-CONNECTED-FAILURE-2026-08-19.md`.

The separately approved corrective revision-10 admin refresh then ran exactly
once as private Fargate task `c08352df6d7846128c7852e3d130b700`. It used the
exact immutable digest
`sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6`,
stopped with container exit `0`, and emitted the terminal `admin-refresh`
`completed` marker. That marker follows the version-controlled schema steps,
governed allowlisted refresh, refresh-state update, and temporary-catalog
cleanup, so the live disposable `goal6_authorization_probe` precondition is
now applied. The private ENI was deleted after stop, no admin task remains
RUNNING, and no retry occurred. No RBAC task was included in this approval.
Goal 6 is now **AWAITING A SEPARATELY APPROVED REVISION-10 RBAC RETRY**;
Phase 6-11 and final acceptance items 34–35 remain unverified. Evidence:
`docs/verification/GOAL-06-RBAC-SCHEMA-ORDERING-ADMIN-REFRESH-CONNECTED-2026-08-19.md`.

The separately approved revision-10 RBAC retry then ran exactly once as task
`03e18f53e9e146c6bba33c5c485de092`. It confirmed principal-specific
authorization denials for `INSERT` and `UPDATE`, then exited `1` because
`DELETE ... WHERE FALSE` returned success. Version-bound Doris 4.0.1 source
confirms this is its constant-false `PhysicalEmptyRelation` no-op path, which
returns before the LOAD privilege check. No row was deleted and the result is
not evidence that DELETE privilege exists, but it also cannot satisfy the
required denial test. CREATE/ALTER/DROP/unauthorized-database probes did not
run. No retry followed, the private ENI was deleted, and no verifier task
remains RUNNING. Goal 6 is now **AWAITING APPROVAL FOR AN OFFLINE DELETE-PROBE
REMEDIATION**; Phase 6-11 and final acceptance items 34–35 remain partially
unverified. Evidence:
`docs/verification/GOAL-06-RBAC-REVISION-10-RETRY-FAILURE-2026-08-19.md`.

The approved offline DELETE-probe remediation replaces only the invalid
constant-false DELETE evidence path. The runner now requires the query-only
identity to prove reserved key `127` absent from the disposable
`goal6_authorization_probe` before attempting DELETE with that non-constant
predicate. A query failure, non-zero count, wrong rejection layer, or allowed
DELETE fails closed; the absent-key precondition guarantees zero affected rows
even in the unexpected-allow case. Static validation, shell parsing, focused
regression tests, and diff integrity pass. No image was built/pushed, no task
definition changed, and no ECS/Doris/AWS/Databricks operation ran. Goal 6 is
now **AWAITING SEPARATE APPROVAL FOR IMMUTABLE IMAGE BUILD/SCAN AND PROMOTION**;
Phase 6-11 remains only partially verified. Evidence:
`docs/verification/GOAL-06-RBAC-DELETE-PROBE-OFFLINE-REMEDIATION-2026-08-19.md`.

The separately approved local artifact checkpoint built exact source aggregate
`c468b8fde5b00aacb208d460099b408b9893912a845a5d48b8f1b59b6647dc64`
as `ask-david-doris-verifier:goal6-delete-probe-c468b8fd`. Read-only inspection
confirmed local OCI image ID
`sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e`,
Linux/amd64, non-root `65532:65532`, and `/bin/sh` entrypoint. A network-
disabled, read-only container verified all six runners, exact remediated RBAC
runner hash, and MariaDB `11.4.12`. Trivy `0.69.3` downloaded a current public
DB and found zero HIGH/CRITICAL vulnerabilities with `--ignore-unfixed`. No
temporary container remains. No ECR push, Terraform/ECS change, task, Doris
SQL, AWS, or Databricks operation occurred. Goal 6 is now **AWAITING SEPARATE
APPROVAL TO PUSH THIS EXACT SCANNED LOCAL IMAGE TO AN IMMUTABLE ECR TAG**;
deployed revision 10 remains unchanged. Evidence:
`docs/verification/GOAL-06-RBAC-DELETE-PROBE-IMAGE-BUILD-SCAN-2026-08-19.md`.

The separately approved ECR promotion then pushed only immutable tag
`goal6-delete-probe-c468b8fd` to the private development verifier repository.
Preflight confirmed account `736956442295`, Region `ap-southeast-1`, repository
tag immutability, scan-on-push configuration, and that the tag did not exist.
Remote OCI digest
`sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e`
matches the exact scanned local image ID. Docker logged out immediately. ECR
returned no image-scan status and `ScanNotFoundException`, so registry findings
are **NOT RUN**; the exact local Trivy scan remains PASS with zero HIGH/CRITICAL
findings. No Terraform, ECS task/task-definition, Doris SQL, Databricks, or
other AWS resource mutation occurred. Goal 6 is now **AWAITING SEPARATE
APPROVAL TO UPDATE IGNORED TFVARS, RUN OFFLINE PREFLIGHT, AND CREATE A SAVED
CONNECTED TASK-DEFINITION-ONLY PLAN**; revision 10 remains deployed on the old
digest. Evidence:
`docs/verification/GOAL-06-RBAC-DELETE-PROBE-IMAGE-ECR-PUSH-2026-08-19.md`.

The ignored development image input was then updated under separate approval
to exact ECR digest
`sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e`,
with verifier tasks remaining enabled. Offline formatting, static validation,
50 Python regressions, Terraform validation, and all 7 development Terraform
tests pass. AWS identity was reverified for account `736956442295` and Region
`ap-southeast-1`. Saved plan
`/tmp/goal-06-rbac-delete-probe-task-definitions-20260819.tfplan` has SHA-256
`decb5329e0c7b7d811525da23d1a607ee8527c4b1a197e6adcea9cfdc88a4dcf`.
Machine-readable inspection shows exactly two `delete,create` ECS task-
definition replacements—admin-refresh and verifier—caused only by
`container_definitions` image changes from the revision-10 digest to the new
digest; all other 257 managed resources are no-op. There is no unrelated,
Databricks, public, or production action. The plan has not been applied and no
task ran. Goal 6 is now **AWAITING HASH-BOUND APPROVAL TO APPLY THIS EXACT SAVED
PLAN**. Evidence:
`docs/verification/GOAL-06-RBAC-DELETE-PROBE-TASK-DEFINITIONS-CONNECTED-PLAN-2026-08-19.md`.

The exact saved plan was then applied under hash-bound approval after SHA-256,
AWS account, and Region revalidation. Terraform completed as exactly `2 added,
0 changed, 2 destroyed`, representing only registration/state replacement of
the two reviewed ECS task-definition revisions. Immediate read-only inspection
confirms `ask-david-development-doris-admin-refresh:11` and
`ask-david-development-doris-verifier:11` are ACTIVE on exact image digest
`sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e`,
remain private Fargate `512` CPU / `1024` MiB with `awsvpc`, and revisions 10
are INACTIVE. Both families have zero RUNNING tasks. No IAM, KMS, network,
security-group, ECR, EC2/EBS, S3, Databricks, public, or production resource
changed, and no task or Doris SQL ran. Goal 6 is now **AWAITING A SEPARATELY
APPROVED ONE-SHOT REVISION-11 RBAC RETRY**; Phase 6-11 remains partially
verified until every denial class completes successfully. Evidence:
`docs/verification/GOAL-06-RBAC-DELETE-PROBE-TASK-DEFINITIONS-APPLY-2026-08-19.md`.

The separately approved revision-11 RBAC verifier then ran exactly once as
private task `8a24b56cb8604292ad77c4e260add739`. The task proved explicit
principal-specific authorization denials for INSERT and UPDATE, but stopped
with exit `1` when DELETE returned success; CREATE, ALTER, DROP, and the
unauthorized-database probe therefore did not run. Version-bound Doris 4.0.1
source and the live result show that a non-constant predicate against the
entirely empty disposable table was still converted to an empty relation by
empty-partition pruning before the later `LOAD_PRIV` check. The reserved-key
precondition proves that no row was deleted, but the result is not acceptable
RBAC-denial evidence. No retry ran, the ephemeral private ENI was deleted, and
no verifier task remains RUNNING. Evidence:
`docs/verification/GOAL-06-RBAC-REVISION-11-EMPTY-PARTITION-FAILURE-2026-08-19.md`.

The approved offline remediation retains the reserved-key absence precondition
and executes `SET disable_empty_partition_prune = true` plus the DELETE in the
same MariaDB session. This prevents the Doris 4.0.1 empty-partition rewrite
from returning before `LOAD_PRIV`, while the precondition keeps the probe
deterministically zero-row. Static validation and regression tests cover the
same-session contract, fail-closed behavior, and no reintroduction of the
constant-false path. No image build/push, Terraform operation, ECS task, Doris
connected SQL, AWS, or Databricks operation occurred. Goal 6 is now **AWAITING
SEPARATE APPROVAL FOR IMMUTABLE IMAGE BUILD/SCAN**; Phase 6-11 remains only
partially verified. Evidence:
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-OFFLINE-REMEDIATION-2026-08-19.md`.

The separately approved local artifact checkpoint then built exact source
aggregate
`3195354def2b35b9d2ca828594ae455e593906689a46145e2ba7b05bcf19a7f5`
as `ask-david-doris-verifier:goal6-empty-prune-3195354d`. Read-only inspection
confirmed local OCI image ID
`sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9`,
Linux/amd64, non-root `65532:65532`, and `/bin/sh` entrypoint. A network-
disabled, read-only container verified all six runners, exact remediated RBAC
runner hash, same-session pruning guard, absence of the invalid constant-false
DELETE, and MariaDB `11.4.12`. Trivy `0.69.3` downloaded a current public DB
and found zero HIGH/CRITICAL findings across 34 Alpine `3.21.7` packages. No
temporary container remains. No ECR push, Terraform/ECS change, task, Doris
SQL, AWS project operation, or Databricks operation occurred. Goal 6 is now
**AWAITING SEPARATE APPROVAL TO PUSH THIS EXACT SCANNED LOCAL IMAGE TO AN
IMMUTABLE ECR TAG**; deployed revision 11 remains unchanged. Evidence:
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-IMAGE-BUILD-SCAN-2026-08-19.md`.

The separately approved ECR promotion then pushed only immutable tag
`goal6-empty-prune-3195354d` to the private development verifier repository.
Preflight confirmed account `736956442295`, Region `ap-southeast-1`, repository
tag immutability, scan-on-push configuration, AES256 encryption, exact local
OCI digest, and that the tag did not exist. Remote OCI digest
`sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9`
matches the exact scanned local image ID. Docker logged out immediately. ECR
returned no image-scan status and `ScanNotFoundException`, so registry findings
are **NOT RUN**; the exact local Trivy scan remains PASS with zero HIGH/CRITICAL
findings. No Terraform, ECS task/task-definition, Doris SQL, Databricks, or
other AWS resource mutation occurred. Goal 6 is now **AWAITING SEPARATE
APPROVAL TO UPDATE IGNORED TFVARS, RUN OFFLINE PREFLIGHT, AND CREATE A SAVED
CONNECTED TASK-DEFINITION-ONLY PLAN**; revision 11 remains deployed on the old
digest. Evidence:
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-IMAGE-ECR-PUSH-2026-08-19.md`.

Under separate approval, the ignored development verifier image input was
updated to exact pushed digest
`sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9`
with verifier tasks still enabled. Goal 6 static validation, 50 Goal 5/6
regressions, Terraform recursive formatting, validation, and all 7 development
Terraform tests pass. Connected identity revalidation matched account
`736956442295` and Region `ap-southeast-1`, and the isolated Terraform data
directory connected to the reviewed S3 backend. The single approved plan
attempt then exited `1`: Databricks workspace reads returned `unexpected EOF`
and account OAuth refresh for profile `ask-david-account` timed out. Terraform
wrote local artifact
`/tmp/goal-06-rbac-empty-partition-pruning-task-definitions-20260819.tfplan`,
but machine-readable metadata explicitly reports `applyable=false`,
`complete=false`, and `errored=true`; it is ineligible for apply. Its partial
change preview contains only the expected two task-definition replacements,
but that is not a valid saved-plan acceptance result. No apply, task, ECR push,
Doris SQL, or infrastructure mutation followed. Goal 6 is now **AWAITING USER
REAUTHENTICATION OF THE DATABRICKS ACCOUNT/WORKSPACE PROFILES AND SEPARATE
APPROVAL FOR ONE NEW SAVED-PLAN ATTEMPT**. Evidence:
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-CONNECTED-PLAN-BLOCKER-2026-08-19.md`.

After the user restored both Databricks OAuth profiles, a separately approved
retry reverified the active workspace principal, account workspace
`7474644358733471` as `RUNNING` / `PREMIUM` / `SERVERLESS` in
`ap-southeast-1`, and AWS account/Region. The retry used a new artifact path;
the prior errored plan was preserved and not reused. Saved plan
`/tmp/goal-06-rbac-empty-partition-pruning-task-definitions-retry-20260819.tfplan`
has SHA-256
`8e6e62d931eb86fe5b65e335cb996122fdb7c05f121fcc85a3cd50f81582f9d0`.
Machine-readable metadata reports `applyable=true`, `complete=true`, and
`errored=false`. It contains exactly two `delete,create` ECS task-definition
replacements—admin-refresh and read-only verifier—caused only by
`container_definitions` image changes from revision-11 digest
`sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e`
to exact scanned/pushed digest
`sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9`;
all other 257 managed resources are no-op. Only the corresponding two output
ARNs update. There is no IAM, KMS, network/security-group, ECR, EC2/EBS, S3,
Databricks, public, production, or Goal 7+ action. No apply or task ran. Goal 6
is now **AWAITING HASH-BOUND APPROVAL TO APPLY THIS EXACT SAVED PLAN**.
Evidence:
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-TASK-DEFINITIONS-CONNECTED-PLAN-2026-08-19.md`.

Under separate hash-bound approval, the saved artifact with SHA-256
`8e6e62d931eb86fe5b65e335cb996122fdb7c05f121fcc85a3cd50f81582f9d0`
was reverified as `applyable=true`, `complete=true`, and `errored=false`, then
applied directly without an implicit new plan. Terraform reported exactly two
task-definition replacements (`2 added, 0 changed, 2 destroyed`): admin-refresh
and read-only verifier only. Immediate read-only inspection confirms both
revision 12 definitions are ACTIVE, use exact image digest
`sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9`,
retain private Fargate/`awsvpc` shape and their scoped task roles, and have zero
RUNNING tasks. No task, Doris SQL, or unrelated AWS/Databricks operation ran.
Goal 6 is now **AWAITING SEPARATE APPROVAL FOR EXACTLY ONE PRIVATE, NO-RETRY
REVISION-12 RBAC VERIFIER RUN**. Evidence:
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-TASK-DEFINITIONS-APPLY-2026-08-19.md`.

The separately approved one-shot revision-12 RBAC verifier then ran exactly
once as task `d5dfb96b0dbb46da8c912911baa51889`. It used the reviewed private
Fargate placement, exact digest, verifier role, and FE endpoint, then stopped
with container exit `1`; its ephemeral ENI was deleted and no retry occurred.
CloudWatch records explicit authorization-layer denial for INSERT and UPDATE
but `unexpected-allow` for DELETE, despite the deployed runner's reserved-key
precondition and same-client `disable_empty_partition_prune=true` guard. The
runner stopped before CREATE/ALTER/DROP/unauthorized-database probes. This is
not sufficient principal-specific RBAC evidence and Phase 6-11 remains partial.
No follow-on mutation occurred. Goal 6 is now **AWAITING SEPARATE APPROVAL FOR
OFFLINE ROOT-CAUSE ANALYSIS AND A MINIMAL REMEDIATION PLAN FOR THE REVISION-12
DELETE-PROBE FAILURE**. Evidence:
`docs/verification/GOAL-06-RBAC-REVISION-12-EMPTY-PARTITION-RETRY-FAILURE-2026-08-19.md`.

The separately approved offline analysis confirmed that the revision-12
`disable_empty_partition_prune` guard cannot establish the needed local-OLAP
authorization path. In the pinned Doris 4.0.1 source,
`PruneEmptyPartition` itself does not consult that session setting; it converts
the entirely empty probe partition into an empty relation, and
`DeleteFromCommand` returns before `LOAD_PRIV`. The minimum safe correction is
planned, not implemented: the controlled admin path will seed disposable
neutral sentinel keys `126` and `128`, while the query-only verifier will prove
both exist and target `127` is absent before it attempts a zero-row DELETE of
`127`. A wrongly authorized DELETE would still affect no row and fail closed.
No source, image, Terraform, task, AWS, Databricks, or Doris connected
operation occurred during analysis. Goal 6 is now **AWAITING SEPARATE APPROVAL
FOR OFFLINE IMPLEMENTATION OF THE NON-EMPTY DELETE-PROBE REMEDIATION**.
Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-REMEDIATION-PLAN-2026-08-19.md`.

The separately approved offline implementation now seeds neutral disposable
authorization-probe sentinels `126` and `128` through the existing controlled
admin schema manifest. The query-only RBAC runner requires those sentinels and
absence of target `127`, emits a sanitized guard marker, and deletes only
absent `127`; it removes the ineffective empty-partition session setting.
Static validation and Goal 6 regression tests pass. This source is not built,
pushed, Terraform-registered, seeded in the live service, or executed. Goal 6
is now **AWAITING SEPARATE APPROVAL TO BUILD AND SCAN THE EXACT NON-EMPTY
DELETE-PROBE VERIFIER IMAGE LOCALLY**. Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-OFFLINE-IMPLEMENTATION-2026-08-19.md`.

The separately approved local-only image checkpoint reverified source aggregate
`181100d9a1cad8b8285369616a32f0f3a9c848ed15f5b198ff11f85f8f79d673` and built
`ask-david-doris-verifier:goal6-nonempty-delete-181100d9`, local OCI digest
`sha256:b2a4629e1e207fa9b2d06cdca5956472f6e4f94e4f40723a5bc45f1a18b17a73`.
Network-disabled non-root inspection confirmed the exact RBAC guard/sentinel
content and all runner shell contracts. Trivy `0.69.3`, using a public DB only,
found zero HIGH/CRITICAL findings in the exact Alpine `3.21.7` image. No Docker
login/ECR push, Terraform, ECS task, Doris SQL, Databricks, or AWS project
operation occurred. Goal 6 is now **AWAITING SEPARATE APPROVAL TO PUSH THIS
EXACT SCANNED LOCAL IMAGE TO A NEW IMMUTABLE DEVELOPMENT ECR TAG**. Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-IMAGE-BUILD-SCAN-2026-08-19.md`.

The separately approved ECR promotion reverified exact source/image values,
then pushed only immutable tag `goal6-nonempty-delete-181100d9` to the private
development verifier repository. Remote ECR digest
`sha256:b2a4629e1e207fa9b2d06cdca5956472f6e4f94e4f40723a5bc45f1a18b17a73`
matches the exact scanned local OCI image; Docker logged out after push. ECR
scan-on-push is enabled but immediate inspection returned
`ScanNotFoundException`, so registry scan findings are NOT RUN—not inferred as
PASS. No Terraform, task definition/task, Doris SQL, Databricks, or unrelated
AWS resource operation occurred. Goal 6 is now **AWAITING SEPARATE APPROVAL TO
UPDATE IGNORED DEVELOPMENT TFVARS, RUN OFFLINE PREFLIGHT, AND CREATE A SAVED
CONNECTED TASK-DEFINITION-ONLY PLAN FOR THIS EXACT IMAGE**. Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-IMAGE-ECR-PUSH-2026-08-19.md`.

The saved development task-definition-only plan with SHA-256
`b7be4075a42d0bf93408ed7d2468a44e150a38f022f8b987fb730084c555e716` was
then applied directly after account and digest revalidation. Terraform reported
exactly `2 added, 0 changed, 2 destroyed`, solely registering revision `13` of
the private Fargate admin-refresh and read-only verifier task definitions; the
old task-definition revisions became inactive. Read-only ECS inspection confirms
both revision `13` definitions are ACTIVE, retain `awsvpc`, Fargate `512` CPU /
`1024` MiB, their separate scoped task roles, and the exact verifier digest
`sha256:b2a4629e1e207fa9b2d06cdca5956472f6e4f94e4f40723a5bc45f1a18b17a73`.
No Goal 6 task is RUNNING. No IAM, KMS, network, security-group, EC2/EBS, ECR,
S3, Databricks, public, or production resource changed, and no task or Doris
SQL ran. Goal 6 is now **AWAITING SEPARATE APPROVAL FOR A ONE-SHOT PRIVATE
ADMIN-REFRESH TO APPLY THE CONTROLLED DISPOSABLE SENTINEL SCHEMA**, after which
the revision-13 RBAC verifier may be approved separately. Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-TASK-DEFINITIONS-APPLY-2026-08-19.md`.

The separately approved one-shot revision-13 private admin-refresh ran as task
`940a073e99c74c2ba67129130549e830` in approved private application subnet
`subnet-034f5f1c9bca753f1`, with no public IP, and stopped with container exit
`1`; no retry ran. Safe, count-only CloudWatch inspection records error code
`1105` and the `TINYINT` marker. The version-controlled schema declares the
disposable `goal6_authorization_probe.probe_id` as signed `TINYINT`, while the
new controlled sentinel row uses `128`, which exceeds its maximum of `127`.
This is a disposable-Doris schema mismatch, not a lakehouse/Unity Catalog
write. The task did not produce its completed marker, so it cannot seed the
sentinels or authorize a revision-13 RBAC verifier run. Goal 6 is now
**AWAITING SEPARATE APPROVAL FOR OFFLINE ANALYSIS AND A DECLARATIVE
DISPOSABLE-PROBE SCHEMA REMEDIATION PLAN**. Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-ADMIN-REFRESH-FAILURE-2026-08-19.md`.

The approved offline schema remediation widens the disposable probe key to
`SMALLINT` and adds the versioned
`doris/migrations/04_recreate_authorization_probe.sql` migration. The admin
runner executes this migration after the base schema; it recreates only the
internal disposable probe and seeds `126`/`128`, preserving absent target
`127`. Shell parsing, Goal 6 static validation, 45 focused regression tests,
and diff integrity all PASS; only pytest cache writes emitted environment
permission warnings. No image, task definition, ECS task, Terraform, AWS, Databricks,
bundle, or Doris connected operation occurred. Goal 6 remains **AWAITING
SEPARATE APPROVAL FOR A NEW IMAGE BUILD/SCAN**.
Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-SCHEMA-OFFLINE-REMEDIATION-2026-08-19.md`.

The separately approved local-only image checkpoint built source aggregate
`6fa3d0c9b55e8fe22916c7448ea44d12de3f750ee047ff6b8cfed34f44458f78` as
`ask-david-doris-verifier:goal6-smallint-probe-6fa3d0c9`, local OCI image ID
`sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88`.
Network-disabled, read-only inspection confirmed the new `SMALLINT` migration,
all runner shell contracts, non-root runtime, and MariaDB `11.4.12`. Trivy
`0.70.0` found zero HIGH/CRITICAL vulnerabilities in the exact Alpine `3.21.7`
image. No Docker login/ECR push, Terraform, ECS task, Doris SQL, Databricks, or
AWS project operation occurred. Goal 6 is now **AWAITING SEPARATE APPROVAL TO
PUSH THIS EXACT SCANNED LOCAL IMAGE TO AN IMMUTABLE DEVELOPMENT ECR TAG**.
Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-SCHEMA-IMAGE-BUILD-SCAN-2026-08-19.md`.

The separately approved ECR promotion then pushed that exact local image to
the immutable development tag
`736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier:goal6-smallint-probe-6fa3d0c9`.
Read-only ECR inspection returned the same digest,
`sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88`.
The repository has scan-on-push enabled, but immediate scan-finding inspection
returned `ScanNotFoundException`; ECR scan findings are therefore UNVERIFIED,
while the prior local Trivy evidence remains PASS. Docker logged out after the
push. No Terraform, ECS task, Doris SQL, Databricks, or unrelated AWS resource
operation occurred. Goal 6 is now **AWAITING SEPARATE APPROVAL TO UPDATE ONLY
IGNORED DEVELOPMENT TFVARS, RUN OFFLINE PREFLIGHT, AND CREATE A SAVED CONNECTED
TASK-DEFINITION-ONLY PLAN FOR THIS EXACT DIGEST**. Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-SCHEMA-IMAGE-ECR-PUSH-2026-08-19.md`.

The separately approved image-input checkpoint updated only ignored development
`terraform.tfvars` to the promoted SMALLINT-remediation digest, passed offline
preflight, and created the saved connected plan
`/tmp/goal-06-rbac-nonempty-delete-probe-smallint-task-definitions-20260819.tfplan`.
The plan SHA-256 is
`79b640a313fc65fb3408d481e1c9833c36ac29ae777e47f0f198b813e5d3f2ff`.
Machine-readable inspection found exactly two `delete,create` replacements:
the admin-refresh and read-only verifier ECS task definitions, with 257
no-ops, zero in-place updates, and no other create/destroy/replacement or
production/public/IAM/KMS/network/EC2/EBS/ECR/Databricks action. No apply or ECS
task ran. Goal 6 is now **AWAITING SEPARATE APPROVAL TO APPLY THIS EXACT SAVED
PLAN**. Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-SCHEMA-TASK-DEFINITIONS-CONNECTED-PLAN-2026-08-19.md`.

The exact approved plan was then applied after hash/account/region/image
revalidation. Terraform reported `2 added, 0 changed, 2 destroyed`, registering
revision `14` for both the private admin-refresh and read-only verifier task
definitions. Immediate read-only ECS inspection confirmed both revisions are
`ACTIVE`, Fargate/`awsvpc`, use the exact SMALLINT-remediation digest, and no
Goal 6 task is running. No task, Doris SQL, ECR push, Databricks operation, or
other AWS resource mutation occurred. Goal 6 is now **AWAITING SEPARATE
APPROVAL FOR ONE PRIVATE ADMIN-REFRESH TASK**; the admin result must be reviewed
before a verifier retry. Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-SCHEMA-TASK-DEFINITIONS-APPLY-2026-08-19.md`.

The separately approved revision-14 private admin-refresh then ran exactly once
through the fail-closed repository wrapper. Task
`394d846105324da08cc8883fe97f63f6` stopped with exit code `0`; the CloudWatch
completion marker was `operation=admin-refresh,status=completed`. It ran in
private subnet `subnet-034f5f1c9bca753f1` at `10.42.25.53` with admin SG
`sg-07a0dd2e8af8aa178`, and the post-run running-task list was empty. No retry,
verifier task, Terraform, ECR, Databricks, or unrelated AWS operation occurred.
Goal 6 is now **AWAITING SEPARATE APPROVAL FOR ONE PRIVATE REVISION-14
READ-ONLY VERIFIER TASK**. Evidence:
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-SCHEMA-ADMIN-REFRESH-CONNECTED-2026-08-19.md`.

The separately approved revision-14 private read-only verifier then ran exactly
once. Task `ee0f6c51b67c41919a34f50a79d48e2f` stopped with exit code `0` and the
`readonly-verify` completion marker. It produced the complete connected result
contract: source dataset `ask_david_development.green_sm_business.goal5_structured_business_metrics`,
refresh timestamp `2026-08-19T09:55:02Z`, query ID
`5f3d5b10fd5b4a08-a24906b966376c6b`, row count `2`, execution duration `0`, and
the representative result. The task ran privately at `10.42.46.180` in
`subnet-0a1aad220d82ef879` with verifier SG `sg-04eb1ebf613ceeadc`; no task was
running afterward. Phase 6-8 is now **PASS**. Goal 6 is **AWAITING SEPARATE
APPROVAL FOR ONE PRIVATE RBAC VERIFIER TASK**; Phase 6-11 remains unverified.
Evidence:
`docs/verification/GOAL-06-PHASE-6-8-READONLY-VERIFIER-CONNECTED-2026-08-19.md`.

The separately approved revision-14 private RBAC verifier then ran exactly
once. Task `1ba950f5ab7f47e490a36bb7afd17022` stopped with exit code `0` in
private subnet `subnet-034f5f1c9bca753f1` at `10.42.28.254`; no task was running
afterward. Positive SELECT returned `2` rows, and all required negative classes
were explicitly denied: INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, and
unauthorized-database access. The non-empty DELETE guard confirmed sentinels
`126` and `128` present with target `127` absent. Phase 6-11 is now **PASS**.
Goal 6 remains partially verified because Phase 6-9 increment/refresh,
Phase 6-10 rebuild, Phase 6-12 query-limit, Phase 6-13 audit, and Phase 6-14
final drift/cleanup still need connected evidence. Evidence:
`docs/verification/GOAL-06-PHASE-6-11-RBAC-VERIFIER-CONNECTED-2026-08-19.md`.

The first separately approved Phase 6-12 query-limit verifier task then ran
exactly once and failed closed before the timeout probe. Task
`ceacc0d27ef348ff84f31af8736be2f6` exited `1` because the query-only identity
used `SHOW PROPERTY FOR 'doris_goal6_query'`, which requires grant-level
visibility. No retry occurred. The minimal offline remediation now uses
current-user `SHOW PROPERTY LIKE 'query_timeout'`; it does not broaden the
query identity's privileges. Phase 6-12 remains **UNVERIFIED** pending a newly
reviewed image/task revision and one connected no-retry retry. Evidence:
`docs/verification/GOAL-06-PHASE-6-12-QUERY-LIMIT-REMEDIATION-OFFLINE-2026-08-19.md`.

The separately approved local Phase 6-12 image checkpoint then built and
scanned the remediated source aggregate
`a4a0f4fd3a003fadd1a9e7ce48c9d3a75dfdf183768dc593df2fbc40847d4b84`. The local
OCI image/index digest is
`sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36`.
Network-disabled non-root inspection passed, and Trivy found zero
HIGH/CRITICAL findings. No ECR push, Terraform, task-definition change, ECS
task, Doris SQL, Databricks, or AWS project operation occurred. Phase 6-12
remains **UNVERIFIED** pending separate promotion, registration, and exactly
one connected no-retry verifier run. Evidence:
`docs/verification/GOAL-06-PHASE-6-12-QUERY-LIMIT-IMAGE-BUILD-SCAN-2026-08-19.md`.

The separately approved Phase 6-12 ECR promotion pushed immutable tag
`goal6-query-limit-a4a0f4fd` to the private development verifier repository.
Read-only inspection confirmed remote digest
`sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36`
matches the scanned local image. ECR scan findings returned
`ScanNotFoundException`, so registry scan status is **UNVERIFIED** while local
Trivy remains PASS. No Terraform, ECS task-definition change, ECS task, Doris
SQL, Databricks, or unrelated AWS operation occurred. Goal 6 is now
**AWAITING SEPARATE APPROVAL TO UPDATE ONLY IGNORED IMAGE INPUT, CREATE A
SAVED TASK-DEFINITION-ONLY PLAN, AND REVIEW IT BEFORE APPLY**. Evidence:
`docs/verification/GOAL-06-PHASE-6-12-QUERY-LIMIT-IMAGE-ECR-PUSH-2026-08-19.md`.

The separately approved Phase 6-12 image-input checkpoint updated only ignored
development `terraform.tfvars` to the promoted query-limit image digest, ran
offline preflight, and created one saved connected development Terraform plan.
The plan SHA-256 is
`c24205563e73adcda4345a1d3707c27807c21a3c701eac3b8469e93f2b982ae1`. Exact
machine-readable inspection found only two ECS task-definition replacements:
`module.doris_verifier.aws_ecs_task_definition.admin[0]` and
`module.doris_verifier.aws_ecs_task_definition.verifier[0]`; both are replaced
only through `container_definitions` to use image digest
`sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36`.
There are zero other creates, updates, replacements, or destroys. No apply or
ECS task ran. Phase 6-12 remains **AWAITING SEPARATE APPROVAL TO APPLY THIS
EXACT SAVED PLAN**. Evidence:
`docs/verification/GOAL-06-PHASE-6-12-QUERY-LIMIT-TASK-DEFINITIONS-CONNECTED-PLAN-2026-08-19.md`.

The exact saved plan was then applied after hash/account/region revalidation.
Terraform reported `2 added, 0 changed, 2 destroyed`, replacing only the
admin-refresh and read-only verifier ECS task definitions. Immediate read-only
inspection confirmed revision `15` of both definitions is `ACTIVE`, Fargate
with `awsvpc`, and uses the exact query-limit image digest
`sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36`.
No task is running and no query-limit verifier task was started. Phase 6-12
remains **AWAITING SEPARATE APPROVAL FOR ONE PRIVATE NO-RETRY QUERY-LIMIT
VERIFIER TASK**. Evidence:
`docs/verification/GOAL-06-PHASE-6-12-QUERY-LIMIT-TASK-DEFINITIONS-APPLY-2026-08-19.md`.

The separately approved private query-limit verifier then ran exactly once
through the fail-closed wrapper from revision `15`. Task
`b8145b93a37c41229382fff01400f638` stopped with exit code `0` in private subnet
`subnet-034f5f1c9bca753f1` at `10.42.27.16`. It confirmed the current query
identity's `query_timeout=30` with `SHOW PROPERTY LIKE`, and bounded
`SLEEP(31)` was enforced after `30` seconds. The CloudWatch marker reported
`status=completed` and `enforcement=timeout`; no retry or write operation
occurred. Phase 6-12 is now **PASS**. Goal 6 remains pending Phase 6-13 audit
and result-contract evidence plus Phase 6-14 final drift/cleanup. Evidence:
`docs/verification/GOAL-06-PHASE-6-12-QUERY-LIMIT-VERIFIER-CONNECTED-2026-08-19.md`.

The separately approved Phase 6-13 admin audit task then ran exactly once from
revision `15` and failed closed. Task
`732ef6a88ea046388810c15f8f77244e` stopped with exit code `1` in private subnet
`subnet-0a1aad220d82ef879` at `10.42.38.69`. Its CloudWatch marker was
`operation=audit-verify,status=audit-row-not-found` for the expected query ID
`5f3d5b10fd5b4a08-a24906b966376c6b`. No retry or second diagnostic task was
run. Phase 6-13 remains **UNVERIFIED**; the repository does not yet prove
whether the gap is retention/timing, query-ID correlation, or another Doris
audit-table condition. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-FAILURE-2026-08-19.md`.

The offline blocker analysis for the Phase 6-13 `audit-row-not-found` failure
is now recorded. The current source performs exact query-ID correlation and
the failure alone does not justify changing privileges, weakening the audit
contract, or claiming a root cause. The minimal next sequence is a separately
approved fresh private read-only result-contract task from verifier revision
`15`, followed by a separately approved audit task using only that fresh
sanitized query ID. If the fresh-ID audit also fails, another offline source
review is required before any executable change. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-REMEDIATION-PLAN-2026-08-19.md`.

The separately approved fresh private result-contract task then ran exactly
once from verifier revision `15`. Task
`84dec5db995f4e61811b57df5e180f20` stopped with exit code `0` in private subnet
`subnet-0a1aad220d82ef879` at `10.42.32.225`. It produced the complete
read-only result contract with fresh query ID
`2259b82920f9455a-a1845feae8876892`, source dataset
`ask_david_development.green_sm_business.goal5_structured_business_metrics`,
refresh timestamp `2026-08-19T15:34:37Z`, row count `3`, and execution duration
`0`. No retry or write operation occurred. Phase 6-13 remains **UNVERIFIED**
until a separately approved audit task correlates this fresh query ID. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-FRESH-RESULT-CONTRACT-CONNECTED-2026-08-19.md`.

The separately approved audit task using that fresh query ID then ran exactly
once and failed closed as well. Task
`ff6cdedf3a7c43038568c5c03544d5e3` stopped with exit code `1` in private subnet
`subnet-034f5f1c9bca753f1` at `10.42.16.113`; CloudWatch again reported
`operation=audit-verify,status=audit-row-not-found`. The fresh-ID retry
hypothesis is therefore rejected. No further task or retry was run. Phase 6-13
remains **UNVERIFIED** and requires a new offline audit source/design review
before any connected operation. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-FRESH-ID-AUDIT-FAILURE-2026-08-19.md`.

The follow-up offline source/design review is complete. It found that the
version-controlled admin migration enables audit logging but the completion
marker does not read back `enable_audit_plugin` or prove that
`__internal_schema.audit_log` is populated; the audit runner consequently
conflates an empty or unavailable log with an exact-ID miss. The proposed
bounded remediation adds read-only guards and distinct fail-closed diagnostics
while keeping exact query-ID correlation and least privilege. No executable
source or cloud state changed in this review. Phase 6-13 remains
**UNVERIFIED** pending separate approval for offline implementation. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-CONTRACT-OFFLINE-REVIEW-2026-08-19.md`.

The approved offline audit-guard implementation is now complete and validated.
The admin and audit runners distinguish plugin-disabled, plugin-unreadable,
empty-log, and unreadable-log states while preserving exact query-ID
correlation and least privilege. Shell parsing, Goal 6 static validation, the
focused regression suite (`46 passed`), and diff checks passed; two pytest
cache-permission warnings were non-failing. The current revision-15 task
definitions do not contain this source change. Phase 6-13 remains
**AWAITING SEPARATE APPROVAL TO BUILD AND SCAN A NEW IMMUTABLE IMAGE** at this
checkpoint. That approval was subsequently completed as the local image
checkpoint recorded below. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-GUARD-OFFLINE-IMPLEMENTATION-2026-08-19.md`.

The separately approved local Phase 6-13 audit-guard image was then built and
scanned from source aggregate
`25b48aea6cbedb2f901b7e959d788fed2f4bc79ece65f49b43efc33f7634907c`. The local
OCI image/index digest is
`sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e`.
Network-disabled non-root inspection passed, and Trivy reported zero
HIGH/CRITICAL findings. No ECR push, Terraform operation, task-definition
change, ECS task, Doris SQL, Databricks, or AWS project operation occurred.
Phase 6-13 remains **AWAITING SEPARATE APPROVAL TO PUSH THIS EXACT IMAGE TO
ECR UNDER A NEW IMMUTABLE TAG**. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-GUARD-IMAGE-BUILD-SCAN-2026-08-19.md`.

The separately approved ECR promotion then pushed exactly immutable tag
`goal6-audit-guards-25b48aea` to the private development verifier repository.
The remote OCI digest
`sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e`
matches the scanned local image. Account, region, repository immutability,
scan-on-push, and destination-tag absence were revalidated before push; Docker
logged out immediately afterward. The immediate registry inspection returned
no scan status, so registry scanning is **UNVERIFIED/NOT RUN** while the local
Trivy scan remains PASS. No Terraform, task-definition, ECS task, Doris SQL,
Databricks, or unrelated AWS operation occurred. Phase 6-13 is now
**AWAITING SEPARATE APPROVAL TO UPDATE ONLY IGNORED IMAGE INPUT, CREATE AND
REVIEW A SAVED TASK-DEFINITION-ONLY PLAN**. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-GUARD-IMAGE-ECR-PUSH-2026-08-19.md`.

The separately approved task-definition checkpoint then updated only the
ignored development `goal_6_verifier_image` input to the promoted audit-guard
digest, passed offline preflight, and created saved plan
`/tmp/goal-06-phase-6-13-audit-guard-task-definitions-20260819.tfplan` with
SHA-256
`b27a1755b130020f09255a87a16239acefc2d929760459b7b734fb36bda84c77`. The
successful textual plan review found exactly two ECS task-definition
replacements, both only at `container_definitions`; all other managed actions
were zero. Terraform formatting, Goal 6 static validation, 46 focused tests,
and diff checks passed. A follow-up `terraform show -json` post-check could
not reload provider schemas due a local plugin-handshake error and is recorded
as UNVERIFIED; the saved plan was not regenerated or applied. Phase 6-13 is
now **AWAITING SEPARATE APPROVAL TO APPLY THIS EXACT SAVED PLAN**. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-GUARD-TASK-DEFINITIONS-CONNECTED-PLAN-20260819.md`.

The exact saved plan was subsequently applied after account, region, and
SHA-256 revalidation. Terraform reported `2 added, 0 changed, 2 destroyed`,
representing only the reviewed admin-refresh and verifier task-definition
replacements. Immediate read-only ECS inspection confirmed revision `16` of
both families is ACTIVE Fargate/`awsvpc` and uses the exact audit-guard image
digest; no task is RUNNING. No new plan, ECS task, Doris SQL, Databricks, ECR,
or unrelated AWS operation occurred. Phase 6-13 is now **AWAITING SEPARATE
APPROVAL FOR ONE PRIVATE ADMIN-REFRESH TASK FROM REVISION 16**. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-GUARD-TASK-DEFINITIONS-APPLY-2026-08-20.md`.

The separately approved private admin-refresh task then ran exactly once from
revision `16`. Task `ace02dffce6242daaea64de45a88571c` stopped with exit code
`0` in private subnet `subnet-034f5f1c9bca753f1` at `10.42.20.84`; its bounded
CloudWatch stream emitted the completed admin-refresh marker and no task
remains RUNNING. No retry, verifier task, Terraform, ECR, Doris SQL,
Databricks, or unrelated AWS operation occurred. Phase 6-13 remains
**AWAITING SEPARATE APPROVAL FOR ONE FRESH PRIVATE READ-ONLY RESULT-CONTRACT
TASK**, followed later by a separate audit task bound to its exact query ID.
Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-GUARD-ADMIN-REFRESH-CONNECTED-2026-08-20.md`.

The separately approved fresh private read-only result-contract task then ran
exactly once from revision `16`. Task `c1f8d389320a4c55b7586d3f5cc78508`
stopped with exit code `0` in private subnet `subnet-0a1aad220d82ef879` at
`10.42.33.239`. It emitted source dataset
`ask_david_development.green_sm_business.goal5_structured_business_metrics`,
refresh timestamp `2026-08-19T17:05:08Z`, query ID
`3688ae5f35c2439d-85b020ada4249d3e`, row count `3`, and execution duration
`0`. No retry or write operation occurred. Phase 6-13 is now **AWAITING
SEPARATE APPROVAL FOR ONE PRIVATE ADMIN AUDIT TASK USING THIS EXACT QUERY ID**.
Evidence:
`docs/verification/GOAL-06-PHASE-6-13-FRESH-RESULT-CONTRACT-2026-08-20.md`.

The separately approved exact-ID audit task then ran exactly once, bound to
query ID `3688ae5f35c2439d-85b020ada4249d3e`. Task
`06b2ae481d3e4605852021314131b529` stopped with exit code `1` in private
subnet `subnet-034f5f1c9bca753f1` at `10.42.21.241`. Its bounded CloudWatch
stream emitted `{"goal":"goal-06","operation":"audit-verify","status":"audit-log-empty"}`.
The wrapper failed closed and did not retry. Phase 6-13 remains
**UNVERIFIED**; the exact query-ID audit contract is not proven. No privilege,
source-data, task-definition, Terraform, ECR, Databricks, or unrelated AWS
mutation occurred after the failed task. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-EMPTY-LOG-FAILURE-2026-08-20.md`.

The owner then performed a read-only FE inspection. It confirmed FE
`doris-port-ready`/listener `ready`, `enable_audit_plugin=true`, installed
built-in `AuditLoader` and `AuditLogBuilder`, an empty `audit_log`, and
`NORMAL/OK` replicas with replication factor `1`. FE `fe.log` contains
`AuditStreamLoader.loadBatch` `SocketTimeoutException: Connect timed out` and
the corresponding failed audit label. This proves the current blocker is the
AuditLoader HTTP batch-delivery path rather than plugin installation, audit
table readability, or replica health. Terraform currently authorizes FE→BE
`9050`/`9060`/`8060` but omits the BE HTTP webserver port `8040`, which the
AuditLoader redirect requires. The offline remediation adds `8040` to the
existing paired SG-to-SG FE→BE rule set while preserving the descriptions of
all existing rules. Static Goal 6 validation, 46 focused regression tests,
Terraform fmt, the Doris-serving mock-provider test (`1 passed, 0 failed`),
and diff checks all passed. The saved connected plan
`goal-06-audit-http-8040-20260820-r2.tfplan` has SHA-256
`2af16e7950852755d85e23fcdda5009673d7e39dddd0db5903a52d855bdbe661` and
reports exactly `2 to add, 0 to change, 0 to destroy`. The hash-bound apply
created only the two TCP/8040 SG-to-SG rules and reported `2 added, 0 changed,
0 destroyed`; read-only inspection confirmed no CIDR/public rule. The one
separately approved audit execution then stopped with exit code `1` and the
CloudWatch marker `audit-log-empty`; no retry occurred. Phase 6-13 remains
**UNVERIFIED**. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-HTTP-8040-OFFLINE-REMEDIATION-2026-08-20.md` and
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-HTTP-8040-APPLY-2026-08-20.md`,
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-HTTP-8040-FAILURE-2026-08-20.md`,
and `docs/verification/GOAL-06-PHASE-6-13-AUDIT-HTTP-8040-STALE-ID-ANALYSIS-2026-08-20.md`.
The fresh post-remediation result-contract task then passed exactly once with
query ID `71e250e78c514a31-8551296f735d0a9a`, exit code `0`, and private IP
`10.42.31.36`. The separately approved fresh-ID audit then passed exactly once
with exit code `0`, `identity_match=true`, `target_match=true`, `state=EOF`,
and `workload_group_match=true`. Phase 6-13 is now **PASS**. Evidence:
`docs/verification/GOAL-06-PHASE-6-13-FRESH-RESULT-CONTRACT-POST-8040-2026-08-20.md`.
`docs/verification/GOAL-06-PHASE-6-13-AUDIT-HTTP-8040-SUCCESS-2026-08-20.md`.

The separately approved Phase 6-14 connected zero-drift/cleanup checkpoint is
now **PASS for the current deployment state**. The isolated Terraform plan
refreshed AWS and Databricks development state and returned `No changes`; its
SHA-256 is
`2bbcb832f1c7929749062c3645705196e62a77d77f4ef184641d4206beadd4d5`.
Independent local JSON inspection found 261 `no-op` resource changes and zero
non-no-op actions. Read-only ECS inspection found no RUNNING task; the
post-increment admin-refresh task `b3314db778e84f47a5bdddaabdd599f0` and
read-only verifier task `9e399737d999478d9f8713d13b2485be` both stopped with
exit code `0`. Persistent FE/BE instances, encrypted root/data volumes, the
Doris log group, and private ECR repository were inventoried without mutation.
This does not complete Goal 6: Phase 6-10 disposable serving-copy rebuild and
the required post-rebuild refresh/read-only comparison remain outstanding and
require a new final zero-drift check afterward. Evidence:
`docs/verification/GOAL-06-PHASE-6-14-ZERO-DRIFT-2026-08-20.md`.

The user then separately approved exactly one private Phase 6-10 rebuild task.
Task `2551e7c4b51949b695bb23b0ee3dd1c5` from admin-refresh revision `16`
stopped with exit code `0` in private subnet `subnet-0a1aad220d82ef879` at
`10.42.40.192`. Its guarded command emitted the completed
`rebuild-serving` marker and targeted only the disposable
`ask_david_serving_development` Doris serving objects. No source-lakehouse,
S3, Terraform, EC2/EBS, Databricks, or retry operation occurred. Phase 6-10
execution is **PASS**; the post-rebuild admin refresh, read-only result
comparison, and a new final zero-drift check remain separately approved
checkpoints. Evidence:
`docs/verification/GOAL-06-PHASE-6-10-REBUILD-CONNECTED-2026-08-20.md`.

After the rebuild, the user separately approved exactly one private admin
refresh task. Task `eb63cf05deb14c89bf3f84a855602994` from revision `16`
stopped with exit code `0` in private subnet `subnet-0a1aad220d82ef879` at
`10.42.44.42` and emitted the sanitized `admin-refresh/completed` result. The
allowlisted source-to-serving refresh sequence completed without retry or
source-lakehouse mutation. Post-rebuild refresh is **PASS**; read-only result
comparison and a new final zero-drift check remain separately approved.
Evidence:
`docs/verification/GOAL-06-PHASE-6-10-ADMIN-REFRESH-POST-REBUILD-2026-08-20.md`.

The separately approved post-rebuild private read-only verifier then ran
exactly once from revision `16`. Task `a6bf93c1a8f74340915646413d8fcd16`
stopped with exit code `0` in private subnet `subnet-0a1aad220d82ef879` at
`10.42.42.187` and emitted `readonly-verify/status=completed`. Its result
contract reported the allowlisted source dataset
`ask_david_development.green_sm_business.goal5_structured_business_metrics`,
representative result `2026-02-01` / `alpha` / event count `1` / metric total
`10.5`, row count `3`, source transformation timestamp
`2026-08-13T04:24:56Z`, refresh timestamp `2026-08-20T07:05:13Z`, and query ID
`cdeff0f1ea78492e-867402ae1eb1156d`. The controlled source-to-serving
projection and result contract are now PASS after rebuild. No retry or source
write occurred. Goal 6 remains **AWAITING SEPARATE APPROVAL FOR A NEW FINAL
CONNECTED PHASE 6-14 ZERO-DRIFT/CLEANUP PLAN**. Evidence:
`docs/verification/GOAL-06-PHASE-6-10-READONLY-POST-REBUILD-2026-08-20.md`.

The separately approved final connected Phase 6-14 zero-drift plan was created
after the post-rebuild comparison. Saved plan
`/tmp/goal6-final-post-rebuild-zero-drift-20260820.tfplan` has SHA-256
`e520bdd87b083fc95aa5f97555f1b8825497926df3b387c5d62495a79e3e1497`.
Machine-readable inspection found `261` resource changes, all `no-op`, with
zero creates, updates, replacements, or destroys. Read-only STS identity
matched account `736956442295`; the ECS `RUNNING` task list was empty. The
complete 52-item acceptance matrix is recorded in
`docs/verification/GOAL-06-FINAL-ACCEPTANCE-2026-08-20.md`. Technical Goal 6
acceptance evidence is complete and the evidence commit is immutable; this
status update is intentionally a separate status-only commit under the
repository freshness rule. No plan was applied.

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
