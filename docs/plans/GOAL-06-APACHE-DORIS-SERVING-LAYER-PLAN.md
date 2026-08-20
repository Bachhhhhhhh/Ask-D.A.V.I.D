# Goal 6 implementation plan — Apache Doris serving layer

Status: **PHASE 6-5 HOST HEALTH VERIFIED — PHASE 6-6 ENDPOINT RULE APPLIED; PRIVATE HEALTH TASK AWAITING APPROVAL**
Environment: development only (`736956442295`, `ap-southeast-1`)
Preflight: [Goal 6 Phase 6-0](../verification/GOAL-06-PHASE-6-0-PREFLIGHT-2026-08-13.md)

## 1. Decision summary

Goal 6 will use **self-hosted Apache Doris 4.0.1 in integrated
storage-compute mode**, with one Frontend (FE) and one Backend (BE) on separate
private EC2 instances. This is a deliberately minimal, single-replica,
development-only topology. It is not a production topology or a performance
benchmark deployment.

The authoritative path remains:

```text
Databricks controlled synthetic pipeline
  -> Unity Catalog managed Delta UniForm Iceberg source
  -> Unity Catalog Iceberg REST + OAuth + vended credentials
  -> short-lived Doris external catalog for a controlled refresh
  -> Doris internal serving copy
```

The reverse path is technically and declaratively impossible in this design:
no Doris identity has Unity Catalog write privileges, no Doris workload receives
direct S3 permissions, and no Databricks source pipeline reads from Doris.

The initial source allowlist is exactly one table:

```text
ask_david_development.green_sm_business.goal5_structured_business_metrics
```

It is a Unity Catalog-managed **Delta UniForm Iceberg interoperability** table,
not native Iceberg. It has `HAS_DIRECT_EXTERNAL_ENGINE_READ_SUPPORT`; actual
Doris interoperability remains an acceptance test, not an assumption.

## 2. Deployment option comparison

| Option | Assessment | Decision |
| --- | --- | --- |
| Self-hosted EC2, integrated Doris | Uses existing verified VPC, supports the FE/BE separation and attached encrypted block volumes that a stateful Doris development cluster needs, and is fully Terraform-manageable. | **Selected** |
| ECS Fargate with EFS | Fargate is suitable for the ephemeral verifier but adds poor stateful-storage fit and mutable task/IP lifecycle complexity for the FE/BE database. It is not selected for persistent Doris. | Rejected |
| New EKS plus Doris Operator | Adds an EKS control plane, Kubernetes operations, and PVC infrastructure solely for one small development cluster. | Rejected |
| Official Doris CloudFormation template | Not Terraform-managed, requests an SSH key pair, and the official template supports only US regions rather than `ap-southeast-1`. | Rejected |
| Managed Doris-compatible vendor service | No verified declarative provider, account boundary, or `ap-southeast-1` offering is available in this project evidence. | Rejected |

The selected instance type is `m7i.xlarge` for both FE and BE: 4 vCPUs and
16 GiB RAM. This is a deliberately cost-conscious, predictable-compute choice
requested for the one-FE/one-BE, one-replica synthetic development topology;
it is below the current Doris development/table guidance of eight CPU cores per
component and is therefore a capability-risk checkpoint, not a production
sizing recommendation. Connected verification must fail closed if it cannot
run the required controlled refresh and acceptance queries. Exact availability
in the selected `ap-southeast-1` AZ must be rechecked during the connected-plan
preflight. At implementation time the AMI and Docker image digest must be
recorded from official sources and pinned in Terraform/configuration; floating
image tags are forbidden.

## 3. Network and storage design

### Placement

- FE and BE: existing private data subnets, one selected development AZ.
  They have no public IP, no public DNS endpoint, and no SSH/bastion path.
- EC2 private addressing is exposed to other Terraform-owned components only
  through typed module outputs. There is no public load balancer, public NLB,
  Internet-facing ALB, or public database/admin endpoint.
- FE and BE root and data volumes: encrypted `gp3` EBS volumes using the
  existing development data KMS key. FE metadata persists independently from
  BE serving storage. The initial sizes are 20 GiB for FE metadata and 50 GiB
  for BE data, matching the minimum development storage purpose; they are not
  source-of-truth storage.
- CloudWatch receives FE/BE and verifier logs in a new KMS-encrypted dedicated
  Doris log group. This requires a narrow in-place addition to the existing
  observability KMS policy for that exact log group only.

### Security groups

New, separate security groups are required; the Goal 3B smoke group remains
exclusive to Goal 3B and is not reused.

| Path | Allowed traffic | Denied by design |
| --- | --- | --- |
| Future Query Service / Goal 6 verifier -> FE | TCP 9030 (MySQL protocol, TLS required) from their dedicated groups only | All CIDR/public ingress; all other source groups |
| Goal 6 admin-refresh task -> FE | TCP 9030, plus health-only FE endpoint where required, from the admin task group only | Public/admin browsing and every unrelated workload |
| FE <-> BE | Only the documented FE/BE membership, heartbeat, callback, and audit HTTP stream-load ports required by the selected Doris 4.0.1 configuration: BE -> FE `9020`/`9030`, FE -> BE `8040`/`9050`/`9060`/`8060` | Verifier or future-query direct access to BE |
| FE/BE and task HTTPS egress | TCP 443 through existing private routing for Databricks OAuth/REST, S3 vended paths, ECR/Secrets Manager/CloudWatch where needed | Any inbound Internet exposure |
| DNS | TCP/UDP 53 only to the VPC resolver | Arbitrary DNS egress |

