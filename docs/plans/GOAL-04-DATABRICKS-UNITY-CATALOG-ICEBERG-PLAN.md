# Goal 4 — Databricks, Unity Catalog, and managed Apache Iceberg

## Status and approval boundary

This Phase 4-1 implementation design, including the single-catalog hierarchy
and staged `bootstrap -> validation -> active` sequence, was approved by the
project owner on `2026-08-10` for Phase 4-2 offline implementation only. After
the first bootstrap apply exposed AWS's not-yet-existing self-principal
constraint, the project owner separately approved the documented two-step
`initial role -> self-trust -> validation -> active` remediation for offline
implementation. This plan is not a completed connected-verification record.
Phase 4-0 read-only discovery is recorded in
`docs/verification/GOAL-04-PHASE-4-0-PREFLIGHT-2026-08-10.md`.

No AWS or Databricks resource may be created, updated, replaced, or deleted
under the Phase 4-2 approval. Every later connected Terraform plan and apply has its own explicit approval
boundary. A bundle deployment or synthetic SQL run is also a separate
connected mutation and cannot be inferred from Terraform approval.

## Fixed scope

Goal 4 establishes a development-only governed lakehouse foundation:

```text
neutral synthetic input
  -> Raw / Bronze managed Iceberg
  -> Curated / Silver managed Iceberg
  -> Business / Gold managed Iceberg
```

Unity Catalog remains the metadata, authorization, audit, and lineage
authority. Data and Iceberg metadata remain in the approved Goal 3 S3 buckets.
Databricks SQL performs the synthetic transformations. Apache Doris,
OpenSearch retrieval, the Goal 5 ingestion framework, controlled tool
services, LangGraph, agents, real Green SM data, and Green SM business logic
remain out of scope. AWS Glue is not introduced as a catalog.

The existing metastore, metastore assignment, system catalogs, workspace
catalogs, and serverless SQL warehouse are references only. Goal 4 does not
create or import a metastore, change its assignment, repurpose an existing
catalog, or create a classic cluster.

## Phase 4-0 facts used by this design

- Databricks profile: `ask-david-development`, OAuth U2M.
- Workspace ID: `7474644358733471`.
- Workspace Region: `ap-southeast-1`, proven by the attached regional
  metastore.
- Existing metastore: `3a7f7e7a-680b-4bd6-907a-6d5e77b43178`.
- Existing serverless SQL warehouse: `Serverless Starter Warehouse`, ID
  `757e0335c6efb51e`, Small, one cluster maximum, 10-minute auto-stop.
- AWS account: `736956442295`; Region: `ap-southeast-1`.
- Existing system/project-unrelated catalogs and credentials must remain
  untouched.
- The exact commercial workspace SKU label and creation date were not exposed
  by the available account API. Required Unity Catalog and serverless
  capabilities are directly operational.

All identifiers above are environment configuration, not secrets. They must be
validated again immediately before every connected plan or operation.

## Approved namespace hierarchy

The repository does not say whether these roadmap names are catalogs or
schemas:

- `green_sm_raw`
- `green_sm_curated`
- `green_sm_business`
- `green_sm_ai`
- `green_sm_platform`
- `green_sm_sandbox`

The proposed hierarchy is:

```text
ask_david_development                         # one isolated development catalog
  green_sm_raw                                # schema: Bronze
  green_sm_curated                            # schema: Silver
  green_sm_business                           # schema: Gold
  green_sm_ai                                 # schema: neutral document metadata
  green_sm_platform                           # schema: audit and quality evidence
  green_sm_sandbox                            # schema: isolated technical scratch area
```

This proposal makes the catalog the environment boundary and the schemas the
data-product/medallion boundaries. A later staging or production environment
can receive a separate catalog without renaming the six roadmap namespaces.
The development catalog can be isolated and bound only to workspace
`7474644358733471`.

The alternative of six top-level catalogs would make environment isolation
and future promotion naming ambiguous and would multiply catalog bindings and
ownership surfaces. The proposed single-catalog hierarchy therefore has the
smaller and clearer authorization boundary.

The project owner approved this hierarchy for offline implementation on
`2026-08-10`. That approval does not approve creating the catalog or schemas.

## Terraform ownership and state boundary

### Environment state

Extend the existing development Terraform root and encrypted remote state:

```text
infrastructure/environments/development
backend key: development/terraform.tfstate
```

This environment state already owns the S3 buckets and KMS key required by
Goal 4. Keeping the AWS IAM/KMS integration and dependent Unity Catalog
resources in the same graph:

- avoids hard-coded bucket and KMS values;
- avoids two Terraform states trying to manage one KMS key policy;
- lets the provider-generated storage-credential external ID feed the exact
  IAM trust policy declaratively;
- permits one saved plan to be separated into AWS and Databricks action lists;
- preserves the existing encrypted, locked backend rather than adding another
  backend or state bucket.

No Goal 3 resource is redesigned. The only in-place Goal 3 extension is the
storage KMS key policy required for the new Unity Catalog IAM role. Existing
storage outputs are made explicit for tests and operator inspection.

### Provider authentication

Add `databricks/databricks ~> 1.122.0` to the development root and lock the
resolved provider checksum. Its workspace-level configuration uses:

```text
profile = ask-david-development
host    = the approved workspace host
```

No PAT, OAuth token, client secret, or credential path is accepted as a
Terraform variable or output. The local OAuth cache remains outside the
repository. The provider must verify the current metastore, current user,
warehouse, and workspace IDs through data sources or check conditions before
planning managed resources.

Account-level OAuth is required to create account identities, assign them to
the workspace, and grant the Service Principal User role. A separate named
OAuth profile `ask-david-account` must be created interactively and verified
read-only before such resources are planned. The account provider uses the
Databricks account host and the already-discovered account ID; the workspace
provider continues to use `ask-david-development`. No account PAT or
service-principal secret will be created for Goal 4.

