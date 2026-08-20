# Goal 6 Apache Doris serving runbook

Goal 6 adds a development-only, synthetic Apache Doris serving copy. It does
not change the system of record: governed Databricks/Unity Catalog managed
Delta UniForm Iceberg-compatible tables in approved S3 storage remain
authoritative. Doris is disposable and must be rebuilt from the allowlisted
Business source when required.

This runbook does not authorize a cloud operation. It records the only approved
execution order after separate review of each saved plan or task contract.

## Checked-in assets

- `infrastructure/modules/doris-serving/`: private FE/BE EC2, encrypted gp3
  storage, narrowly scoped security groups, IMDSv2, and KMS-encrypted logs;
- `infrastructure/modules/doris-verifier/`: private one-off Fargate admin and
  read-only verifier task definitions with separate task roles and secrets;
- `infrastructure/environments/development/goal6*.tf`: disabled-by-default
  development wiring, secret containers/versions, scoped UC identity, and
  one SSE-KMS neutral increment fixture;
- `doris/`: secret-free REST-catalog template and internal serving DDL;
- `databricks/sql/goal_06/`: controlled Raw -> Curated -> Business increment;
- `docker/Dockerfile.doris-verifier`: non-root MySQL-compatible verifier image;
- `scripts/validate_goal6.py`: credential-free static contract validator.
- `infrastructure/scripts/run-goal6-readiness-markers.ps1` and `.sh`: guarded,
  private, one-task runtime readiness evidence collectors. The Bash wrapper is
  the executable path on Linux hosts without `pwsh`; both implement the same
  fail-closed contract.

The private host bootstrap mounts Doris FE/BE logs from the encrypted data
volumes and configures the CloudWatch agent to publish them only to the
dedicated KMS-encrypted Doris log group. The same runbook enables Doris audit
logging and a bounded `goal6_readonly` workload group; the verifier result
records source dataset, refresh timestamp, query ID, row count, and duration.
The bootstrap also persists non-sensitive lifecycle markers in
`<role>-log/bootstrap-status.log`, which the dedicated log stream collects.
Before any volume mount, package installation, Docker launch, or CloudWatch
agent setup, it also emits `bootstrap-invoked` to the root console/journal path
`/var/log/goal6-doris-bootstrap.log`. An exit before successful listener
readiness emits `bootstrap-failed` with only the numeric exit code. Once the
role volume and CloudWatch agent are available, the root marker file is copied
into the encrypted role evidence stream and collected as
`{instance_id}/<role>/bootstrap-root`. These early markers distinguish a
missing/early-failing user-data run from a Doris listener failure; they never
replace the required `doris-port-ready` marker.
`doris-port-ready` for both FE and BE is required before launching an ECS
verifier; EC2 `running` state and platform checks alone are insufficient.
The exact rendered FE and BE bootstrap payloads must also pass the
Terraform-managed `ec2_user_data_is_within_aws_limit` check (`<= 16,384` bytes)
before a connected plan can be reviewed. This is a deployment-size guard only;
it does not authorize an EC2 replacement or any AWS operation.
When `goal_6_enabled=false`, the module skips all four FE/BE bootstrap and
size-check template renders. This keeps disabled foundation/Goal 4 plans from
evaluating `count = 0` resources or null secret inputs. Enabling Goal 6 restores
the unchanged bootstrap rendering and the same fail-closed size guard.
The host bootstrap must pass the official Docker discovery contract: FE gets
`FE_SERVERS` plus `FE_ID=1`, and BE gets `FE_SERVERS` plus `BE_ADDR`; it must
also fail visibly unless the private FE/BE listener becomes ready. A Docker
container ID or successful image pull alone is not application-health evidence.
The BE entrypoint initiates a private MySQL-protocol connection to FE port
`9030` to inspect membership and register the backend. Therefore both the FE
ingress and BE egress rules for that exact SG-to-SG path are mandatory. FE
also initiates heartbeat/RPC traffic to BE ports `9050`, `9060`, and `8060`,
and Doris AuditLoader follows an FE HTTP stream-load redirect to the BE
webserver port `8040`. The matching FE egress and BE ingress rules for all four
ports must remain paired. An ingress rule alone does not authorize a new
connection from the source host. These rules never use a CIDR or expose Doris
publicly.
After startup, BE initiates disk, tablet, task, and index-policy callbacks to
the FE Thrift RPC listener on TCP `9020`. That path likewise requires a paired
BE-egress/FE-ingress SG-to-SG rule. A healthy local FE `9020` listener and a
healthy local BE `9050` listener do not prove that cross-host callback path;
the private network policy must authorize it independently.
Because FE and BE first-boot execution is concurrent, BE waits through a
bounded, credential-free TCP probe for private FE `9030` before launching the
BE container. The status stream must show
`fe-registration-port-waiting` followed by `fe-registration-port-ready`.
`fe-registration-port-unavailable` is terminal evidence and stops deployment
verification; it must never trigger public ingress or an implicit task retry.
Before starting the container, bootstrap applies the official host prerequisites
(`vm.max_map_count=2000000` and `nofile=1000000`) through Terraform-owned
sysctl, PAM limits, systemd Docker limits, and an explicit container ulimit.
It also persists a bounded, redacted `container-diagnostics.log` on the
encrypted role volume when the listener is unavailable; this is diagnostic
evidence only and never authorizes an automatic retry or metadata deletion.
The bootstrap keeps the image-provided `fe.conf`/`be.conf` intact and writes
only Terraform-owned overrides through `fe_custom.conf`/`be_custom.conf`.
The Docker launch is bounded, captures its output in `docker-run.log`, and
emits `container-launch-failed` when no container ID can be established.
CloudWatch collection uses explicit status, private-IP, container, and Docker
run paths with a short flush interval rather than relying on a wildcard.
At each terminal listener state, bootstrap also emits a bounded
`container-diagnostics-summary` record containing only container presence,
state, running flag, exit code, error-present flag, and redacted-log line
count, plus a coarse `log_signal` classification (`bind`, `metadata`,
`configuration`, `exception`, `other`, or `none`). Raw `docker logs` never
enters the status stream; it remains redacted and volume-only. This summary is
the approved evidence path when the
container stream is delayed or unavailable, and it never authorizes an
automatic retry or volume reset.

