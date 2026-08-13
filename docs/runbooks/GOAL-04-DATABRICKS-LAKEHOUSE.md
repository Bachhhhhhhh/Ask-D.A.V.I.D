# Goal 4 Databricks lakehouse runbook

## Current boundary

This runbook describes connected checkpoints; it does not authorize them.
Phase 4-2 and approved offline remediations may run only credential-free
static/offline checks. A connected Terraform plan, any saved-plan apply,
credential validation, bundle validation/deployment, SQL run, or negative test
requires the explicit approval defined in the Goal 4 plan.

Only AWS account `736956442295`, Region `ap-southeast-1`, the approved
development Databricks workspace, its existing Unity Catalog metastore, and
its existing Serverless SQL Warehouse are in scope. No staging or production
resource is allowed.

## Local untracked inputs

Keep these values only in the ignored development `terraform.tfvars` or named
OAuth/AWS profiles:

- `goal_4_stage`;
- `goal_4_storage_role_self_assumption_enabled`;
- approved workspace host and numeric workspace ID;
- existing metastore ID;
- existing Serverless SQL Warehouse ID;
- Databricks account ID;
- existing governance administrator user name;
- workspace OAuth profile `ask-david-development`;
- account OAuth profile `ask-david-account`;
- approved AWS profile for the existing development account.

Do not put PATs, OAuth tokens, client secrets, AWS access keys, profile file
contents, storage-credential external IDs, Terraform state, or saved plans in
the repository. Bucket/KMS values and bundle deployment identifiers come from
Terraform outputs, not copied tracked constants.

## Offline Phase 4-2 gate

Run the normal repository and infrastructure checks plus:

```powershell
.\scripts\dev.ps1 databricks-static
```

The static validator must pass and `git status` must show no tracked token,
state, plan, local tfvars, or backend file. This phase must not run
`terraform plan`, `terraform apply`, `databricks bundle validate`,
`databricks bundle deploy`, or any SQL/job command.

## Future staged Terraform sequence

1. Reverify the Databricks and AWS identities, exact workspace/account/Region,
   current metastore ID, and existing warehouse configuration read-only.
2. Configure the missing account-level OAuth profile interactively. Never ask
   Codex to display or copy its token.
3. Set the ignored stage to `bootstrap`, leave the self-assumption flag false,
   and create an initial-role saved connected plan. On a clean deployment its
   scope is one storage credential, one IAM role, one inline policy, and one
   in-place storage KMS policy update. After the recorded partial apply, the
   credential must be a no-op and only the IAM role/policy creates plus KMS
   update remain. No namespace, identity, replacement, or destroy is allowed.
4. Hash that exact initial-role plan and stop for its apply approval.
5. After the initial-role apply succeeds, set only the ignored
   `goal_4_storage_role_self_assumption_enabled` input to `true` while retaining
   `goal_4_stage = "bootstrap"`.
6. Create and review a new saved plan whose only managed-resource action is an
   in-place IAM trust-policy update adding the role's own ARN. Hash it and stop
   for a separate apply approval.
7. Only after that trust-policy apply succeeds, validate the Terraform-owned
   storage credential against an approved managed prefix. The approved
   validator may create/read/delete its own temporary object. Every IAM
   self-assumption, S3, KMS, and `PATH_EXISTS` check must pass.
8. If `PATH_EXISTS` fails because an otherwise empty prefix has no durable
   object, implement only Terraform-managed zero-byte trailing-slash markers
   at the seven approved roots. Run offline validation, then request separate
   approvals for a saved plan whose expected actions are exactly seven
   `aws_s3_object` creates, its apply, and one new credential validation. Do
   not create markers with AWS CLI, SDK, console, or Databricks CLI.
9. Only after every credential validation operation passes, set the ignored
   stage to `active` and create a new saved plan.
   It may add the reviewed locations, bindings, catalog, six schemas, groups,
   service principals, memberships, entitlements, rule sets, and grants. It
   must contain no AWS change, metastore/assignment, warehouse/cluster,
   replacement, destroy, production, or Goal 5+ action.
10. Hash and approve that plan separately. Stop on any apply failure and make
   only a declarative correction followed by a new plan.

The active-stage Terraform check and offline preflight both reject a false or
omitted self-assumption gate. Never validate the storage credential between
the initial-role and trust-policy applies.