The host currently has the Databricks CLI and Docker but no native Terraform
binary. Docker-based Terraform cannot safely consume the host OS-keyring OAuth
session by default. Offline mocked validation can remain containerized, but a
connected Databricks plan requires either a user-installed native Terraform
compatible with the repository constraint or a separately approved,
checksum-verified ephemeral HashiCorp binary under `/tmp`. The OAuth cache must
not be downgraded to plaintext merely to make a container work.

## Expected AWS resources and changes

### New resources

1. One development-only IAM role, for example
   `ask-david-development-unity-catalog-storage`.
2. One `aws_iam_role_policy` inline policy attached only to that role.
3. Seven zero-byte, trailing-slash `aws_s3_object` markers, one at each
   approved catalog/schema managed-storage root. Terraform owns these markers
   so an otherwise empty S3 prefix is addressable during Databricks
   `PATH_EXISTS` validation. Every marker is explicitly encrypted with the
   existing storage KMS key and contains no synthetic record or business data.

The role permits only:

- required S3 bucket metadata/list operations on approved buckets, with list
  operations restricted to the managed prefixes where AWS condition support
  permits;
- get, put, delete, multipart, and abort operations on the exact managed
  prefixes;
- `kms:Encrypt`, `kms:Decrypt`, `kms:ReEncrypt*`,
  `kms:GenerateDataKey*`, and `kms:DescribeKey` on the existing storage KMS
  key;
- `sts:AssumeRole` on itself in the identity policy, ready for the separately
  approved trust-policy self-assumption sub-step.

It receives no AWS console access, static credentials, wildcard bucket
resources, Glue permission, non-storage service permission, or permissions for
RDS, Redis, ECS, OpenSearch, Secrets Manager, or Terraform state.

The initial-role trust policy contains exactly:

- the Databricks Unity Catalog AWS principal returned by the storage
  credential/provider (the documented standard-partition default is
  `arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL`);
- `sts:ExternalId` equal to the external ID generated for the project storage
  credential.

Only after that IAM role exists does a second, separately reviewed plan update
the trust policy in-place to add the role's own ARN for self-assumption. The
root input `goal_4_storage_role_self_assumption_enabled` defaults to `false`;
the ignored development tfvars may change it to `true` only after the
initial-role apply succeeds. This ordering avoids an AWS `Invalid principal`
error from naming a role in its own trust policy before AWS has created it.

The external ID is not guessed or copied into source. Terraform obtains it
from `databricks_storage_credential.aws_iam_role[0].external_id`.

The storage integration is deliberately staged. `bootstrap` owns only the
credential plus its AWS role/policy/KMS prerequisites and contains two apply
sub-steps: initial role creation with self-assumption disabled, then an in-place
trust update with self-assumption enabled. Credential validation occurs only
after both applies succeed. `active` is rejected unless self-assumption is
enabled and adds locations, namespaces, identities, and grants only after a
read-only credential validation succeeds. This prevents a failed storage
assumption from partially creating the governed namespace.

### In-place change

Update the existing storage KMS key policy to retain account-root delegation
and explicitly allow only the new Unity Catalog storage role the required
cryptographic operations. Expected replacement and destroy counts are zero.

### Existing AWS resources reused unchanged

- Raw, Curated, Business, Documents, Artifacts, Audit, and Logs buckets.
- Storage KMS key and alias.
- Terraform state bucket and state KMS key.

No new S3 bucket, VPC, subnet, NAT gateway, endpoint, security group, instance,
cluster, Glue database/catalog, or long-running compute resource is expected.
File-event SNS/SQS permissions are excluded because file arrival and Auto
Loader belong to Goal 5.

## S3 managed-storage layout

Create isolated Unity Catalog external locations over non-overlapping managed
prefixes, not over whole buckets for user-facing file access:

| Unity Catalog object | Approved S3 storage root |
| --- | --- |
| Development catalog fallback | Artifacts bucket `/unity-catalog/development/catalog` |
| `green_sm_raw` schema | Raw bucket `/unity-catalog/development/green_sm_raw` |
| `green_sm_curated` schema | Curated bucket `/unity-catalog/development/green_sm_curated` |
| `green_sm_business` schema | Business bucket `/unity-catalog/development/green_sm_business` |
| `green_sm_ai` schema | Documents bucket `/unity-catalog/development/green_sm_ai` |
| `green_sm_platform` schema | Audit bucket `/unity-catalog/development/green_sm_platform` |
| `green_sm_sandbox` schema | Artifacts bucket `/unity-catalog/development/green_sm_sandbox` |

The catalog has a fallback managed root, while every required schema has an
explicit managed root so its storage purpose remains deterministic. Each root
contains only a Terraform-owned zero-byte marker at `<root>/` before Unity
Catalog use. Unity Catalog appends its own `__unitystorage` paths. SQL table
definitions never contain `LOCATION`; this is the key managed-table invariant.

Each external location and the storage credential use isolated mode and are
bound only to the approved development workspace. `fallback` and direct file
access are disabled. Only the Terraform governance owner receives the
temporary `CREATE MANAGED STORAGE` capability needed to configure roots. Data
engineers, workflow identities, readers, and denied-test identities receive no
`READ FILES`, `WRITE FILES`, `CREATE EXTERNAL TABLE`, `CREATE EXTERNAL VOLUME`,
or storage-credential privilege.

## Expected Databricks Terraform resources

### References/checks only

- current user;
- current metastore and its Region/ID;
- current workspace ID;
- existing serverless SQL warehouse ID and configuration;
- collision checks for project catalog, identities, storage credential, and
  external locations.

There is no `databricks_metastore` or `databricks_metastore_assignment`
resource.

### Persistent resources