For BE, `doris-port-ready` is necessary but not sufficient. The bootstrap
creates the exact encrypted-volume bind source explicitly, configures it as
`storage_root_path` with `medium:hdd`, and checks that the configured Doris
container user can write the mounted directory. It then makes a private,
bounded `SHOW BACKENDS` check through FE and accepts readiness only when the
matching BE is alive, not decommissioned, and reports non-zero total capacity.
The status stream records `be-storage-root-writable` followed by
`be-storage-capacity-ready`. Either `be-storage-root-unavailable` or
`be-storage-capacity-unavailable` is terminal evidence: stop, inspect the
durable diagnostics, and prepare a reviewed Terraform remediation. Do not
work around these markers by changing replica count, adding public access, or
creating an unmanaged data path.

When the current host bootstrap has already terminated and its host log stream
is absent, do not infer readiness from EC2 state or recreate the hosts merely
to reproduce historical markers. After separate task-run approval, use exactly
one repository wrapper:

- `run-goal6-readiness-markers.ps1` on a PowerShell host; or
- `run-goal6-readiness-markers.sh` on a Bash host.

The wrapper binds the approved account, `ap-southeast-1`, revision-8 admin task
definition, immutable image digest, both private application subnets, admin
security group, FE `10.42.64.238`, and BE `10.42.71.97`. It permits only the
image-entrypoint override `[-c, <script>]`, executes the read-only
`SHOW BACKENDS;` control-plane query, and requires a private task ENI plus exit
code zero. It must then find all five sanitized CloudWatch records: FE
`listener_state=ready`, FE `doris-port-ready` for `9030`, BE
`listener_state=ready`, BE `doris-port-ready` for `9050`, and BE
`be-storage-capacity-ready` with alive true, decommissioned false, and non-zero
total capacity. Any unavailable marker, missing row, zero capacity, task
failure, or contract mismatch stops without retry. These records prove current
FE query-listener reachability and FE-observed BE heartbeat/capacity state;
they do not rewrite the old bootstrap log or authorize refresh/DDL/DML.

The approved `2026-08-18` execution of this contract completed once with exit
code zero and emitted all five required markers. Its task ID, private
attachment, exact CloudWatch records, and no-retry result are recorded in
`docs/verification/GOAL-06-RUNTIME-READINESS-MARKERS-CONNECTED-2026-08-18.md`.
That result closes current FE/BE listener and BE capacity readiness only. It
does not itself execute or approve the Phase 6-7 admin refresh.