Never use AWS CLI, Databricks UI, ad-hoc CLI resource creation, targeted apply,
or an implicit replacement plan to repair a failure.

The initial-role and trust-policy applies are complete. Their reviewed plan
SHA-256 values are recorded in the Goal 4 plan. Seven approved marker objects
were then applied, and the second one-shot credential validation passed every
operation including `PATH_EXISTS`. The active-stage saved plan SHA-256
`c4a81b50ef40531b38a1f785f861d281db02b9e20bc391b209b4c906dafe8502`
applied as `54 added, 1 changed, 0 destroyed`; immediate read-only inspection
verified the intended active foundation without AWS, metastore, assignment,
warehouse, cluster, replacement, or destroy actions. All applied plans are
stale and must never be reused.

## Future bundle and SQL sequence

### Iceberg-compatible managed-table format profile

The authoritative Tables API inventory reports the seven synthetic tables as
managed Delta UniForm (`data_source_format = DELTA` with the approved
`delta.universalFormat.enabledFormats = iceberg` property). They expose
Iceberg-compatible metadata in S3, but they are not native Iceberg tables. The
approved Goal 4 project profile retains them and does not run the
destructive drop/recreate remediation. This distinction must remain visible in
all reports; no native-format claim may be inferred from `USING ICEBERG`, SQL
`information_schema`, or an Iceberg metadata path alone.

The deprecated `remediation/01_drop_delta_uniform_synthetic_tables.sql` was
removed from the repository, remains unreferenced, and is excluded by the
bundle. The excluded directory now contains only a non-executable README
marker so strict bundle validation can match the explicit exclusion; no
executable remediation SQL is permitted there. The separately approved
deployment of aggregate source SHA-256
`49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027` proved the
file is absent from the workspace. Do not execute it under the compatibility
profile. Before final acceptance, preserve a sanitized raw Tables API record
and report both the managed Delta format and Iceberg-compatible S3 metadata:

```bash
python scripts/verify_goal4_table_inventory.py /path/to/sanitized-table-inventory.json
```

The verifier remains a native-Iceberg diagnostic and must fail closed if used;
it is not the acceptance predicate for this compatibility profile. Existing
pipeline, history, lineage, authorization, and cost evidence remains valid
because the seven table identities are retained. See
`docs/verification/GOAL-04-NATIVE-ICEBERG-FORMAT-BLOCKER-2026-08-11.md` for the
format disclosure and remaining zero-drift boundary.

After Terraform resources pass read-only verification, derive bundle variables
from Terraform outputs. Select the approved workspace and OAuth identity only
with `--profile ask-david-development`; do not pass or interpolate a bundle
workspace-host variable. Keep the bundle root under the governance
administrator's `/Workspace/Users/...` path, never `/Workspace/Shared`.

The first strict connected validation failed before deployment because the CLI
attempted profile matching while `${var.workspace_host}` was unresolved. After
the offline auth/root remediation, the second strict connected validation
confirmed that host/profile matching worked, then stopped on one permission
warning: the user-scoped folder inherited governance-admin `CAN_MANAGE`, but
the bundle declared only group ACLs. It also recommended target-scoping the
production-mode root. The second run created only an ignored local
`.databricks/.gitignore`; neither run deployed or executed SQL/jobs.

The current offline remediation declares the same governance admin user as
`CAN_MANAGE` in the bundle and moves the unchanged user-scoped path to
`targets.development.workspace.root_path`. After all offline gates pass,
request separate approval to run exactly one strict connected validation with
the same reviewed target and Terraform-derived variables, omitting
`workspace_host`. Stop on any warning or error and do not retry implicitly.

That separately approved strict validation subsequently passed with exit `0`,
`Validation OK!`, no warning, and no recommendation for bundle SHA-256
`a3c4d178fc44afe19691403dd3a746822e24f88e53782432f2f51f0ae6c394e7`
and resources SHA-256
`8ce89a428d0521344b279a767afaf02051fcdffaeae85ea2f13662745505f919`.
Do not rerun it merely before deployment. The next separate approval is for
deployment of this exact five-job manifest and 12 synchronized SQL files,
without running a job or SQL task. Inspect deployed resources read-only and
stop before workflow execution.