Security groups cannot constrain the public Databricks workspace by FQDN. The
necessary HTTPS egress is via the existing NAT from private subnets, while IAM,
OAuth scope, Unity Catalog privileges, vended credentials, and destination
ports remain independently constrained. This is not public ingress.

The one resource implementing that private TCP/443 egress carries a
resource-scoped `AVD-AWS-0104` Trivy annotation. It applies only to the FE/BE
HTTPS egress resource, never to an ingress rule or another security group. The
source and static regression checks require both the narrow scope and its
documented private-NAT rationale.

The FE enables MySQL-protocol TLS and all MariaDB clients use the
MariaDB-compatible `--ssl` option. The initial development configuration may
use the Doris built-in certificate only for this private synthetic environment;
certificate verification with a managed CA is not asserted by this checkpoint.
A custom CA/mTLS policy is deferred and must be a separate security decision
before any non-synthetic environment. MySQL-specific `--ssl-mode` options are
not permitted in the MariaDB-based verifier image.

## 4. Private verification execution path

The Codex host will never open a TCP connection to Doris. The exact path is:

```text
Codex / AWS control plane
  -> approved repository wrapper invokes ECS RunTask
  -> one Goal 6 Fargate task in existing private application subnets
       (assignPublicIp=DISABLED, dedicated verifier or admin group)
  -> private FE endpoint on TCP 9030 with TLS
  -> CloudWatch Logs evidence, inspected read-only after task stops
```

The persistent verifier support is Terraform-owned: a small purpose-built task
definition, its execution/task roles, secret references, security group rules,
and log group. Each actual run is one-off; there is no ECS service, no public
IP, and no standing Query Service. The task stops after each operation. The
verifier image contains only a MySQL-compatible client, OAuth/REST helper, and
the versioned Goal 6 test runner. It contains no static credentials.

The admin-refresh task and read-only verifier use distinct task roles and
security groups. The former can read only the named OAuth, admin, and query
secret containers because it must initialize the restricted query identity;
the latter reads only the query-identity secret and cannot create catalog/mart
objects.

## 5. Identity and credential model

| Identity | Purpose | Boundaries |
| --- | --- | --- |
| Terraform development administrator | Declarative provisioning only | Existing approved profile; no runtime credential embedded in Doris |
| `ask-david-development-doris-external-read` Databricks service principal | Obtain OAuth access to Unity Catalog Iceberg REST | Workspace user only; no metastore admin, SQL warehouse, catalog ownership, source MODIFY, CREATE, DROP, or broad account privileges |
| Doris bootstrap/admin identity | Cluster bootstrap, catalog creation, internal serving migration/refresh only | Password in a dedicated KMS-encrypted Secrets Manager container; no source-table write grant |
| Future Query Service Doris identity | Future controlled-service read-only access | `SELECT` only on approved internal serving marts; no DDL/DML/admin privileges |
| Goal 6 admin Fargate task role | Read exact admin, query-bootstrap, and OAuth secret containers and emit logs | No S3 data grant, no broad Secrets Manager access, no AWS administrative permissions |
| Goal 6 verifier Fargate task role | Read exact query secret container and emit logs | Cannot retrieve OAuth/admin secrets and cannot mutate Doris configuration |

The Databricks service principal receives only:

1. `USE CATALOG` on `ask_david_development`;
2. `USE SCHEMA` and `EXTERNAL USE SCHEMA` on `green_sm_business`;
3. `SELECT` on the single allowlisted `goal5_structured_business_metrics`
   table.

There is no `EXTERNAL USE LOCATION`, direct S3 IAM grant, metastore
administrator privilege, or grant on Raw, Curated, AI, or Platform schemas.
The service principal uses OAuth machine-to-machine authentication. Its client
secret is created/rotated declaratively where the provider supports it, written
only to a dedicated KMS-encrypted Secrets Manager secret, injected at runtime,
and never committed, printed, written to task definitions, or retained in
CloudWatch logs. Terraform state remains remote, encrypted, and Git-ignored.

## 6. Unity Catalog / Delta UniForm integration

The integration uses the Unity Catalog Iceberg REST endpoint:

```text
https://<approved-workspace>/api/2.1/unity-catalog/iceberg-rest
```

The private admin runner accepts the approved workspace only as one HTTPS
`*.cloud.databricks.com` origin, normalizes one trailing slash, and fails
closed before OAuth/REST use if it is malformed. It composes all paths from the
normalized origin; it must never prepend a second `https://`.

The Doris catalog template uses:

- `type=iceberg` and `iceberg.catalog.type=rest`;
- the exact `ask_david_development` warehouse/catalog;
- OAuth2 using the dedicated service principal;
- `iceberg.rest.vended-credentials-enabled=true`;
- S3 region `ap-southeast-1`;
- a versioned allowlist check before every source read.

The refresh harness obtains a short-lived OAuth token at run time. It creates
the external catalog only for the controlled refresh/read operation and removes
it immediately afterward. Thus neither a PAT nor long-lived OAuth credential
is retained in committed configuration or as a standing Doris catalog secret.
The credentials returned by Unity Catalog are vended and scoped by the
principal's table privileges. No static AWS access key is configured anywhere.

If the selected Doris version cannot consume the vended Unity Catalog Delta
UniForm Iceberg representation, the task must fail closed. The response is a
durable incompatibility report and a new review, not a source-table rewrite,
Glue/HMS addition, static S3 permission, or source-format relabeling.

## 7. Internal serving objects and refresh/rebuild model

The first serving database is `ask_david_serving_development` and contains only
neutral synthetic state:

- `serving_metric_daily`: `metric_date`, `category`, `event_count`,
  `metric_total`, authoritative source table ID, source `transformed_at`, and
  Doris `refreshed_at`.