The separately approved Phase 6-7 admin refresh was subsequently executed once
from revision 8. It stopped with exit code zero on a private Fargate ENI and
emitted the fixed completion marker only after the temporary Unity Catalog
Iceberg REST catalog had read the allowlisted Delta UniForm source, refreshed
the internal serving copy/state, and been dropped. Do not repeat that task.
Count and representative-value parity still require the read-only verifier;
see
`docs/verification/GOAL-06-PHASE-6-7-ADMIN-REFRESH-CONNECTED-2026-08-18.md`.

The read-only verifier must emit the complete future Query Service result
contract. Its representative query, immediate `LAST_QUERY_ID()`, and summary
query run in one MariaDB session. Required output fields are `query_result`,
`source_dataset`, `refresh_timestamp`, `executed_query_id`, `row_count`, and
`execution_duration`. Source remediation of this contract is not present in
the active revision-8 image; do not run later verifier acceptance against that
revision. The exact source set has been built, scanned, and pushed under
immutable ECR digest
`sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510`,
but it has not been Terraform-registered. Update ignored tfvars, create/review
a saved plan, and apply only through separate approval boundaries. See
`docs/verification/GOAL-06-RESULT-CONTRACT-OFFLINE-REMEDIATION-2026-08-18.md`
and
`docs/verification/GOAL-06-LATER-PHASE-IMAGE-ECR-PUSH-2026-08-18.md`.

Later verifier phases use separate fixed image commands:

- `/app/doris-rbac-verify`: positive SELECT plus actual INSERT/UPDATE/DELETE/
  CREATE/ALTER/DROP/unauthorized-database denials. INSERT/UPDATE are zero-row;
  DELETE targets absent key `127` between two fixed disposable sentinel keys
  (`126`, `128`), so it is also zero-row if unexpectedly allowed. CREATE is
  session-temporary, and ALTER/DROP target only the disposable authorization
  probe.
- `/app/doris-query-limit-verify`: as the query identity, confirms its own
  `query_timeout=30` property with `SHOW PROPERTY LIKE` (the `FOR <user>` form
  requires grant-level visibility and is intentionally not used), then
  requires bounded timeout of `SLEEP(31)`.
- `/app/doris-audit-verify`: correlates the exact result-contract query ID to
  sanitized audit identity/target/EOF/query-time/workload evidence. Before the
  exact-ID lookup it reads `enable_audit_plugin` and the audit-log row count;
  it fails closed with distinct `audit-plugin-disabled`,
  `audit-plugin-unreadable`, `audit-log-empty`, or
  `audit-log-unreadable` markers instead of conflating those states with an
  exact-ID miss.

Each command requires a separately reviewed one-off private task and must stop
without retry. None exists in active revision 8. The new source image is built,
scanned, and pushed, but use these commands only after its exact digest is
Terraform-registered through its own approval boundaries. See
`docs/verification/GOAL-06-LATER-PHASE-VERIFIERS-OFFLINE-2026-08-18.md`.

After registration, invoke the three read-only-secret operations only through
`infrastructure/scripts/run-goal6-verifier.sh`. Its allowlist maps `readonly`,
`rbac`, and `query-limit` to fixed image commands, binds the exact
revision/digest/private network/task-role/secret shape, launches exactly one
task with no retry, and outputs only parsed Goal 6 JSON evidence. Rebuild and
audit are intentionally not available through this lower-privilege wrapper.
See
`docs/verification/GOAL-06-LATER-PHASE-VERIFIER-WRAPPER-OFFLINE-2026-08-18.md`.

Use `infrastructure/scripts/run-goal6-admin-operation.sh` only for the two
admin-bound later operations. `rebuild` and `audit` have distinct,
non-interchangeable confirmation switches and fixed commands. A rebuild drops
only the internal disposable serving objects and must be followed by a
separately approved admin refresh plus read-only comparison; the wrapper never
chains those tasks. Audit accepts only the exact query ID emitted by a prior
approved representative query and never falls back to the latest row, because
that would not prove correlation to the representative result. See
`docs/verification/GOAL-06-ADMIN-OPERATION-WRAPPER-OFFLINE-2026-08-18.md`.