The separately approved historical deployment of aggregate source SHA-256
`022cebf1d12e8a22d5e9f7f57b1a5d9d4ca28dede7f71666b09ea1bfc318ec7e`
subsequently completed. Its original inspection found exactly five jobs and 12
top-level SQL files, no active runs, a stopped warehouse, and no cluster. A
later read-only inspection found the nested remediation SQL too, so that
deployment is superseded for sync-boundary acceptance. The next approval
boundary is one run of authorized pipeline job `967410491586823`, source-set
SHA-256
`651e9779baf3e230230e6c948860d281e2bc2fd527cf35b1fc551fe76e1b4165`.
Do not run history, lineage, or either negative job under that approval.

The separately approved authorized pipeline subsequently completed as run
`347925882630202`, `TERMINATED/SUCCESS`, with all eight tasks at attempt `0`.
Immediate inspection found no active runs and the Small Serverless SQL
warehouse inside its 10-minute auto-stop window. The next separate boundary is
one read-only run of history job `695423086105630`, source-set SHA-256
`7b9bf0f3c74cbef8bea365a747a9540c116d4a667bda677a7e63ab72cb23a9bb`.
Do not run lineage or either negative job under the history approval.

That first history run failed at attempt `0` before inspection because
Serverless SQL rejected concatenation inside
`DESCRIBE DETAIL IDENTIFIER(...)`. It was not retried. The offline remediation
selects the approved catalog with `USE CATALOG IDENTIFIER(:catalog_name)` and
uses static schema-qualified names for the read-only inspection. After offline
validation, require separate strict-validation and redeployment approvals
before any one-shot history retry.

The separately approved strict validation for aggregate source SHA-256
`9714d971417979d131d23f051519f10cb83392b9aa7927a33af4d68840691c4e`
subsequently passed with no warning or recommendation. The next separate
boundary is redeployment of that exact source set, expected to synchronize only
the remediated history SQL content. Inspect the five jobs and history file
read-only, then stop before any retry.

That separately approved redeployment completed successfully. All five job
identities/task counts remained unchanged, and read-only export proved deployed
history SQL SHA-256
`7b521c1f5d4a24d55a0c6658a87c7d0703b35994ee58bc98f01e1062cdfa3927`
matches source. The next boundary is one remediated history retry for job
`695423086105630`, source-set SHA-256
`cfe6d0f047dd9a42e0550f51b9acd1352b17182e8d061184c68610c469631572`.
Stop before lineage or negative jobs.

The separately approved history retry then completed as run
`966938583513350`, `TERMINATED/SUCCESS`, at attempt `0`; all seven table-detail
statements, Raw history, and version-1 assertion executed successfully. Do not
run the currently deployed lineage job yet: its SQL selects only Raw-to-Curated
rows, asserts no row count, and does not verify Curated-to-Business. Strengthen
that contract offline and repeat strict-validation/redeployment boundaries
before a lineage run.

The approved offline remediation now makes `10_verify_lineage.sql` fail unless
`system.access.table_lineage` contains both exact directed edges:

1. `green_sm_raw.synthetic_events` ->
   `green_sm_curated.synthetic_events`;
2. `green_sm_curated.synthetic_events` ->
   `green_sm_business.synthetic_metrics`.

The static gate also requires exactly two assertions and rejects mutation
statements. Do not deploy or run this remediated source merely because the
offline gate passes. First obtain approval for exactly one strict connected
bundle validation. If and only if it has no warning or error, stop and request
a separate exact-source redeployment approval. A lineage run remains a third,
separate approval boundary.

That strict connected validation subsequently passed with `Validation OK!`,
no warning, and no recommendation for aggregate source SHA-256
`fc68749ff6f26741212ea9a4763844c5ad7c91bdaf26cf3084070103366ee257`
and lineage SQL SHA-256
`0be1b989978af4bb467fde8e336ef15a2b9cad78be62ae76c1d4fb5ad81f6a4e`.
The next boundary is separate approval to redeploy that exact source. Expected
content change is only synchronized `10_verify_lineage.sql`; inspect all five
job identities and the deployed lineage file read-only, then stop before any
lineage execution.