1. One isolated storage credential backed by the new AWS IAM role.
2. Seven isolated external locations for the roots in the table above.
3. One isolated catalog, `ask_david_development`.
4. Six schemas with the exact roadmap names.
5. Workspace bindings for the storage credential, external locations, and
   catalog to workspace `7474644358733471` in read-write mode where supported.
6. Account identities created with the account provider and assigned only to
   the development workspace with `USER` access:
   - `ask-david-development-governance-admins` group;
   - `ask-david-development-data-engineers` group;
   - `ask-david-development-business-readers` group;
   - `ask-david-development-lakehouse-workflow` service principal;
   - `ask-david-development-denied-test` service principal.
7. Workspace entitlements for the two service principals: workspace and SQL
   access enabled; cluster and instance-pool creation disabled.
8. Group membership and account-level Service Principal User role needed to
   run the acceptance jobs as the two test principals.
9. Unity Catalog grants described below.

The Service Principal User/Manager rule sets are authoritative. Each new
service principal therefore has exactly one
`databricks_access_control_rule_set` containing every intended grant rule. The
governance-admin group receives manager and user roles; no second Terraform
resource may manage the same rule-set name. This avoids overwriting an implicit
creator rule with an incomplete ACL.

The service principals have workspace and Databricks SQL access only. Cluster
creation and instance-pool creation are false. No OAuth client secret or PAT is
created. The existing `users` warehouse ACL is expected to provide `CAN_USE`;
the plan must stop if it does not. The existing warehouse and its current ACL
are not imported, recreated, resized, or otherwise managed by Goal 4.

## Least-privilege grant model

### Governance administrators

- own/manage the new catalog, schemas, credential, and locations;
- receive only privileges required to maintain those project objects;
- contain the current verified administrator for development;
- receive no account-admin or metastore-admin role from Goal 4.

### Data engineers and workflow principal

- `USE CATALOG` on `ask_david_development`;
- `USE SCHEMA`, `SELECT`, and `MODIFY` only where the SQL workflow reads or
  writes;
- `CREATE TABLE` only during the approved bundle/acceptance deployment if
  SQL, rather than Terraform, creates the managed Iceberg tables;
- no direct external-location or storage-credential privilege.

The workflow service principal is a member of the data-engineers group and is
the `run_as` identity for the authorized synthetic pipeline job.

### Business readers

- `USE CATALOG`;
- `USE SCHEMA` and `SELECT` only on `green_sm_business`;
- no Raw, Curated, Platform, AI, Sandbox, storage credential, or external
  location privilege.

### Denied test principal

- workspace/SQL access sufficient to submit the negative acceptance query;
- top-level bundle `CAN_VIEW` solely to read synchronized neutral SQL files;
- no bundle `CAN_RUN`, `CAN_MANAGE`, edit, or deploy permission;
- no `USE CATALOG`, `USE SCHEMA`, `SELECT`, storage credential, external
  location, S3, KMS, or AWS IAM permissions.

It must fail both a protected-table query and a direct approved-S3-path query.
The expected authorization failure is evidence; unexpected success stops the
goal immediately.

Grant resources must be authoritative per securable. The implementation must
not split multiple `databricks_grants` resources over the same securable and
must preserve owner access explicitly.

## Existing Serverless SQL reuse and cost controls

All SQL tasks use existing warehouse `757e0335c6efb51e`:

- Small;
- serverless;
- maximum one cluster;
- 10-minute auto-stop.

No SQL warehouse or classic/all-purpose/job cluster is created. Before every
billable SQL execution, report the warehouse name, size, serverless status,
current state, and auto-stop value. Runs are one-shot and deterministic. After
verification, read-only inspection must show the warehouse stopped or in its
documented auto-stop window, with no temporary compute left running.

If a required acceptance capability cannot run as a SQL task on this
warehouse, stop and report the exact capability, minimum serverless/job
compute, and cost before proposing any additional compute.

## Declarative Automation Bundle

Create one development target under `databricks/bundles/goal_04_lakehouse`.
The bundle references, rather than creates, the existing workspace and
warehouse. It deploys SQL files and one-shot jobs only.

Proposed tasks:

```text
bootstrap_managed_iceberg
  -> load_raw_synthetic
  -> build_curated
  -> build_business
  -> run_quality_checks
  -> record_execution_audit
  -> verify_table_types_and_history
  -> verify_lineage
```

Task dependencies are explicit. The authorized job runs as the workflow
service principal. Separate negative jobs run as the denied-test principal:

- `deny_protected_table_access`;
- `deny_direct_s3_path_access`.

The bundle target fixes the catalog, warehouse ID, and environment from
non-secret variables. The approved named Databricks CLI profile exclusively
selects the workspace host and OAuth authentication; the bundle must not
declare an interpolated host mapping. Its deployment root is scoped to
`/Workspace/Users/${var.governance_admin_user_name}/.bundle/` rather than
`/Workspace/Shared`. Offline implementation uses local YAML/schema checks;
connected `databricks bundle validate` is read-only and occurs later against
the approved target. Bundle deploy and run are separate connected approvals.

## Managed Apache Iceberg tables

All physical tables use explicit `USING ICEBERG` and omit `LOCATION`. A
post-create assertion must show provider/catalog metadata identifying the
table as managed Apache Iceberg, not Delta and not external.

The minimum table set is:

| Category | Proposed table | Purpose |
| --- | --- | --- |
| Event-like structured data | `ask_david_development.green_sm_raw.synthetic_events` | Deterministic Bronze input |
| Curated event flow | `ask_david_development.green_sm_curated.synthetic_events` | Validated/deduplicated Silver records |
| Entity master data | `ask_david_development.green_sm_curated.synthetic_entities` | Neutral entity reference data |
| Aggregated metrics | `ask_david_development.green_sm_business.synthetic_metrics` | Gold aggregation from Curated |
| Document metadata | `ask_david_development.green_sm_ai.synthetic_document_metadata` | Neutral document identifiers and technical attributes only |
| Agent execution audit | `ask_david_development.green_sm_platform.synthetic_agent_execution_audit` | Generic future-runtime audit shape; no agent implementation |
| Data quality results | `ask_david_development.green_sm_platform.synthetic_data_quality_results` | Durable assertion outcomes |