- `serving_refresh_state`: a non-authoritative watermark and refresh result.
- `serving_data_freshness`: a view or compact table exposing source freshness,
  Doris refresh timestamp, and derived refresh lag.

`serving_metric_daily` is a one-replica internal Doris table. It is explicitly
disposable. The initial safety profile uses a controlled full replacement:
it reads only the allowlisted Business table through a temporary external
catalog, replaces only the internal Doris copy, and records the resulting
watermark, count, and status in `serving_refresh_state`. The synthetic input
is still incremental: one Terraform-managed, SSE-KMS neutral CSV under the
existing approved Goal 5 raw-source prefix is applied by a dedicated
Databricks SQL task through Raw -> Curated -> Business before the controlled
serving refresh reads it. A later incremental Doris materialization strategy
requires a separately reviewed source change and proof that its idempotency
contract is equivalent to this safer full-replacement profile.

The one-replica declaration does not waive BE storage readiness. Before an
admin refresh may create the table, the Terraform-owned BE bootstrap must
prove that its configured container user can write the exact EBS-backed
`storage_root_path`, and that `SHOW BACKENDS` reports the matching BE alive,
not decommissioned, with non-zero total capacity. The explicit development
root is `/opt/apache-doris/be/storage,medium:hdd`. A listener with zero
reported capacity is a fail-closed host/storage blocker, not a reason to
lower replication further or alter the governed source path.

The rebuild test performs this direction only:

```text
record expected Doris result
  -> DROP/TRUNCATE Doris-only serving copy
  -> re-run versioned internal migration
  -> full refresh from Unity Catalog external source
  -> compare source count, aggregate, provenance, and freshness
```

It never changes or deletes a Unity Catalog table, S3 object, Iceberg metadata,
or Databricks pipeline output.

## 8. Access controls, workload controls, and audit

- The future Query Service identity is constrained by Doris RBAC to `SELECT`
  on the approved internal serving database/tables and narrowly needed
  metadata. It is source-IP constrained to the future Query Service security
  group, and a verifier test proves DML, DDL, and unauthorized database access
  are rejected.
- A development workload group and query-user properties apply a 30-second
  timeout, 25% CPU/memory caps, concurrency two, and a bounded queue. The
  acceptance test uses harmless deterministic configuration inspection rather
  than resource exhaustion.
- Doris audit logging is enabled. Query evidence must contain query ID,
  authenticated identity, target object, status, and duration/timestamp. The
  small verifier result contract includes query result, source dataset, refresh
  timestamp, query ID, row count, and execution duration.

This does not implement the Goal 8 Query Service, a policy API, an agent, or
agent-generated SQL.

## 9. Terraform/state boundary and anticipated resources

All AWS and Databricks persistent resources remain in the existing encrypted
development Terraform state at `infrastructure/environments/development`; the
bootstrap state root is not changed. The root will call a new
`infrastructure/modules/doris-serving` module and a narrow verifier support
module. This avoids untracked cross-state dependencies on the verified Goal 3
network and Goal 4 Unity Catalog foundation.

Expected AWS resources:

- two private EC2 instances and encrypted root/data EBS volumes;
- EC2 instance profile/roles scoped to bootstrap logging and exact secret
  retrieval where needed;
- Doris FE, BE, admin-task, and verifier-task security groups/rules;
- a KMS-encrypted CloudWatch log group and an exact observability KMS-policy
  statement;
- a small ECS Fargate admin-refresh task definition and a separate verifier
  task definition, with their least-privilege roles/policies;
- KMS-encrypted Secrets Manager containers/versions for the OAuth, bootstrap,
  and query identities;
- one Terraform-managed SSE-KMS neutral incremental fixture object.

### Two-step verifier-image bootstrap

The initial Goal 6 foundation plan must not create ECS task definitions because
their image must be an immutable digest in the Terraform-created private ECR
repository. Terraform therefore has two explicit, default-off gates:

1. `goal_6_enabled=true`, with `goal_6_verifier_tasks_enabled=false`, creates
   the reviewed serving/ECR/identity foundation but no verifier task definition.
2. After separately approved local build/scan and private ECR push, set only
   `goal_6_verifier_tasks_enabled=true` and the reviewed `@sha256:` image
   input. A second saved plan may then create the admin and verifier task
   definitions. No task is run by either plan.

This prevents a floating image tag, circular ECR bootstrap input, or ad-hoc
task-definition repair.

Expected Databricks resources:

- one account/workspace-assigned external-read service principal and its
  minimal entitlement/rule-set;
- its scoped OAuth secret, handled as a sensitive secret reference;
- modifications to the existing Terraform-owned catalog/schema grant resources
  so the new grants do not fight `databricks_grants` ownership;
- one development-only Databricks bundle job that applies the approved neutral
  increment to the governed Raw -> Curated -> Business path using the existing
  Serverless SQL warehouse. It creates no cluster or warehouse.

No metastore, workspace assignment, catalog, schema, external location, Glue
catalog, Hive Metastore, RDS, Redis, OpenSearch collection/index, agent,
controlled tool service, production resource, or real Green SM data is in
scope.

## 10. Repository implementation outline

Phase 6-2 will create or modify only the following Goal 6-owned areas:

```text
doris/
  catalogs/                 # secret-free Unity Catalog REST template
  schemas/                  # serving schema and RBAC DDL
  materialized_views/       # neutral serving mart definitions
  migrations/               # ordered internal-only migrations
  tests/                    # static DDL/allowlist/refresh/rebuild tests
  README.md
infrastructure/
  modules/doris-serving/
  modules/doris-verifier/
  environments/development/goal6.tf
  environments/development/goal6_variables.tf
  environments/development/outputs.tf
databricks/
  bundles/goal_06_doris/
  sql/goal_06/
docker/
  Dockerfile.doris-verifier
scripts/
  validate_goal6.py
docs/
  runbooks/GOAL-06-DORIS.md
  verification/...
  PROJECT_STATUS.md
tests/unit/
  test_goal6_static.py
```