That separately approved redeployment completed with `Deployment complete!`.
Bundle summary and direct job inspection confirmed the same five job IDs,
names, task counts, run-as identities, and existing warehouse reference. The
exported deployed lineage file matches reviewed SHA-256
`0be1b989978af4bb467fde8e336ef15a2b9cad78be62ae76c1d4fb5ad81f6a4e`
byte for byte. No job ran. The next boundary is a separately approved read-only
warehouse check and exactly one run of lineage job `825751066015430`; stop on
failure and do not run either negative job.

That separately approved lineage run completed as run `764855862302905`,
`TERMINATED/SUCCESS`, with task attempt `0`. Both fail-closed lineage
assertions therefore passed, no active run remained, and the existing
warehouse entered only its configured 10-minute auto-stop window. Do not run
either negative job under that approval. Review the protected-table expected-
failure contract offline, request its own one-shot approval, and keep the
direct-path negative job as a later separate boundary.

The first separately approved protected-table negative run
`401673129115320` failed at attempt `0` before query execution. The denied
principal could not fetch `11_denied_table_access.sql` from the user-scoped
bundle root, so `INTERNAL_ERROR` is not accepted as Unity Catalog denial. No
retry or direct-path job followed.

The approved minimal remediation adds the denied service principal to
top-level bundle permissions with exactly `CAN_VIEW`. Databricks applies
top-level permissions to bundle resources, workspace directories, and files;
file `CAN_VIEW` permits read but not run/edit/manage. The static gate rejects
missing access and any elevation to `CAN_RUN` or `CAN_MANAGE`. Run offline
validation, then obtain separate approvals in this order:

1. strict connected bundle validation;
2. exact-source redeployment plus read-only ACL/file inspection;
3. one protected-table retry.

Do not run the direct-path job until the protected-table retry yields the exact
expected Unity Catalog authorization error.

The separately approved strict connected validation of aggregate source
SHA-256
`26a6b65951f39e5bf9dcdb53f21d5ddc9c493d0346d60e3b68657e5f576508c1`
then passed with `Validation OK!`, no warning, and no recommendation. The exact
source redeployment also completed. Read-only inspection confirmed unchanged
job identities/tasks/run-as/warehouse, denied-principal `CAN_VIEW` on all five
jobs, inherited workspace-file `CAN_READ`, and byte-for-byte matches for both
exported negative SQL files.

The protected-table retry completed as job run `231413013546726`, task run
`210727807599395`, attempt `0`. Databricks reports the expected-failure job as
`ERROR/RUN_EXECUTION_ERROR`; the task output is the acceptance evidence:
`INSUFFICIENT_PERMISSIONS`, no `USE CATALOG` on `ask_david_development`, and
SQLSTATE `42501`. This is principal-specific Unity Catalog rejection and
satisfies criterion 27. Do not reinterpret the expected job failure as a
successful Databricks run.

The direct-path run completed once as job run `791479735507837`, task run
`263272690337919`, attempt `0`. Its task output was
`INVALID_PARAMETER_VALUE.LOCATION_OVERLAP` from `CheckPathAccess`. This is a
structural managed-storage path guard that applies before principal-specific
authorization. It satisfies criterion 28 only together with the separately
approved connected read-only inspection proving all of the following:

- denied SP has only workspace/SQL entitlements and no UC storage/data grant;
- storage credential and seven locations grant management only to the
  governance-admin group and bind only to workspace `7474644358733471`;
- IAM trust contains only the matching UC master role and self-role with the
  external-ID condition;
- the storage role has exactly one prefix-scoped inline policy and no attached
  policy;
- the storage KMS key trusts only account root and the storage role; and
- all six backing bucket policies contain only `DenyInsecureTransport` and no
  `Allow` principal.

Do not run either negative job again. Any future evidence review must preserve
the distinction between the principal-specific table denial and the structural
managed-path rejection.

The authorization evidence-contract remediation changes comments and static
validation only; both executable negative SQL statements remain byte-for-byte
equivalent after comments are removed. After offline validation, require
separate approvals for strict connected bundle validation and comment-only
redeployment. Do not rerun either negative job. Syntax, network,
missing-object, workspace-file, or compute failures are not evidence.

## Completion checks

Run and record all 38 Goal 4 acceptance criteria, a final connected zero-drift
Terraform plan, bundle validation, resource inventory, warehouse/cluster
state, secret/tracked-file checks, and architecture-scope review. Goal 4 stays
unverified until a durable verification report and immutable evidence commit
exist. Do not begin Goal 5.