The six required categories are covered; the extra Curated event table makes
the Raw-to-Curated-to-Business flow directly testable. The phrase `agent
execution audit` is only the generic table category required by Goal 4. It
does not implement a LangGraph runtime, Supervisor, sub-agent, or tool service.

Synthetic rows use fixed identifiers, timestamps, numeric values, and neutral
labels such as `entity-001` and `event-001`. No Green SM names, identifiers,
metrics, documents, domains, policies, formulas, or business semantics appear.
The workflow is idempotent by deterministic keys and `MERGE`/replacement rules
that cannot duplicate the fixed acceptance dataset.

## Quality, history, lineage, and audit strategy

### Deterministic data quality

At minimum, write PASS/FAIL rows for:

- fixed expected Raw row count;
- required-column non-null checks;
- unique event and entity identifiers;
- accepted neutral status-domain values;
- Curated rejection count and duplicate count;
- Business aggregate reconciliation against Curated;
- all six generic table categories present;
- all physical tables managed and `ICEBERG`.

Any failed required assertion makes the job fail after recording its result.

### Iceberg history

Perform at least two approved writes on an acceptance table, then use
`DESCRIBE HISTORY` and a version/time-travel read to prove multiple managed
Iceberg versions are inspectable. Retention remains at Databricks defaults for
Goal 4; no cost-increasing retention extension is introduced.

### Lineage

Verify Raw -> Curated and Curated -> Business edges through Catalog Explorer
or the lineage API/system table. Prefer the durable read-only query against
`system.access.table_lineage` if that system schema is enabled. If it is not
enabled, stop before enabling it because enabling a system schema is a
persistent metastore mutation not included in this plan; use an existing
lineage API/UI read-only view as the fallback evidence.

The approved deterministic SQL contract filters both source and target to the
Terraform-managed development catalog and fails unless both directed edges are
present:

- `green_sm_raw.synthetic_events` ->
  `green_sm_curated.synthetic_events`;
- `green_sm_curated.synthetic_events` ->
  `green_sm_business.synthetic_metrics`.

Returning zero rows is not acceptance evidence. The verification query must
remain read-only and use assertions so a missing edge fails the job.

### Auditability

- Query/job run records identify the workflow service principal.
- Unity Catalog grants and object ownership are queryable.
- System audit tables are used read-only if already enabled.
- The execution-audit table records only synthetic run identifiers, task
  status, row counts, timestamps, and non-sensitive error classes.
- No token, credential, SQL connection string, S3 signed URL, or secret value
  is emitted to logs or verification reports.

## Authorized and denied acceptance tests

1. Run the pipeline once as the workflow service principal and require all
   expected reads/writes and quality assertions to succeed.
2. Run a table query as the denied service principal and require the
   principal-specific Unity Catalog `INSUFFICIENT_PERMISSIONS` error with
   SQLSTATE `42501` after the synchronized SQL file is loaded.
3. Run a direct path query as the denied service principal and require Unity
   Catalog to reject the managed-storage URL with `LOCATION_OVERLAP`. This is
   a structural managed-path control, not a principal-specific decision, so it
   counts only when the policy inspections in steps 4 and 5 are also clean.
4. Inspect AWS IAM and KMS policies read-only and prove that neither
   Databricks service principal has an AWS identity or direct bucket/key grant.
5. Inspect Unity Catalog grants and prove that only the governance owner can
   configure managed storage and that data principals cannot use external
   locations directly.

The protected-table test must match its expected authorization error class.
The managed-path test must match `LOCATION_OVERLAP` and must never be used by
itself to claim principal-specific denial. Network, syntax, missing-object,
workspace-file, or compute errors do not count as access rejection.

## Expected repository changes after design approval

### Infrastructure

- extend `infrastructure/environments/development/{versions.tf,providers.tf,variables.tf,locals.tf,main.tf,outputs.tf}`;
- extend its example tfvars and Terraform tests;
- add `infrastructure/modules/databricks-aws-storage/` for IAM and scoped
  S3/KMS role-policy construction;
- extend `infrastructure/modules/kms/` with an optional exact storage-access
  role so the existing key receives an in-place policy update;
- add separate Databricks storage-credential, account-identity, and lakehouse
  modules so the staged dependency graph has no cycle;
- update TFLint/Trivy exclusions only if a documented false positive exists;
  security checks must not be weakened globally.

### Databricks assets

- replace the placeholder-only `databricks/README.md` with Goal 4 usage and
  boundaries;
- create `databricks/bundles/goal_04_lakehouse/` bundle configuration;
- create versioned SQL files under `databricks/sql/goal_04/`;
- add static/contract tests under the repository `tests/` tree;
- no notebook or Python/Spark job is expected.

### Developer tooling and documentation

- add safe offline Databricks format/static/bundle-schema validation commands
  to `Makefile`, `scripts/dev.py`, and `scripts/dev.ps1`;
- add credential-free CI for Terraform/provider schema, SQL/static contracts,
  and bundle validation that performs no workspace deployment or SQL run;
- update repository structure, security, infrastructure, development, and
  runbook documents;
- create a Goal 4 runbook and later a separate verification report;
- update `docs/PROJECT_STATUS.md` at each durable checkpoint, but never mark
  Goal 4 `VERIFIED` until connected verification and an immutable evidence
  commit exist.

Local `terraform.tfvars`, `backend.hcl`, OAuth caches, Terraform state, saved
plans, SQL result artifacts containing identifiers, and credentials remain
ignored and untracked.