Terraform inputs will be non-secret and validate the exact environment,
instance family, image digest, selected data subnet, S3 object hash, and
approved workspace/metastore/catalog names. Secret values, local tfvars,
backend files, state, plans, OAuth tokens, client secrets, and generated
passwords remain ignored and are never written to these source files.

## 11. Validation and approval sequence

1. **Phase 6-2:** implement the above declarative source and tests only.
2. **Phase 6-3:** run Goal 6-scoped formatting, static validation, pytest
   regression tests, Terraform fmt/validate/test/TFLint/Trivy, Docker build,
   static SQL/Doris validation, `git diff --check`, and source/secret checks.
   The repository-wide platform-foundation suite, its `pydantic` dependency,
   and any Pydantic-dependent import or test result are explicitly excluded
   from Goal 6 acceptance. They remain a separate Goal 2 development concern;
   no Goal 6 status may depend on their installation or verification.
3. **Phase 6-4:** after a separate approval, reverify identity and create one
   saved connected development Terraform plan. Stop if it shows any destroy,
   replacement, production change, metastore change, unreviewed public
   exposure, or scope drift.
4. **Phase 6-5:** apply only the reviewed plan after a hash-bound approval.
   A failure stops for inventory and declarative remediation; no automatic
   destroy, retry, or out-of-band repair is permitted.
5. **Phases 6-6 through 6-13:** execute each approved private task exactly as
   reviewed, inspect only CloudWatch/control-plane evidence, and stop on the
   first unexpected task or source-format failure.
6. **Phase 6-14:** run zero-drift validation, confirm temporary tasks stopped,
   document persistent/cost-bearing resources, and create durable evidence
   before any verification claim.

## 12. Resource impact and deferred work

The FE and BE EC2 instances, EBS volumes, NAT egress they use, CloudWatch Logs,
Secrets Manager secrets, KMS usage, and any Fargate verifier/admin runtime are
cost-bearing. The EC2 instances and EBS volumes remain persistent after
verification; they are not destroyed automatically. Fargate tasks are
one-off and stop after each run. Before provisioning, the saved plan review
will enumerate every cost-bearing resource and its exact instance/storage
shape.

The roadmap's 10M-row, 20-user, and P95 benchmark is explicitly
**DEFERRED — OPTIONAL SCALE/PERFORMANCE VALIDATION**. Production HA, multiple
replicas, cross-AZ topology, custom CA/mTLS, scheduled refresh, autoscaling,
Goal 7 OpenSearch, Goal 8 Query Service, agents, and real Green SM data are
out of scope.

## 12.1 Current deployment recovery checkpoint

The first approved foundation apply created the intended private FE/BE
foundation. A subsequent saved reconciliation plan was a verified no-op and
read-only state inspection confirms the FE and both volume attachments are now
state-owned. That plan must not be applied because it has no action.

The separate blocking condition is host bootstrap: both AMI root volumes are
8 GiB, and the BE Docker pull failed with `no space left on device` while
unpacking the digest-pinned Doris image. EC2 health and private exposure are
healthy, but Doris health is not. The dedicated BE data volume is not the
failing filesystem.

The approved offline remediation declares a 30 GiB encrypted gp3 root volume
for each host. It also introduces a BE-only bootstrap generation marker in
the rendered user data together with `user_data_replace_on_change = true`.
Generation `2` intentionally replaces the failed BE so first-boot cloud-init
can run with sufficient root filesystem capacity. It does not change the
dedicated 50 GiB BE serving-data volume, data source, IAM, KMS, subnets,
security groups, or public-exposure posture. The FE root-volume expansion is
expected to be in-place; the exact action set remains a saved-plan decision,
not an assumption.

### EC2 user-data size contract

The Terraform-rendered FE and BE bootstrap payloads are subject to AWS's
16,384-byte EC2 `user_data` limit. The module assigns its payloads from
`local.fe_user_data` / `local.be_user_data` and has a fail-closed pre-plan
check requiring deterministic size-equivalents to be at most `16384`. The
equivalents use the fixed 21-byte AWS EBS-volume-ID shape while all other
rendered inputs are the same. A connected plan therefore stops before review
if a template, image reference, ARN, or bootstrap marker exceeds the limit.
This guard changes neither Doris configuration nor runtime bootstrap logic.
All four template renders are conditional on the module's known `enabled`
gate. Disabled foundation and Goal 4 test plans therefore render no FE/BE
bootstrap, do not index resources whose `count` is zero, and do not interpolate
the intentionally absent Goal 6 secret ARNs. When enabled, the rendered
bootstrap and size guard retain the same inputs and behavior.

The reviewed and approved root-bootstrap remediation was applied on
`2026-08-13` from saved-plan SHA-256
`81943eb2c58097e074b87f96d57b736767e9ab105c9b8997d3eb7576a28bfe30`.
It retained the private topology and persistent serving-data volume, expanded
the FE root in place, replaced the BE only for generation 2, and reattached
the same BE data volume. EC2 platform checks and BE bootstrap evidence pass;
Doris application health remains unverified. No task launch, image push, or
integration test is authorized at this checkpoint without its own approval.

## FE listener bootstrap remediation (applied; revision-4 task failed)