For Phase 6-9, the bundle job is the only allowed authoritative increment
path. Its single neutral fixture is MERGEd idempotently through the existing
Goal 5 Raw, Curated, and Business tables on stable layer-specific keys. The
verify task requires one row at each layer and Business total `42.0`. The job
uses the existing Serverless SQL Warehouse and contains no Doris operation;
run a separately approved admin refresh only after the authoritative job
succeeds. See
`docs/verification/GOAL-06-PHASE-6-9-CONTROLLED-INCREMENT-OFFLINE-AUDIT-2026-08-18.md`.

When both listeners remain unavailable after the discovery, host-prerequisite,
stable-IP, and diagnostic remediations, use the separately reviewed
`goal_6_rebuild_serving_state` Terraform gate to create fresh disposable FE
metadata and BE serving-state volumes. The old encrypted volumes must remain
Terraform-managed and protected from deletion. Do not use Doris
`metadata_failure_recovery` automatically: the official documentation warns
that misuse can truncate metadata or create split-brain. A rebuild is valid
because S3/Unity Catalog remains the source of truth; it is not permission to
reset or delete a volume implicitly.

## Cost and topology boundary

The design has one private FE and one private BE, each `m7i.xlarge` (4 vCPU,
16 GiB), in a selected private data subnet. They have no public IP, SSH path,
public load balancer, or public database endpoint. Both hosts require a 30 GiB
encrypted gp3 root volume for the pinned Doris images; FE uses a separate 20
GiB and BE a separate 50 GiB encrypted gp3 data volume. Both EC2 instances and volumes are
persistent and cost-bearing; Fargate tasks are one-off and stop after each run.

The goal owns neither a production HA topology nor scheduled refresh,
OpenSearch, a controlled Query Service, agents, a new SQL warehouse, a classic
Databricks cluster, or real Green SM data.

## Offline validation

Run without cloud credentials:

```bash
make format-check
make lint
make typecheck
make test
make databricks-static
make goal5-static
make goal6-static
make security
git diff --check
```

When Terraform is installed, run only offline checks during this phase:

```bash
terraform fmt -check -recursive infrastructure
terraform -chdir=infrastructure/environments/development init -backend=false
terraform -chdir=infrastructure/environments/development validate
terraform -chdir=infrastructure/environments/development test -test-directory=tests
tflint --init --config infrastructure/.tflint.hcl
tflint --chdir=infrastructure --recursive --config infrastructure/.tflint.hcl
trivy config --skip-files '**/*.tfplan' --severity HIGH,CRITICAL --exit-code 1 infrastructure
trivy config --severity HIGH,CRITICAL --exit-code 1 infrastructure/modules/doris-serving
```

The sole Goal 6 Trivy exception is an inline `AVD-AWS-0104` annotation on the
private TCP/443 FE/BE egress resource. It is not a repository-wide ignore and
does not permit any public ingress or non-HTTPS egress.

The repository-wide source scan excludes ignored local saved-plan artifacts;
the Doris module is scanned separately to ensure its uncommitted source is
evaluated rather than a stale saved-plan snapshot.

Do not create local `terraform.tfvars`, `backend.hcl`, saved plans, image
artifacts, OAuth credentials, or secret values as part of offline work.

## Connected sequence — requires fresh approval at every step

1. Reverify AWS account `736956442295`, `ap-southeast-1`, private subnet
   selection, Terraform-managed FE/BE private IP inputs
   (`10.42.64.238`/`10.42.71.97`), instance availability, AMI/image digests,
   and Databricks
   workspace/metastore/catalog/warehouse identity read-only.
2. Build and scan the verifier image locally, then request distinct approval to
   push its immutable digest to the Terraform-created private ECR repository.
3. Set only the reviewed non-secret Goal 6 foundation inputs in ignored tfvars:
   `goal_5_source_objects_enabled=true`, `goal_6_enabled=true`, and
   `goal_6_verifier_tasks_enabled=false`. The first setting retains the three
   already verified Goal 5 source objects. Create one saved development Terraform
   plan. It must create no task definition because
   the private ECR image digest does not exist yet. Review every AWS and
   Databricks action; expected destroy/replacement/public exposure/metastore
   change is 0.