## Offline implementation validation

The Phase 4-2 implementation will define repository commands equivalent to:

```text
terraform fmt -check -recursive infrastructure
terraform init -backend=false
terraform validate
terraform test with mocked AWS and Databricks providers
tflint
trivy config
Databricks bundle schema/YAML static validation without workspace access
SQL static assertions for explicit USING ICEBERG and absence of LOCATION/DELTA
Ruff
mypy
pytest with coverage
Bandit
pip-audit
detect-secrets
pre-commit --all-files
git diff --check
```

Offline tests must prove:

- no metastore or metastore-assignment resource;
- no SQL warehouse, cluster, Glue, Goal 5+, or future-agent resource;
- every physical table uses `USING ICEBERG` and no table specifies `LOCATION`;
- every storage root is built from Goal 3 Terraform outputs;
- role trust always includes the exact external ID and UC principal, adds the
  self-principal only through a disabled-by-default flag, and blocks `active`
  while that flag is false;
- S3/KMS permissions are prefix/key scoped;
- identity entitlements prohibit cluster creation;
- workspace bindings target only the development workspace;
- no secrets or real data are present.

Offline validation cannot prove live IAM assumption, KMS/S3 access, managed
Iceberg behavior, lineage, authorization rejection, or zero drift.

## Connected execution sequence and approval gates

### Phase 4-3 — saved connected plan

1. Reverify Databricks OAuth identity, workspace, metastore, warehouse, and
   AWS account/Region.
2. Initialize only the already-approved encrypted development backend.
3. Keep `goal_4_storage_role_self_assumption_enabled = false` and create the
   initial-role `bootstrap` saved development plan.
4. Render plan JSON locally and report AWS and Databricks actions separately.
5. Require: no metastore, assignment, existing catalog, existing warehouse,
   production, destroy, or replacement action.
6. On a clean deployment, expected managed-resource actions are exactly one
   storage credential create, one IAM role create, one inline role-policy
   create, seven managed-root marker creates, and one in-place storage KMS
   key-policy update. The historical initial-role remediation occurred before
   marker implementation and therefore contained only the IAM role/policy
   creates and KMS update. No external location, catalog, schema, identity,
   grant, binding, warehouse, or job exists in a bootstrap plan.
7. Hash the saved plan and stop for approval of that exact SHA-256.

Because the credential's external ID is computed at apply, the `bootstrap`
plan uses an ignored local stage input to set `skip_validation = true` only for
credential creation. The initial IAM trust consumes the generated external ID
and contains only the Databricks UC principal. After the initial-role apply
succeeds, set the ignored self-assumption flag to `true`, create a new saved
plan, and require that its only managed-resource action is an in-place IAM role
trust-policy update adding the role's own ARN. Hash and approve that exact plan
separately. No governed namespace is enabled in either bootstrap sub-step.

Never reuse a saved plan after any partial or successful apply. The failed
bootstrap plan SHA-256
`d7ee6ac5e85b2d067210798dc1e9462d21747c505befeb5e26a6352c9d4bd735`
is retained only as forensic evidence and is stale.

The approved initial-role plan SHA-256
`2ddc27a4336db94dbb9b159af1b4d2389752e017f0260635c0e5bfa4b6cb0d6d`
applied as `2 added, 1 changed, 0 destroyed`. The approved self-assumption
trust-policy plan SHA-256
`395828d28b26aae401dae740c69f9b20693dae7a5c34d0764278c12c797d5c59`
applied as `0 added, 1 changed, 0 destroyed`.

The first approved credential validation then returned `PASS` for `READ`,
`LIST`, `WRITE`, and `DELETE`, but `FAIL` for the distinct `PATH_EXISTS`
operation. The response contained no failure message; the result is consistent
with the approved S3 prefix having no durable object after the temporary
validation object was deleted. Goal 4 stopped as required. The declarative
remediation adds the seven KMS-encrypted markers above. Before a second
credential validation, create and review a new saved development plan whose
expected managed-resource actions are exactly seven `aws_s3_object` creates,
with zero update/replacement/destroy and zero Databricks action. Apply that
exact saved plan only with separate approval.

After the marker apply succeeds, request separate approval and run exactly one
credential validation equivalent to:

```text
databricks storage-credentials validate
  --storage-credential-name <terraform-owned-name>
  --url <approved-raw-managed-prefix>
```

Do not run this validation until the trust-policy-only apply succeeds. Do not
print temporary credentials. All validation checks, including role assumption
and S3/KMS operations, must PASS. A failure stops the goal and requires a
declarative correction plus a new saved plan.

Only after every validation operation, including `PATH_EXISTS`, passes, change
the ignored local stage input to `active`.
The safe source default remains strict validation (`skip_validation = false`).
Create a second saved plan that may update the credential validation flag and
create only the reviewed external locations, bindings, catalog, schemas,
identities, memberships, entitlements, rule sets, and grants. Its AWS action
count must be zero. Hash and review that exact plan separately. No source
hotfix, targeted apply, or ad-hoc CLI/UI fix is allowed between stages.

### Phase 4-4 — exact saved-plan apply

For each approved plan:

- reverify identity/account/workspace/Region;
- verify the saved-plan hash;
- apply only that file;
- stop on any error;
- inspect resources read-only;
- never generate an implicit replacement plan.

### Phase 4-5 — bundle and SQL

After Terraform verification:

1. report warehouse state/cost controls;
2. review the exact bundle manifest and synchronized file set;
3. run connected read-only `databricks bundle validate` against the exact
   development target;
4. separately request approval to deploy the exact bundle;
5. separately request approval to run the one-shot authorized workflow and
   negative jobs;
6. do not add compute.