The first revision-3 private admin-refresh attempt reached the FE host but
received an active TCP refusal on query port 9030. Read-only SG, route, NACL,
and flow-log evidence ruled out a network drop. The host template had mounted
the Doris configuration but omitted the official Docker FE/BE discovery
variables, allowing a detached container ID without a usable listener.

The approved offline remediation now renders `FE_SERVERS`/`FE_ID` for FE and
`FE_SERVERS`/`BE_ADDR` for BE, derives only private addresses, and adds a
local 9030/9050 readiness guard. It adds explicit FE bootstrap generation 2
and deliberate `user_data_replace_on_change` wiring so the connected plan
exposes the FE/BE replacement and volume reattachment actions. The saved
connected plan was created and reviewed without apply, ECS task, or AWS
resource mutation. It is recorded in
[`GOAL-06-FE-LISTENER-REMEDIATION-OFFLINE-2026-08-13.md`](../verification/GOAL-06-FE-LISTENER-REMEDIATION-OFFLINE-2026-08-13.md).

Offline evidence, including the explicit repository-wide mypy limitation, is
recorded in
[`GOAL-06-PHASE-6-5-ROOT-BOOTSTRAP-REMEDIATION-OFFLINE-2026-08-13.md`](../verification/GOAL-06-PHASE-6-5-ROOT-BOOTSTRAP-REMEDIATION-OFFLINE-2026-08-13.md).
The FE-listener saved-plan result is recorded in
[`GOAL-06-FE-LISTENER-REMEDIATION-CONNECTED-PLAN-2026-08-13.md`](../verification/GOAL-06-FE-LISTENER-REMEDIATION-CONNECTED-PLAN-2026-08-13.md).
Its SHA-256 is
`90c504a9e54529d3d4d82e61088455573ab0d02d9ff287df47bc0b6ca7bf83a0`.
The plan contains six delete/create replacements: the two hosts, both volume
attachments, and both Goal 6 task definitions whose private-host inputs become
unknown during replacement. Applying that exact action set requires a
separate hash-bound approval.

## 13. Next approval requested

The connected plan above was created after explicit approval on `2026-08-13`.
The exact hash-bound plan
`90c504a9e54529d3d4d82e61088455573ab0d02d9ff287df47bc0b6ca7bf83a0` was
approved and applied successfully as `6 added, 0 changed, 6 destroyed`.
Immediate inspection confirmed private FE/BE replacements, reattachment of the
existing metadata/serving-data volumes, active task-definition revision 4, and
no running Goal 6 task. The subsequent separately approved read-only health
inspection passed EC2 checks, but the one-off revision-4 verification task
failed at the FE connection. No retry, bundle/SQL run, or implicit
replacement plan is authorized by this apply. A separately approved revision-4
private admin-refresh task reached `STOPPED` with exit code `1` and again
reported `ERROR 2002 (HY000): Can't connect to server on '10.42.78.72' (115)`.
No retry was made. The durable task evidence is
[`GOAL-06-PRIVATE-ADMIN-TASK-REVISION-4-2026-08-13.md`](../verification/GOAL-06-PRIVATE-ADMIN-TASK-REVISION-4-2026-08-13.md).
The Goal 6 checkpoint remains blocked pending a new saved connected plan for
this offline readiness-marker remediation and its separate review/approval.

The approved follow-up plan was subsequently created and reviewed as a
plan-only operation. The exact artifact is
`goal-06-fe-readiness-marker-remediation-20260813.tfplan` with SHA-256
`07a9efc1f932b2eabc48216aef89cc476f0f6cfbc582a5a3d83b13b69f5349a6`. It has
243 no-op resources and exactly six delete/create replacements: FE and BE
instances, their volume attachments, and the two Goal 6 task definitions whose
private-host values propagate during host replacement. It has zero in-place
changes and no IAM/KMS/network/S3/ECR/Databricks/production/public-exposure
actions. No apply or task run occurred. A separate hash-bound approval is
required before applying it; see
[`GOAL-06-FE-READINESS-MARKER-REMEDIATION-CONNECTED-PLAN-2026-08-13.md`](../verification/GOAL-06-FE-READINESS-MARKER-REMEDIATION-CONNECTED-PLAN-2026-08-13.md).

The exact plan was subsequently approved and applied successfully as `6 added,
0 changed, 6 destroyed`. The new private FE/BE hosts are
`i-0fe26c51fd499b7de` (`10.42.64.238`) and `i-07d1e1eddfec1c9eb`
(`10.42.71.97`); the existing encrypted role volumes are reattached at
`/dev/sdf`, and both task definitions are active at revision 5. Immediate
inspection found no running task. FE health was `ok/ok`; BE was still
initializing and no new marker stream was visible yet. Subsequent read-only
console inspection recorded `doris-port-unavailable` for FE `9030` and BE
`9050` after the local readiness guard; neither host reached
`doris-port-ready`. No task launch or retry was performed. The apply evidence is
[`GOAL-06-FE-READINESS-MARKER-REMEDIATION-APPLY-2026-08-13.md`](../verification/GOAL-06-FE-READINESS-MARKER-REMEDIATION-APPLY-2026-08-13.md).
The next boundary is an offline diagnosis/remediation for the failed FE/BE
listeners. No connected retry, task launch, or replacement plan is authorized
until that remediation is reviewed.

The approved offline diagnosis/remediation is recorded in
`docs/verification/GOAL-06-DORIS-LISTENER-DIAGNOSIS-OFFLINE-2026-08-14.md`.
It applies the Doris host prerequisite contract, passes the available static
checks, and intentionally does not delete metadata/serving-data volumes or
retry a task. Terraform and security-tool validation remain unverified on this
host because the corresponding executables are unavailable. The next approval
boundary is one saved connected development plan whose exact FE/BE bootstrap
replacement set must be reviewed before any apply or verifier task.