4. Apply precisely that reviewed foundation plan only after hash-bound approval.
   No CLI/UI repair is allowed after an error.
   If the BE bootstrap fails before its container starts, do not resize it
   manually. Use a separately reviewed Terraform recovery generation that
   declares sufficient root storage and deliberately replaces only the failed
   BE so cloud-init runs again. The BE data volume remains a separate,
   Terraform-owned serving-copy volume.
   The module must reject either private IP unless it is inside the selected
   data-subnet CIDR and distinct from the other host. The bootstrap must emit
   `private-ip-configured` for both hosts; a `private-ip-mismatch` marker is a
   fail-closed blocker.
   If a private verifier later receives a TCP/9030 refusal while SG/route/NACL
   evidence is `ACCEPT`, treat FE listener/process unavailability as the
   blocker. Remediate the declarative Docker discovery variables and readiness
   guard first; do not open ingress or retry a task ad hoc. The FE generation
   replacement must be visible in a new saved plan and approved separately.
5. Build and scan the verifier image locally, then request separate approval to
   push its immutable digest to the Terraform-created private ECR repository.
   Set only `goal_6_verifier_tasks_enabled=true` and the reviewed digest in the
   ignored tfvars; create and review a second saved plan for task definitions.
6. After separate hash-bound apply approval, verify private FE/BE health and
   task-definition/role/SG configuration read-only. Confirm the dedicated
   Doris log streams contain `doris-port-ready` for both FE and BE before
   requesting separate approval for each one-off admin or verifier Fargate
   task. If either marker is absent, stop; do not launch a task merely because
   EC2 is `running`. Review `container-diagnostics.log` and the
   host-prerequisite marker before proposing any further declarative change.
   Never delete a Doris metadata or serving-data volume as an implicit
   readiness fix.
   For BE, require both `doris-port-ready` and the subsequent
   `be-storage-capacity-ready` marker; listener evidence without usable
   capacity does not authorize an admin-refresh task.
7. The paired repository wrappers
   `infrastructure/scripts/run-goal6-admin-refresh.ps1` and
   `infrastructure/scripts/run-goal6-admin-refresh.sh` are the only execution
   paths for the admin task. Use PowerShell on a PowerShell host and Bash on a
   Linux host without `pwsh`. They require an explicit confirmation switch,
   verify the account, region, exact task definition revision and digest, FE,
   BE, workspace origin, private subnet list, admin security group,
   Fargate/`awsvpc` shape, task/execution roles, secret-reference names, and
   `assignPublicIp=DISABLED` before invoking one ECS RunTask. They wait for
   STOPPED, perform no retry, read the
   non-sensitive completion marker from the CloudWatch stream, and emits only
   ECS attachment plus CloudWatch metadata; it never prints secret or raw
   log-event contents. The wrapper is not executed by offline validation.
8. The admin task may create a short-lived UC REST catalog, perform an
   allowlist-checked refresh into internal Doris tables, and drop the catalog.
   It may not write Unity Catalog, S3, or the source table.
   A verifier image that introduces a new internal disposable schema object
   must not be tested merely after its task definitions are registered. Run
   the matching, separately approved admin-refresh revision first so its
   version-controlled `CREATE ... IF NOT EXISTS` migrations are applied. In
   particular, RBAC probes that target `goal6_authorization_probe` require the
   schema-bearing admin-refresh revision to complete before the RBAC verifier;
   otherwise Doris resolves a missing table before it reaches the privilege
   check, yielding `wrong-rejection-layer` rather than authorization evidence.
   The DELETE probe must not use `WHERE FALSE`: Doris 4.0.1 returns that empty
   plan before checking `LOAD_PRIV`. It can also prune a scan of an entirely
   empty partition before the privilege check. The version-controlled controlled
   admin refresh runs the versioned disposable-probe migration, which recreates
   the internal probe with a `SMALLINT` key and seeds only neutral disposable
   sentinel keys `126` and `128`;
   the query-only runner requires both to exist and reserved key `127` to be
   absent before deleting only `127`. This keeps the partition non-empty while
   preserving zero affected rows if DELETE is unexpectedly allowed. The runner
   does not rely on `disable_empty_partition_prune`, which is ineffective for
   this local OLAP path. Any failed/non-zero precondition or unexpectedly
   allowed DELETE fails closed; never seed the reserved key or target serving,
   Unity Catalog, or source data.
   Its injected workspace value must be a single HTTPS
   `*.cloud.databricks.com` origin (an optional trailing slash is normalized);
   the runner fails closed before OAuth when the value is malformed and never
   composes a double-scheme URL. Its named bootstrap administrator receives
   `ADMIN_PRIV` only at Doris's required global scope, `*.*.*`; the obsolete
   two-level `*.*` scope is invalid for `ADMIN_PRIV` and must never be restored.