The first separately approved strict connected bundle validation ran exactly
once after the active-stage apply and stopped before deployment. Databricks
CLI `1.11.0` could not resolve `workspace.host: ${var.workspace_host}` before
matching the named profile, so validation exited `1`. The warehouse remained
stopped, no cluster/session/job appeared, and no bundle state directory was
created. The approved offline remediation removes the bundle host variable
and both host mappings, relies solely on
`--profile ask-david-development`, and moves `root_path` from
`/Workspace/Shared` to the governance administrator's user-scoped workspace
path. A second strict connected validation requires a new, separate approval.

The second separately approved strict connected validation also ran exactly
once and stopped before deployment. The host/profile error was resolved, but
strict mode rejected one workspace-folder permission warning: the
user-scoped root inherited `CAN_MANAGE` for the governance administrator while
the bundle ACL declared only groups. The CLI also recommended placing
`root_path` directly under the production-mode development target. It created
only the ignored local `databricks/.databricks/.gitignore`; no deployment,
job/SQL run, Terraform operation, or AWS mutation ran. The approved second
offline remediation moves the same user-scoped path to
`targets.development.workspace.root_path` and declares the existing governance
administrator user as `CAN_MANAGE`. A third strict connected validation
requires another separate approval.

The third separately approved strict connected validation ran against bundle
SHA-256
`a3c4d178fc44afe19691403dd3a746822e24f88e53782432f2f51f0ae6c394e7`
and resource-manifest SHA-256
`8ce89a428d0521344b279a767afaf02051fcdffaeae85ea2f13662745505f919`.
Databricks CLI `1.11.0` exited `0` with `Validation OK!`, no warning, and no
recommendation. It did not deploy or run a task. The next boundary is separate
approval to deploy the exact validated five-job bundle and 12 synchronized SQL
files, followed by read-only inspection and another stop before any workflow
execution.

The separately approved historical deployment of aggregate source SHA-256
`022cebf1d12e8a22d5e9f7f57b1a5d9d4ca28dede7f71666b09ea1bfc318ec7e`
then completed with exit `0`. Read-only inspection verified exactly five jobs,
12 top-level synchronized SQL files, correct identities/warehouse references,
no active runs, warehouse `STOPPED`, and no cluster. A later read-only
inspection found the nested destructive remediation SQL too; this is superseded
by the explicit-exclude remediation documented below. The next boundary is
separate approval for one execution of the eight-task authorized pipeline job
`967410491586823`; history, lineage, and negative jobs remain unexecuted.

That separately approved pipeline execution completed as one-time run
`347925882630202`, `TERMINATED/SUCCESS`. All eight tasks used the existing
warehouse and succeeded at attempt `0`; no active run remained. The next
boundary is separate approval for one read-only execution of history job
`695423086105630`, followed by another stop before lineage or negative tests.

The first separately approved history run `952431524488579` failed at attempt
`0` before returning metadata because the current Serverless SQL parser
rejected `||` inside `DESCRIBE DETAIL IDENTIFIER(...)`. It was not retried.
The approved offline remediation selects the approved catalog once through
`USE CATALOG IDENTIFIER(:catalog_name)` and uses static schema-qualified table
names for every `DESCRIBE` and the version-1 read. A new strict validation and
redeployment require separate approvals before a history retry.

The separately approved strict connected validation of remediated aggregate
source SHA-256
`9714d971417979d131d23f051519f10cb83392b9aa7927a33af4d68840691c4e`
then passed with exit `0`, no warning, and no recommendation. The next boundary
is separate approval to redeploy that exact source set, followed by read-only
inspection and another stop before any history retry.

The separately approved redeployment then completed successfully. Read-only
inspection confirmed unchanged five-job identities/task counts and a deployed
history-file hash matching
`7b521c1f5d4a24d55a0c6658a87c7d0703b35994ee58bc98f01e1062cdfa3927`.
The next boundary is separate approval for exactly one remediated history retry
of job `695423086105630`.

That remediated history retry completed as run `966938583513350`,
`TERMINATED/SUCCESS`, at attempt `0`. Seven table-detail statements, Raw
history, and the version-1 assertion all executed successfully. Review of the
next lineage SQL found an acceptance gap: it only returns Raw-to-Curated rows,
does not assert any row exists, and omits Curated-to-Business. A deterministic
offline lineage-contract remediation is required before connected lineage
validation/deployment/run approvals.

The approved offline remediation now implements two explicit `assert_true`
checks over `system.access.table_lineage`, covering the exact Raw-to-Curated
and Curated-to-Business edges above. Static validation rejects either missing
edge, a missing assertion, or any data mutation. Exact aggregate source
SHA-256
`fc68749ff6f26741212ea9a4763844c5ad7c91bdaf26cf3084070103366ee257`
subsequently passed strict connected bundle validation with exit `0`, no
warning, and no recommendation. It has not been redeployed or executed. Those
remain separate approval boundaries in that order.

The separately approved exact-source redeployment then completed successfully.
Read-only inspection confirmed unchanged five-job identities/configuration and
an exported deployed lineage file matching reviewed SHA-256
`0be1b989978af4bb467fde8e336ef15a2b9cad78be62ae76c1d4fb5ad81f6a4e`.
The lineage job remains unexecuted and requires its own one-shot approval.

That separately approved lineage job subsequently completed as run
`764855862302905`, `TERMINATED/SUCCESS`, at task attempt `0`. Both deterministic
directed-edge assertions passed and no active run remained. Authorization
negative tests remain separate approval boundaries.

The first protected-table negative run `401673129115320` failed before SQL
execution because the denied run identity could not fetch its synchronized
workspace file. This `INTERNAL_ERROR` is not authorization evidence. The
approved offline remediation adds only top-level bundle `CAN_VIEW`, with static
tests rejecting missing or elevated permissions. Strict validation,
redeployment, and a one-shot protected-table retry require separate approvals.