The saved connected plan was subsequently created and reviewed as a read-only
operation. Artifact:
`goal-06-doris-listener-host-prereq-remediation-20260814.tfplan`; SHA-256
`bbe5e504b136fd639995c033d90afecf3a557fb430dbd3a1f194f29e5b7a0bbd`.
It contains six reviewed delete/create replacements and 243 no-op resources,
with no IAM/KMS/network/S3/ECR/Databricks/production/public-exposure action.
Apply remains a separate hash-bound approval boundary, and no verifier task is
allowed before both replacement hosts produce `doris-port-ready`.

The exact plan was approved and applied on `2026-08-14` as
`6 added, 0 changed, 6 destroyed`. The replacement FE/BE hosts reached
`host-prerequisites-ready`, but both readiness guards later recorded
`doris-port-unavailable` on ports `9030` and `9050`; no `doris-port-ready`
evidence or host log stream exists. EC2 checks are `ok/ok`, task definitions
are active at revision 6, and no Goal 6 task was launched or retried. See
`docs/verification/GOAL-06-DORIS-LISTENER-HOST-PREREQ-APPLY-2026-08-14.md`.
The next boundary is offline diagnosis only; no connected retry is authorized.

### Stable private-IP remediation boundary

The replacement hosts used different private addresses from the persisted
single-node FE/BE state. The next offline-only remediation therefore declares
`goal_6_fe_private_ip = "10.42.64.238"` and
`goal_6_be_private_ip = "10.42.71.97"` as Terraform-managed development
inputs. The module assigns those addresses privately, verifies both are
distinct and inside the selected data subnet, and the host bootstrap records
and enforces the expected local address before starting Docker. This boundary
does not reset volumes or run tasks; it must be followed by a new saved
connected plan and separate approval.

### Disposable serving-state rebuild boundary

If the diagnostic apply still leaves both listeners unavailable, the approved
next design is a default-off Terraform gate named
`goal_6_rebuild_serving_state`. Enabling it creates fresh encrypted FE/BE
serving-state volumes while retaining the prior managed volumes with
`prevent_destroy`; it does not enable Doris metadata recovery, format a disk,
or delete any old state. The resulting saved plan must be reviewed for only
the two new volume creates and the dependent FE/BE host/attachment
replacements, with zero old-volume deletes and zero unrelated cloud actions.
The lakehouse source remains authoritative and the rebuild is disposable.

### Private FE/BE initiated-traffic remediation boundary

Offline review of the Terraform source and the applied serving-state rebuild
plan found a deterministic network-contract defect. The live-plan model had
only FE/BE ingress rules plus HTTPS-only host egress. The official Doris BE
Docker bootstrap must initiate a MySQL-protocol connection to FE `9030` to
inspect/register backend membership, while FE initiates heartbeat/RPC traffic
to BE `9050`, `9060`, and `8060`. Ingress rules do not replace the matching
outbound authorization for a new connection.

The official branch-4.0 `init_be.sh` performs that FE inspection and
registration before it invokes `start_be.sh --console`. This explains the
observed state in which the BE Docker container was running but listener
`9050` was unavailable: the container entrypoint was still blocked before the
BE process start. The prior redacted `log_signal=configuration` classification
is supporting context only, not the authoritative diagnosis.

The remediation adds only five private SG-to-SG rules: BE egress and FE
ingress on `9030`, plus FE egress to the three already-approved BE ports. It
does not add a CIDR, public path, new service, or additional Doris port. The
ignored development input keeps `goal_6_rebuild_serving_state = true` so the
fresh encrypted 20/50 GiB serving-state volumes selected by the approved
rebuild remain the desired volumes. A connected plan must show zero EBS volume
deletes/replacements and stop on any attempt to return to the old detached
volumes.

The BE host bootstrap also removes the FE/BE first-boot race: before Docker BE
starts, it performs a bounded credential-free TCP readiness check against the
private FE `9030` registration path. It emits waiting/ready/unavailable
markers and fails closed if FE never becomes reachable. This prevents a
healthy configuration from being classified as failed merely because BE
started before the new FE bound its query listener.

The already-reviewed bootstrap-marker source will require FE/BE user-data
replacement before it can produce new durable evidence. The exact replacement
and attachment action set remains a connected-plan result, not an assumption.
No apply or verifier task is allowed until that saved plan is separately
reviewed and approved. After apply, both current hosts must independently emit
`bootstrap-invoked`, a ready diagnostics summary, and `doris-port-ready` for
`9030`/`9050`; any other terminal marker stops the workflow.

### BE-to-FE RPC callback remediation boundary

Project-owner diagnostic evidence from `2026-08-18` confirms both processes
are locally healthy: FE listens on `10.42.64.238:9020`, BE listens on
`10.42.71.97:9050`, and the BE data volume is healthy. BE logs continuously
record timeouts opening transport to FE `9020` from the disk, tablet, task,
and index-policy report callbacks. Terraform inspection confirms the paired
BE security group has no egress and the FE security group has no ingress for
that exact RPC path.

The minimum declarative remediation is exactly two development-only SG-to-SG
rule creates: BE egress to FE TCP `9020` and FE ingress from BE TCP `9020`.
It adds no CIDR, public exposure, instance/user-data change, volume action,
task-definition change, or broader port range. A connected saved plan must
contain only those two creates and zero update/replace/destroy actions; any
different result stops for review. Applying the exact reviewed saved plan
requires separate hash-bound approval. Post-apply acceptance requires direct
evidence that the BE callback timeouts cease and the BE reports usable
capacity; EC2 health or local listener evidence alone is insufficient.