9. The only repository execution path for the initial FE reachability proof is
   `infrastructure/scripts/run-goal6-fe-health.ps1`. It requires the explicit
   `-ConfirmGoal6FeHealth` switch; binds the AWS account, region, immutable
   task-definition revision/image, FE host, two private application subnets,
   and verifier SG; and requires `assignPublicIp=DISABLED`. The verifier image
   intentionally has `ENTRYPOINT ["/bin/sh"]`. ECS task-definition inspection
   correctly reports a null `entryPoint` when no task definition overrides that
   image setting; the wrapper requires that null state and binds the immutable
   reviewed image digest. It then passes exactly `-c <bounded mysqladmin TLS
   ping>` as the ECS command override. It must never pass a second `/bin/sh`,
   because that would execute `/bin/sh /bin/sh -c ...` and fail before
   `mysqladmin` runs. The
   wrapper launches exactly one task, performs no SQL or serving query, waits
   for it to stop, and accepts only exit `0` plus non-sensitive MariaDB
   listener evidence: either `mysqld is alive`, or an expected `Access denied`
   response to the deliberately passwordless ping. The latter proves private
   TCP/TLS listener reachability while confirming that anonymous access is not
   granted; it is not a query-identity success. Any other result stops without
   retry.
10. Run later read-only verifier tasks individually: freshness, least-privilege
   Doris RBAC, denied DML/DDL/database access, rebuild, and benchmark only if
   the optional scale checkpoint is separately approved.
11. Finish with a zero-drift plan, inspect stopped tasks/logs, sanitize durable
   evidence, and update project status only after every acceptance item passes.

The wrapper is intentionally parameterized rather than embedding account,
subnet, security-group, task-definition, or image values. A future approved
run must supply the Terraform-derived values and the active revision explicitly,
for example:

```powershell
./infrastructure/scripts/run-goal6-admin-refresh.ps1 `
  -ExpectedAccountId 736956442295 `
  -Region ap-southeast-1 `
  -NamePrefix ask-david-development `
  -Cluster ask-david-development-cluster `
  -ApplicationSubnetIds subnet-<application-a>,subnet-<application-b> `
  -AdminSecurityGroupId sg-<goal6-admin> `
  -TaskDefinition ask-david-development-doris-admin-refresh:2 `
  -ExpectedRevision 2 `
  -ExpectedImage 736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier@sha256:<approved-digest> `
  -ConfirmGoal6AdminRefresh
```

That command remains an independently approved connected operation; adding the
wrapper does not authorize a task run.

On the current Linux execution host, use the reviewed Bash wrapper with the
same Terraform-derived values and additionally bind FE `10.42.64.238`, BE
`10.42.71.97`, and workspace origin
`https://dbc-7f3363e3-d129.cloud.databricks.com`. Its exact source hash and
offline evidence are recorded in
`docs/verification/GOAL-06-PHASE-6-7-ADMIN-REFRESH-BASH-WRAPPER-OFFLINE-2026-08-18.md`.

## Stop conditions

Stop before mutation and request review if a plan proposes an Internet-facing
endpoint, CIDR ingress, static S3 credentials, a Glue/Hive catalog, a source
table change, a non-allowlisted source, production action, replacement or
destroy, source format incompatibility, a secret in output/log/source, or any
failed task. The remediation must remain declarative and receive a new plan and
approval.

After a failed task-start inspection, the approved offline remediation must
remain Terraform-owned: the existing AWS interface-endpoint SG receives narrow
Goal 6 admin-SG-to-endpoint and verifier-SG-to-endpoint TCP/443 rules only.
The shared ECS execution role retains one exact-ARN policy for the three Goal
6 Secrets Manager containers plus `kms:Decrypt` on the Secrets KMS key. Do not
grant wildcard secrets/KMS actions, broaden endpoint ingress to CIDRs, or retry
a task before a new saved plan is reviewed and approved.