The exact remediated aggregate source subsequently passed strict connected
bundle validation with `Validation OK!`, no warning, and no recommendation.
The exact source was then redeployed successfully. Read-only inspection proved
that all five jobs retained their identities, tasks, run-as principals, and
existing warehouse, while the denied principal received only bundle-level
`CAN_VIEW` and inherited workspace-file `CAN_READ`. Exported negative SQL files
matched the reviewed source byte for byte.

The one-shot protected-table retry ran as job run `231413013546726`, task run
`210727807599395`, attempt `0`. The SQL file loaded and Unity Catalog rejected
the denied principal with `INSUFFICIENT_PERMISSIONS`, no `USE CATALOG` on
`ask_david_development`, and SQLSTATE `42501`. Criterion 27 therefore passed.

The separately approved direct-path job then ran once as job run
`791479735507837`, task run `263272690337919`, attempt `0`. Unity Catalog
rejected the approved managed-storage root in `CheckPathAccess` with
`INVALID_PARAMETER_VALUE.LOCATION_OVERLAP`. Deterministic connected inspection
then proved that the denied principal has no UC storage/data grant or AWS
identity; the credential, seven locations, catalog, and schemas match the
least-privilege model; IAM trust contains only the UC master role and
self-role with the matching external-ID condition; the storage role has one
prefix-scoped inline policy and no attached policy; KMS trusts only account
root and the storage role; and all backing bucket policies contain only the
TLS-deny statement. The structural path rejection plus these clean live policy
inspections satisfy criterion 28 without claiming that `LOCATION_OVERLAP` is a
principal-specific authorization class.

### Phases 4-6 and 4-7

Run all 38 acceptance checks, collect sanitized evidence, run final connected
Terraform zero-drift plan, validate the bundle, check Git tracking, and create
the durable verification report. Any managed-resource change in the final plan
requires review rather than apply.

## Missing environment-specific inputs

The following must exist locally and remain untracked before connected
planning:

- approved AWS profile and current session for account `736956442295`;
- Databricks workspace OAuth profile `ask-david-development`;
- Databricks account OAuth profile `ask-david-account` and verified
  account-admin privilege for identity, workspace-assignment, and service
  principal role APIs;
- workspace host, workspace ID, metastore ID, and warehouse ID;
- the approved namespace decision;
- an explicit boolean/stage that permits Goal 4 resources in development;
- `goal_4_stage = bootstrap|active`, with strict credential validation in
  `active` and no namespaces in `bootstrap`;
- `goal_4_storage_role_self_assumption_enabled = false|true`, defaulting to
  false and required to be true before `active` can plan.

The AWS bucket names, bucket ARNs, storage KMS ARN, IAM role ARN, credential
external ID, service-principal application IDs, and managed paths must be
derived from Terraform resources/outputs. They are not manually copied into
tracked source. No credential value is a Goal 4 input.

## Acceptance-evidence matrix

No row is satisfied merely by this plan. The durable verification report must
record PASS, FAIL, or UNVERIFIED and the exact evidence for every row.

| # | Acceptance criterion | Required evidence |
| --- | --- | --- |
| 1 | Approved development workspace | OAuth identity plus workspace host/ID API response |
| 2 | Premium-capable functionality | Operational Unity Catalog and serverless SQL capability; exact SKU separately noted if unavailable |
| 3 | Correct Region | Attached metastore global ID/Region and AWS Region |
| 4 | Unity Catalog enabled | Current metastore API and SQL result |
| 5 | Existing metastore reused | Same metastore ID before and after apply |
| 6 | No duplicate metastore | Terraform inventory and metastore list |
| 7 | Unity Catalog is primary | Grants/object inventory and no competing catalog implementation |
| 8 | Existing serverless warehouse usable | One-shot SQL result and warehouse inspection |
| 9 | No unnecessary classic cluster | Compute inventory before and after |
| 10 | IAM storage credential works | Credential validation and successful managed-table I/O |
| 11 | Only approved S3 paths | External-location URLs and Terraform/AWS policy inspection |
| 12 | KMS access works | Encrypted object metadata plus successful write/read |
| 13 | Required namespaces | Catalog/schema API inventory |
| 14 | Least-privilege grants | `SHOW GRANTS`/permissions API assertions |
| 15 | Service principals scoped | SCIM, entitlements, memberships, and role inspection |
| 16 | Six generic Iceberg-compatible table categories | Table inventory mapped to the six categories; Tables API format disclosure |
| 17 | Managed Iceberg-compatible tables | Tables API proves seven `MANAGED` Delta UniForm tables with Iceberg-compatible metadata; native Iceberg is explicitly not claimed |
| 18 | No unapproved format substitution | Tables API proves the retained Delta UniForm representation is the approved project profile; no external or unmanaged table |
| 19 | Approved S3-backed Iceberg-compatible metadata | Managed locations plus encrypted S3/Iceberg-compatible metadata evidence; underlying transaction format disclosed as Delta |
| 20 | Raw flow | Deterministic Raw row/result assertion |
| 21 | Curated flow | Deterministic Curated reconciliation |
| 22 | Business flow | Deterministic Gold aggregate reconciliation |
| 23 | Quality checks | All required recorded assertions PASS |
| 24 | Lineage | Raw-to-Curated and Curated-to-Business lineage edges |
| 25 | Snapshots/history | Multiple `DESCRIBE HISTORY` rows and time-travel read |
| 26 | Authorized access | Workflow service-principal job succeeds |
| 27 | Unauthorized table access | Denied principal receives `INSUFFICIENT_PERMISSIONS`, SQLSTATE `42501` |
| 28 | No direct S3 bypass | Managed-path `LOCATION_OVERLAP` plus clean live UC/IAM/KMS/S3 policy inspection |
| 29 | No unmanaged Iceberg | Table inventory and absence of `LOCATION` definitions |
| 30 | Development isolation | Workspace bindings and exact workspace ID |
| 31 | Existing catalogs unchanged | Before/after metadata and Terraform action inventory |
| 32 | No production change | Environment inputs, bindings, and saved-plan inspection |
| 33 | No real Green SM data | Synthetic fixture/source and live sample inspection |
| 34 | No Goal 5+ implementation | Repository/resource scope review |
| 35 | Accepted ADRs unchanged | Git diff/name-status review |
| 36 | No secret/state/plan tracked | Git status, ignore checks, secret scans, tracked-file review |
| 37 | No unexpected drift | Final connected saved plan with zero managed-resource changes |
| 38 | No unnecessary compute running | Final warehouse/cluster state and auto-stop inspection |