The separately approved connected plan now satisfies that contract. Its
SHA-256 is
`2e5d7aaa4889fd90865f312c3659f6ce1f41cc6a82dde8d8a3faecb56fb9ae4b`,
and filtered plan JSON contains only the two expected TCP `9020` creates with
zero update, replacement, or destroy action. No apply or ECS task has run.
Applying this exact artifact remains a separate approval boundary; see
`docs/verification/GOAL-06-BE-FE-RPC-9020-CONNECTED-PLAN-2026-08-18.md`.

The exact artifact was subsequently approved and applied as `2 added, 0
changed, 0 destroyed`. Immediate SG inspection and post-apply VPC Flow Logs
prove BE-to-FE TCP `9020` changed from historical `REJECT` to bidirectional
`ACCEPT`; both hosts remain private and `ok/ok`, with no task run. Network
remediation is therefore PASS. Direct Doris capacity evidence remains a
separate checkpoint because no FE/BE host log stream exists and the completed
bootstrap process cannot retroactively emit `be-storage-capacity-ready`. See
`docs/verification/GOAL-06-BE-FE-RPC-9020-APPLY-2026-08-18.md`.

## Runtime readiness-marker evidence boundary

The repaired TCP `9020` path proves that BE-to-FE callbacks are now accepted,
but it does not independently prove current Doris control-plane state. Exact
marker searches found no current FE/BE host stream in the dedicated Doris log
group, and the completed bootstrap cannot retroactively emit
`listener_state=ready`, `doris-port-ready`, or
`be-storage-capacity-ready`. Replacing healthy hosts solely to reproduce these
markers would be disproportionate and would create avoidable availability and
volume-attachment risk.

The minimum follow-up is one guarded private Fargate diagnostic using the
already Terraform-created revision-8 admin task definition and its immutable
image. Repository-managed PowerShell and Bash wrappers bind the account,
region, task definition/revision/image, private application subnets, admin SG,
and fixed FE/BE addresses before launch. The task override runs only a bounded
`SHOW BACKENDS;` query through FE. It emits sanitized success markers only if
FE `9030` is queryable and the row for BE `10.42.71.97` is alive, is not
decommissioned, and has non-zero total capacity. This is current,
deterministic FE-control-plane evidence for FE listener readiness, BE heartbeat
listener readiness, and BE usable storage. It does not run refresh, DDL/DML,
Terraform, ECR, Databricks, or a direct BE mutation.

Offline validation of this contract is complete. One connected task launch
remains a separate explicit approval boundary. There is no implicit retry: a
non-zero exit, missing marker, unavailable marker, public ENI, or any immutable
task-definition mismatch stops for review. See
`docs/verification/GOAL-06-RUNTIME-READINESS-MARKERS-OFFLINE-2026-08-18.md`.

The one-task checkpoint was subsequently approved and executed once. Task
`221d070dc24b40b0a1144b573e137fac` stopped with exit code zero on a private
Fargate attachment and its exact CloudWatch stream contains every required FE,
BE, listener, port, and capacity marker with no unavailable record. Runtime
FE/BE listener readiness and BE usable-storage readiness are PASS. This does
not authorize or satisfy Phase 6-7 refresh, serving-copy validation, later
authorization/performance checks, or final zero drift. See
`docs/verification/GOAL-06-RUNTIME-READINESS-MARKERS-CONNECTED-2026-08-18.md`.

## FE health command-vector contract

The initial private FE listener check is a bounded MariaDB TLS `mysqladmin`
ping executed only through the versioned
`infrastructure/scripts/run-goal6-fe-health.ps1` wrapper and only after a
separate task-run approval. The verifier image has `ENTRYPOINT ["/bin/sh"]`.
Therefore its ECS override must be exactly `[-c, <health command>]`, rather
than `[/bin/sh, -c, <health command>]`; the latter produces a double-shell
invocation and can fail before the ping starts. ECS task-definition inspection
reports null `entryPoint` when it does not override the image entrypoint; the
wrapper requires that null state and binds the reviewed immutable image digest
whose Docker configuration supplies `/bin/sh`. It otherwise fails closed on a
private `awsvpc` Fargate shape, FE host, two application subnets, verifier SG,
or `assignPublicIp=DISABLED` mismatch. It performs no SQL query and accepts
only exit `0` plus non-sensitive listener evidence: `mysqld is alive` or the
expected MariaDB `Access denied` response to a passwordless ping. The latter
proves private TCP/TLS reachability and denied anonymous access, but does not
substitute for later query-identity validation.

## Admin bootstrap global-privilege contract

The private admin-refresh runner creates only its dedicated named Doris
administrator from an injected secret. Doris 4.0 treats `ADMIN_PRIV` as a
global-only privilege, so the bootstrap grant must be exactly
`GRANT ADMIN_PRIV ON *.*.* TO '<admin-user>'@'%';`. The two-level form `*.*`
is invalid and causes the runner to stop before it can add a BE, obtain OAuth,
construct its temporary Unity Catalog Iceberg REST catalog, or read the
allowlisted lakehouse source. This syntax correction changes no AWS, Unity
Catalog, S3, KMS, IAM, network, source-table, or task-execution contract. It
still requires a newly built/scanned immutable image, separately approved ECR
push, task-definition revision, and one independently approved task before
any Phase 6-7 result may be claimed.