## Risks and stopping conditions

Stop immediately on any of these conditions:

- workspace, AWS account, Region, metastore, or warehouse mismatch;
- inability to prove the existing metastore rather than create another;
- namespace proposal not approved;
- account identity permissions are unavailable;
- any existing system/workspace/sample/ML catalog mutation;
- any metastore assignment, warehouse, cluster, Glue, production, Goal 5+,
  replacement, or destroy action;
- storage path outside the approved Goal 3 buckets/prefixes;
- IAM/KMS permission broader than this plan;
- inability to create explicit managed Iceberg with Serverless SQL;
- a table resolves to Delta or external/unmanaged Iceberg;
- unauthorized table or path access succeeds;
- real Green SM data or business semantics appear;
- secrets, state, or saved plans become tracked;
- final connected plan is not zero drift.

## Cost implications

- Terraform/Unity Catalog metadata objects have no always-running compute in
  this design.
- S3, KMS requests, and stored synthetic Iceberg files incur small usage-based
  charges.
- Serverless SQL incurs DBU/cloud compute only while the approved one-shot
  tasks execute and then follows the existing 10-minute auto-stop.
- Managed Iceberg metadata maintenance and predictive optimization can incur
  serverless usage.
- No NAT, RDS, Redis, cluster, warehouse, or other persistent cost-bearing
  resource is added by Goal 4.
- File events, streaming, and additional history retention are deferred.

## Phase 4-1 stopping condition

Stop for review of this design and, specifically, approval or rejection of:

1. one catalog `ask_david_development` with the six `green_sm_*` schemas;
2. schema-level managed roots mapped to the approved Goal 3 buckets;
3. extension of the existing encrypted development Terraform state;
4. two service principals and three groups with the grant model above;
5. reuse of the existing Small Serverless SQL warehouse;
6. the staged credential-validation plan/apply sequence.

Approval permits Phase 4-2 repository implementation and offline validation
only. It does not permit a connected plan, Terraform apply, bundle deploy, SQL
run, or any AWS/Databricks mutation.

## Iceberg-compatible managed-table format decision

The final raw Tables API inventory is the authoritative format source for this
workspace. It reports all seven synthetic tables as `MANAGED` with
`data_source_format = DELTA`, `delta.enableIcebergCompatV2 = true`, and
`delta.universalFormat.enabledFormats = iceberg`. This is Databricks Delta
UniForm: the managed tables expose Iceberg-compatible metadata in the approved
S3 storage, but they are not native Iceberg tables.

The project owner approved retaining these seven existing tables and using the
same managed Delta UniForm representation with Iceberg-compatible metadata in
approved S3 for this project from this point forward. Native Iceberg is no
longer a planned or required format, and the destructive seven-table drop must
not be executed. This changes the Goal 4 implementation direction, but does
not amend the accepted ADRs; those ADRs still require a separate governance
update before this format decision can be treated as an architecture-wide
replacement for their Apache Iceberg wording.

The existing read-only metadata gate and raw Tables API evidence remain useful
as explicit disclosures. The deprecated destructive drop script was removed
from the repository and must not be recreated or run under this profile; the
bundle sync exclusion remains as defense in depth. The complete decision and
corrected acceptance statuses are recorded in
`docs/verification/GOAL-04-NATIVE-ICEBERG-FORMAT-BLOCKER-2026-08-11.md`.

The previous deployment also exposed a bundle-sync leak: `sync.include` alone
did not act as an allowlist, and the nested destructive remediation file was
present in the workspace. The offline fix added the explicit
`sync.exclude: sql/goal_04/remediation/**` contract, static enforcement, and
regression coverage. The separately approved redeployment of aggregate source
SHA-256 `49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027`
completed successfully; read-only inspection confirmed exactly 13 top-level
SQL files and no deployed remediation path. See
`docs/verification/GOAL-04-BUNDLE-SYNC-EXCLUDE-VERIFICATION-2026-08-12.md`.

Do not proceed directly to final drift. Connected recovery no longer includes
table deletion or recreation under the approved compatibility profile. The
remaining connected boundary is a separately approved read-only resource/
compute inspection and zero-drift development plan. The raw Tables API result
must continue to show exactly the seven expected managed tables and must be
reported honestly as Delta UniForm with Iceberg-compatible metadata.

## Authoritative implementation references

- [Unity Catalog managed Apache Iceberg](https://docs.databricks.com/aws/en/iceberg/)
- [Managed tables](https://docs.databricks.com/aws/en/tables/managed)
- [Managed storage locations](https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-storage/managed-storage)
- [S3 storage credential and external location](https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-storage/s3/s3-external-location-manual)
- [Workspace/catalog binding](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/workspace-catalog-binding)
- [Iceberg table history](https://docs.databricks.com/aws/en/tables/history)
- [Lineage system tables](https://docs.databricks.com/aws/en/admin/system-tables/lineage)
- [Declarative Automation Bundle SQL tasks](https://docs.databricks.com/aws/en/dev-tools/bundles/job-task-types)
- [Databricks Terraform Unity Catalog guide](https://registry.terraform.io/providers/databricks/databricks/latest/docs/guides/unity-catalog)