The current Linux host has no `pwsh`, so the existing PowerShell-only launch
path cannot be executed directly. The minimum offline resumption adds a Bash
wrapper implementing the same one-task, private, no-retry contract. It binds
the active revision-8 task definition and immutable image, exact FE/BE and
Databricks workspace origin, two private application subnets, admin security
group, task/execution roles, expected environment variables, the three named
Secrets Manager references, and the dedicated CloudWatch configuration. It
uses no command override and therefore executes only the image's reviewed
`/app/doris-admin-refresh` entrypoint. It reads logs only to require the
sanitized completed marker and never prints task output or secret values.

Read-only AWS/Databricks revalidation on `2026-08-18` confirms the approved
account and region, no running admin task, active revision 8 with the reviewed
image and private configuration, the development workspace/metastore in
`ap-southeast-1`, external access enabled, and the isolated development
catalog intact. Offline Bash parsing, static validation, focused regression
tests, compilation, and diff integrity pass. The next boundary is separate
approval for exactly one admin-refresh task; no task was launched by this
preparation. See
`docs/verification/GOAL-06-PHASE-6-7-ADMIN-REFRESH-BASH-WRAPPER-OFFLINE-2026-08-18.md`.

That approval was later granted and the guarded revision-8 task ran exactly
once on `2026-08-18`. It used a private Fargate ENI, stopped with exit code
zero, emitted the completion marker, and left no admin task running. The marker
is emitted only after the temporary Unity Catalog Iceberg REST catalog reads
the allowlisted Delta UniForm source, refreshes the internal serving copy and
state, and is dropped. This closes the connected interoperability and initial
refresh gate. Count and representative-value parity remain unverified pending
the read-only verifier. Evidence:
`docs/verification/GOAL-06-PHASE-6-7-ADMIN-REFRESH-CONNECTED-2026-08-18.md`.

The follow-up read-only grants and Tables API audit confirms the dedicated
Doris application has only `USE_CATALOG`, `USE_SCHEMA`,
`EXTERNAL_USE_SCHEMA`, and table-level `SELECT` across the exact allowlisted
path. No source write or create privilege is present. The source is a managed
Delta UniForm table whose Tables API metadata exposes the Iceberg-compatible
representation and S3 `_iceberg/metadata` path. This makes the planned
integration eligible for the connected test but does not prove it: Phase 6-7
must still stop unless a real Doris query through Unity Catalog Iceberg REST
succeeds.

The later-phase offline gap audit also found that the original read-only
verifier did not meet final result-contract acceptance: it omitted
`query_result` and obtained `LAST_QUERY_ID()` in a separate client session.
The remediated source now collects the representative row and immediate query
ID within one TLS MariaDB session and emits the complete typed contract. This
source change requires a future immutable image rebuild/push and Terraform task
definition revision before Phase 6-11/6-13 execution; it does not change or
block the existing revision-8 admin runner needed for Phase 6-7. Evidence:
`docs/verification/GOAL-06-RESULT-CONTRACT-OFFLINE-REMEDIATION-2026-08-18.md`.

Phase 6-11 through 6-13 now also have source-managed, separate evidence
runners. The RBAC runner uses zero-row/session-temporary/disposable-object
probes and accepts only permission-layer rejections. The limit runner requires
the configured user property and bounded `SLEEP(31)` timeout. The audit runner
correlates the exact representative query ID with identity, target, EOF state,
query time, and workload group. Their exact source set has now been built and
scanned and pushed under immutable ECR digest
`sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510`,
but it has not been deployed. They remain unavailable to ECS until a
separately approved Terraform-managed task revision; they did not alter the
revision-8 Phase 6-7 task. Evidence:
`docs/verification/GOAL-06-LATER-PHASE-VERIFIERS-OFFLINE-2026-08-18.md` and
`docs/verification/GOAL-06-LATER-PHASE-IMAGE-ECR-PUSH-2026-08-18.md`.

The connected revision-10 RBAC retry exposed one Doris 4.0.1-specific caveat:
`DELETE ... WHERE FALSE` is constant-folded to an empty relation and returns
before Doris checks `LOAD_PRIV`. The corrected DELETE evidence contract first
uses the same query-only identity to require that reserved `TINYINT` key `127`
is absent from the disposable `goal6_authorization_probe`, then attempts a
DELETE with `WHERE probe_id = 127`. A failed or non-zero precondition stops
before DELETE; an allowed DELETE still fails closed. This forces a real table
authorization path while the proved-absent target guarantees zero affected
rows. INSERT and UPDATE retain their existing deterministic zero-row probes.
No production/serving or Unity Catalog object is a negative-test target.

## Primary references

- [Databricks Iceberg REST external access](https://docs.databricks.com/aws/en/external-access/iceberg)
- [Databricks credential vending](https://docs.databricks.com/aws/en/external-access/credential-vending)
- [Databricks Unity Catalog integrations](https://docs.databricks.com/aws/en/external-access/integrations)
- [Apache Doris Iceberg REST catalog](https://doris.apache.org/docs/3.x/lakehouse/metastores/iceberg-rest/)
- [Apache Doris Iceberg catalog](https://doris.apache.org/docs/4.x/lakehouse/catalogs/iceberg-catalog/)
- [Apache Doris secure MySQL transport](https://doris.apache.org/docs/4.x/admin-manual/auth/certificate/)
- [Apache Doris 5-minute quick start](https://doris.apache.org/docs/dev/getting-started/quick-start/)
- [Apache Doris ADD BACKEND](https://doris.apache.org/docs/4.x/sql-manual/sql-statements/cluster-management/instance-management/ADD-BACKEND/)
- [Apache Doris GRANT](https://doris.apache.org/docs/4.x/sql-manual/sql-statements/account-management/GRANT-TO/)
- [Apache Doris AWS deployment caveats](https://doris.apache.org/docs/dev/install/deploy-on-cloud/doris-on-aws/)
