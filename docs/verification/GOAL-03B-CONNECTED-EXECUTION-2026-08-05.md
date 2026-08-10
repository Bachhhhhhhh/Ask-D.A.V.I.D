# Goal 3B connected execution verification — 2026-08-05

## Scope and provenance

This report records the connected development execution in AWS account
`736956442295`, region `ap-southeast-1`. It is not an assertion that Goal 3B
is complete. The tracked report becomes immutable only when its reviewed
source change is committed.

Terraform was the only mechanism used to create or change AWS infrastructure.
AWS CLI calls were limited to STS identity, CloudTrail troubleshooting, and
read-only smoke-test inspection. No secret value, S3 object data, or real
Green SM data was retrieved.

## Reviewed plan and apply evidence

| Item | Result |
| --- | --- |
| Bootstrap saved plan | Applied separately after explicit approval; its state was migrated to the encrypted S3 backend. |
| Initial development saved plan | `0e3c653b34e9283e59d7dc3064cc17a9f50034e5e7bb314a8a7178e97c213470`; partial apply exposed a missing CloudWatch Logs KMS key-policy permission and an ElastiCache API failure. |
| Remediation | The observability KMS key policy now authorizes only `logs.ap-southeast-1.amazonaws.com` and only the runtime and VPC-flow log-group encryption contexts. Terraform mock tests passed for this policy. |
| Replacement development saved plan | `9d57e708ae0d687d84258646c399549a40ee77bc4d38ac536cc662b4f84d4b00`; reviewed as 4 additions, 1 in-place change, 0 destroys. |
| Replacement apply | PASS — `4 added, 1 changed, 0 destroyed`. |
| Post-apply drift check | PASS — `terraform plan -detailed-exitcode` exited `0`: `No changes. Your infrastructure matches the configuration.` |
| Plan-artifact cleanup | PASS — the ignored saved plan was deleted after apply and drift verification. |

The first retry of the replacement plan failed before state could be loaded
because Docker bridge DNS timed out while resolving the S3 backend. The plan
hash and AWS identity were rechecked; a read-only state-list check through
Docker host networking succeeded before the exact same approved plan was
applied. This was a local transport failure, not an AWS mutation.

## Dynamic smoke-test saved plan — 2026-08-06

After offline validation, the connected development plan for the static smoke
task definitions was created against the approved account and region. Its
ignored artifact was stored only in a local temporary directory until the
approved apply completed.

| Item | Result |
| --- | --- |
| Saved-plan SHA-256 | `b4c073514bf5154e7295319c782b1f8963a451d0fb85995d9e404b13fc841e87` |
| Account and region | `736956442295`, `ap-southeast-1` |
| Planned actions | `8 to add, 0 to change, 0 to destroy` |
| Scope | Three one-off Fargate task definitions; two tightly scoped IAM roles; two inline role policies; one AWS-managed execution-policy attachment. |
| Apply | PASS — after explicit approval, `8 added, 0 changed, 0 destroyed`. |
| Post-apply task check | PASS — the ECS cluster reported no running task. |
| Post-apply drift check | PASS — `terraform plan -detailed-exitcode` returned `0`: `No changes. Your infrastructure matches the configuration.` |
| Plan-artifact cleanup | PASS — the saved plan and temporary source/state copies were removed after apply and drift verification. |
| Non-actions | No ECS service, Fargate task launch, secret value retrieval, S3 object access, database write, network modification, or destruction. |

The plan created configuration only. It did not launch a task, so the apply
itself incurred no Fargate task runtime cost.

## Dynamic smoke-test diagnostic — 2026-08-06

The approved PostgreSQL smoke task was launched once after its task definition,
identity, digest, private subnet, and no-public-IP configuration were checked.
The initial attempt could not be reconstructed to a durable exit result after
delayed inspection, so it is not verification evidence. It imported the
pull-through-cache image and had a private ENI, but did not justify launching
Redis or S3.

The approved PostgreSQL revision-2 retry used a private ENI in an application
subnet with no public IP and the dedicated smoke security group. It stopped
before the container started with `TaskFailedToStart` / `CannotPullContainerError`:
the pull of the digest-pinned account-private pull-through-cache image timed
out while connecting to a public ECR IP on TCP/443. It has no container exit
code because the container never started. No secret value, task log, database
result, S3 object data, or business data was retrieved. Redis and S3 smoke
tasks were not launched, as the approved conditional runtime sequence required
a zero PostgreSQL exit code first.

Read-only inspection confirmed that the ECR API and Docker interface endpoints
were `AVAILABLE`, had private DNS enabled, and accepted HTTPS from the smoke
security group. Fargate nevertheless resolved the pull target publicly. The
first network/ECR remediation, saved-plan SHA-256
`06b9c095db6165b571c89f014f8deb73345a0a758454ae064c67ec8bda241a3f`,
was applied after approval as `15 added, 0 changed, 3 destroyed`; it created
the isolated smoke group, ECR pull-through cache, and revision-2 definitions.

The pending, source-only remediation changes only that isolated synthetic
smoke group: it permits temporary TCP/443 egress through the existing NAT
gateway so a Fargate pull that resolves publicly can proceed. It remains
private (no public task IP), uses only reviewed digest-pinned images, and is
documented by a resource-level Trivy suppression. It is not connected planned
or applied at the time of this report update and must never be reused by a
service, agent, or general workload.

The first saved NAT-fallback plan, SHA-256
`8cb44a4ee44ad072c3df602fc8570d6f9b3de7558592e0779ecfe52d26d1ef6e`,
was **rejected and was not applied**. In addition to the intended HTTPS-rule
replacement, it proposed updates to the RDS, Redis, and AWS-endpoint security
groups that would remove their standalone smoke ingress rules. The cause was
an IaC modeling conflict: each group mixed an inline workload ingress rule
with a standalone smoke ingress rule. The approved follow-up source fix moves
all of those ingress rules to standalone resources before a replacement plan
is requested.

The replacement plan, SHA-256
`772abca96d7e82757153e23f0309e2f5858d55bb051edd1a0813092a675218ac`,
was also **rejected and was not applied**. It correctly retained the smoke
ingress rules, but proposed three creates for workload ingress rules that
already exist in AWS. Read-only inspection identified their existing rule IDs:
RDS `sgr-05b601d138b2aa153`, Redis `sgr-08f686af3d412b3c9`, and AWS endpoints
`sgr-0a6582981c3911ad6`. Terraform cannot automatically adopt inline rules
into standalone-resource state. A separately approved Terraform state import
of exactly those IDs is required before a new plan can prove that only the
smoke HTTPS replacement remains.

After explicit approval, all three existing rules were imported successfully
into the development remote state at their corresponding
`aws_vpc_security_group_ingress_rule` addresses. A read-only state-list check
confirmed the three mappings, and an immediate AWS read-only inspection still
showed all three workload rules and all three smoke rules with their original
IDs and source security groups. The imports changed Terraform state ownership
only; they did not create, modify, or delete an AWS resource. A fresh saved
plan remains separately approval-gated.

The fresh saved development plan has SHA-256
`98f18cceb241e2a0997f71bbb28adcb344f6c4f5d4978e9f23f4b236b835f2e8`
and was reviewed as `1 to add, 3 to change, 1 to destroy`. The add/destroy
pair is only the expected replacement of smoke TCP/443 egress from the AWS
endpoint security-group reference to `0.0.0.0/0` through the existing NAT.
The three in-place changes add the mandatory project tags to the imported RDS,
Redis, and AWS-endpoint workload ingress rules; JSON review confirmed their
protocol, port, destination security group, and source workload security group
do not change. At review time, the plan had not been applied and remained in a
local temporary directory pending separate approval.

The exact plan was then applied after approval for account `736956442295` and
region `ap-southeast-1`: `1 added, 3 changed, 1 destroyed`. The replacement
HTTPS egress rule is `sgr-0e6de964451572027`. Immediate read-only inspection
confirmed it is attached only to the dedicated smoke security group, permits
only TCP/443 to `0.0.0.0/0`, and has all mandatory tags. The three imported
workload rules retained their original ports and workload security-group
source and received only the mandatory tags. The ECS cluster still reported
zero running tasks; the apply did not launch a smoke task.

## Dynamic runtime smoke after NAT fallback — 2026-08-06

The approved runtime sequence verified the exact revision-2 task definitions,
pinned image digests, task/execution roles, Fargate/`awsvpc` mode, one-container
shape, two private application subnets, dedicated smoke security group, and
`assignPublicIp=DISABLED`. The local machine did not have PowerShell, so the
same wrapper guards and sequential launches were executed directly with AWS
CLI. No Terraform plan, apply, destroy, ECS service, or arbitrary task was run.

| Check | Task | Result |
| --- | --- | --- |
| PostgreSQL TLS `SELECT 1` | `3094f2ee9a8344319b97965ef8bfde4d` | PASS — revision 2 exited `0` with private IP `10.42.23.200` in `subnet-034f5f1c9bca753f1`. |
| Redis TLS `PING` | `298664c3b3a24c7f9e77c049aec27557` | FAIL — revision 2 started successfully but exited `1` with private IP `10.42.21.3`. Its only log message was `Unrecognized option or bad number of args for: '--host'`. The static command must use the supported `redis-cli -h` option. |
| S3 Raw allow / Curated deny | `9b972798b5ae407f8b8d2ce68b73608d` | PASS — revision 2 exited `0` with private IP `10.42.47.247` in `subnet-0a1aad220d82ef879`; no object body or metadata listing was retrieved. |

All task ENIs were deleted immediately after task stop, before a separate
Association lookup could run. The launch requests explicitly disabled public
IP assignment, both selected subnets have `MapPublicIpOnLaunch=false`, and ECS
attachment metadata recorded only private IPv4 addresses. The ECS cluster
reported zero running tasks after the sequence. VPC Flow Logs created streams
for all three task ENIs with current ingestion timestamps, confirming delivery
during the synthetic checks without reading flow-record payloads.

The Redis failure is a deterministic static-command defect, not a Redis
network, TLS-handshake, container-pull, or infrastructure-start failure. No
secret value or real Green SM data was read or printed. Only the Redis command
requires source remediation and a separately approved Terraform task-definition
revision/apply before retry.

The approved source-only remediation changed exactly the Redis endpoint option
from `--host` to `-h` and added a contract assertion that requires `-h` and
rejects `--host`. Offline development validation and two root contract tests
passed; the smoke-test module contract passed; TFLint passed; and Trivy reported
zero HIGH/CRITICAL findings while recognizing the existing resource-scoped NAT
fallback suppression. No connected plan, apply, AWS operation, or task launch
was performed during this source remediation.

The approved connected plan step produced saved-plan SHA-256
`d87a748332dbc0d2730caa8992085254eba9beeac3486463dc1277cc74acaf6d`.
It was reviewed as `1 to add, 0 to change, 1 to destroy`, replacing only
`module.smoke_test.aws_ecs_task_definition.this["redis"]`. JSON review
confirmed the only functional command change is `--host` to `-h`; the pinned
image digest, task role, execution role, Fargate configuration, and all other
resources are unchanged. The plan has not been applied and no task was run.

The exact plan was applied after separate approval: `1 added, 0 changed,
1 destroyed`. Terraform registered
`ask-david-development-smoke-redis:3` and deregistered revision 2 from managed
state. Immediate read-only inspection confirmed revision 3 is `ACTIVE`, uses
the corrected `redis-cli -h` command, retains the reviewed digest, roles,
Fargate/`awsvpc` configuration, and one-container shape. PostgreSQL and S3
remain revision 2. The cluster reported zero running tasks; the apply did not
launch Redis or any other task. The saved-plan artifact was deleted after use.

The separately approved Redis revision-3 retry ran as task
`9c6b9c20b0ee4effac422feacbac80d1`. It started its container in private
application subnet `subnet-034f5f1c9bca753f1` with private IP
`10.42.17.184`, then exited `1`. Its only task-log message was
`Unrecognized option or bad number of args for: '--port'`. The first command
fix was effective because `--host` was no longer rejected; the pinned
`redis-cli` also requires the short port option `-p` instead of `--port`.
The task ENI's VPC Flow Log stream has current event/ingestion timestamps, and
the ECS cluster reported zero running tasks after the retry. No additional
retry, plan, apply, destroy, secret read, or business-data access occurred.

The approved second source-only remediation changed exactly the Redis port
option from `--port` to `-p`. The regression assertion now requires
`redis-cli -h ... -p 6379` and rejects both unsupported `--host` and `--port`.
Offline development validation and two root contract tests passed; the
smoke-test module contract passed; TFLint passed; and Trivy reported zero
HIGH/CRITICAL findings while recognizing the existing resource-scoped NAT
fallback suppression. No connected apply or task launch was performed during
this source remediation.

On `2026-08-07`, the separately approved connected development plan for the
second Redis command remediation was saved locally with SHA-256
`33195976e34877c2b27824f8706d7526c3c22657c3ed006f926c2f4af3751a46`.
Offline JSON review found exactly one non-no-op resource change: replacement
of `module.smoke_test.aws_ecs_task_definition.this["redis"]` because its
container definition changes `--port 6379` to `-p 6379`. The pinned image
digest, task role, and execution role are unchanged. The exact artifact was
then applied after separate approval: `1 added, 0 changed, 1 destroyed`.
Terraform registered `ask-david-development-smoke-redis:4` and deregistered
revision 3 from managed state. Immediate read-only inspection confirmed
revision 4 is `ACTIVE`, uses the reviewed `redis-cli -h ... -p 6379` command,
and retains the reviewed digest, roles, Fargate compatibility, and `awsvpc`
network mode. The ECS cluster reported zero running tasks; the apply did not
launch Redis or any other task. The saved-plan artifact remains local and is
not committed.

The separately approved Redis revision-4 retry ran exactly once as task
`7fcaec5eb6a24f8d8d0d63d70983a1cf`, protected against duplicate launch by an
ECS client token. It used the two approved private application subnets, smoke
security group `sg-0ef6cd84adeccf1b7`, and `assignPublicIp=DISABLED`. The task
started in `subnet-034f5f1c9bca753f1` with private IP `10.42.30.237`, stopped
with container exit code `0`, and emitted only the expected
`REDIS_TLS_SMOKE_PASS` marker. ECS had already removed ENI
`eni-0d8ca4edbe1ce9ec1` before a later Association query, so no claim is based
on a surviving ENI association; the launch request disabled public IP and the
task attachment reported only its private address. VPC Flow Log stream
`eni-0d8ca4edbe1ce9ec1-all` had current event and ingestion timestamps, without
reading flow-record payloads. The cluster reported zero running tasks after
the retry. No additional task, Terraform plan/apply/destroy, secret read, or
business-data access occurred.

## VPC Flow Logs remediation addendum — 2026-08-06

The first connected smoke inspection found that the VPC-flow CloudWatch log
group existed but no VPC Flow Log delivered into it. The following reviewed
remediation was then implemented and validated offline:

- an `ALL`-traffic VPC Flow Log with a 600-second aggregation interval;
- a dedicated delivery role trusted only by `vpc-flow-logs.amazonaws.com`,
  restricted by the approved account and VPC Flow Log source ARN; and
- an inline delivery policy that can create streams and put events only in the
  approved VPC-flow log group.

The saved plan
`959576ab058d69c71fe7bd472ed40ca0899ccb5efc56a129de75b0e47f63fde4`
was reviewed as 3 additions, 0 changes, and 0 destroys, then applied after
explicit approval: 3 added, 0 changed, 0 destroyed. The post-apply detailed
drift plan exited `0`. The flow log is `ACTIVE` with
`DeliverLogsStatus=SUCCESS`. No log stream exists yet because no VPC traffic
was intentionally generated after creating it.

## Final zero-drift plan and acceptance gap — 2026-08-07

The separately approved final development plan ran with
`-detailed-exitcode`, refreshed the approved account `736956442295` in
`ap-southeast-1`, and exited `0`: `No changes. Your infrastructure matches the
configuration.` Its local saved artifact has SHA-256
`d898f91cb24ba788cba5bb0406e86a558f8681cd47107789accd6ccd1d0ddb54`.
Offline JSON review with Terraform `1.10.5` confirmed zero non-no-op resource
changes and zero non-no-op output changes. The artifact was not applied; no
task or destructive operation ran.

Zero drift does not by itself prove that the configuration implements the
approved plan. The acceptance review found that the approved Goal 3 plan
assigns base alarms to the observability module, makes alarm thresholds
environment inputs, and requires CloudWatch alarm verification in Checkpoint
3B. `docs/INFRASTRUCTURE.md` also states that a base RDS CPU alarm exists.
However, neither the Goal 3A commit nor the current Terraform tree contains an
`aws_cloudwatch_metric_alarm`, an alarm-threshold input, or a smoke assertion
for an alarm. AWS and Terraform agree because both omit the accepted alarm
scope. This is an implementation/verification gap, not infrastructure drift,
and prevents a Goal 3B `VERIFIED` claim.

## Base RDS CPU alarm remediation — offline implementation 2026-08-07

After the owner approved the reviewed remediation plan and selected
`rds_cpu_alarm_threshold_percent = 90`, the source-only implementation added:

- exactly one five-of-five, one-minute average `AWS/RDS` `CPUUtilization`
  alarm for the Terraform-managed DB instance;
- the required root/module threshold input and typed RDS identifier output;
- the existing encrypted alert topic as the alarm's only action, with no
  subscription, OK action, or insufficient-data action;
- `kms:GenerateDataKey*` and `kms:Decrypt` for
  `cloudwatch.amazonaws.com`, limited to the same account and exact alarm ARN;
- positive/negative Terraform contract tests, exact KMS-policy regression
  coverage, a required-variable preflight test, and read-only alarm runbook
  checks that do not change state or publish a message.

Offline results: Terraform formatting and development validation passed; two
development-root tests passed; three observability tests passed; one KMS test
passed; TFLint passed; Trivy reported zero HIGH/CRITICAL findings; five
preflight unit tests passed; Ruff formatting/lint and strict mypy passed; full
pytest passed 14 tests with 96.67% coverage; Bandit, detect-secrets, and the
checked-in environment validation passed. PowerShell execution was not
available for the read-only script, so that script received static review only.
`pip-audit` could not run offline because it attempted to query PyPI.

The actual ignored development `terraform.tfvars` was outside the approved
source/tests/docs edit scope and initially lacked the new assignment. Under a
later local-input-only approval, `rds_cpu_alarm_threshold_percent = 90` was
added on `2026-08-08`; strict offline preflight then passed with a structurally
valid state KMS key ARN. No connected Terraform plan, apply, destroy, AWS API
operation, task launch, subscription, alarm-state change, or notification
publish occurred during this local-input checkpoint.

## Base RDS CPU alarm remediation — saved plan review 2026-08-08

Under separate approval limited to connected planning, Terraform `1.10.5`
refreshed the development state for account `736956442295` in
`ap-southeast-1` and created a local saved plan. No apply, destroy, or task ran.
The saved artifact SHA-256 is
`d3cfa2db71da41020eabe109913eba2fa97117176f0e7e13cfdc8a965c159712`.

Offline `terraform show -json` review confirmed:

- input account `736956442295`, Region `ap-southeast-1`, and threshold `90`;
- exactly one create:
  `module.observability.aws_cloudwatch_metric_alarm.rds_cpu_high`;
- exactly one in-place update: `module.kms.aws_kms_key.observability`;
- no replacement paths, no destroy, and no other managed-resource action;
- the alarm contract is `AWS/RDS` `CPUUtilization`, `Average`, `Percent`,
  `GreaterThanThreshold`, five of five 60-second periods, threshold `90`, and
  `treat_missing_data = "missing"` for DB instance
  `ask-david-development-postgres`;
- the existing encrypted alert topic is the only alarm action, with no OK or
  insufficient-data action;
- the existing account-root and CloudWatch Logs KMS statements are unchanged;
  the only added statement grants `kms:GenerateDataKey*` and `kms:Decrypt` to
  `cloudwatch.amazonaws.com`, constrained to the exact source account and
  exact alarm ARN.

The artifact was local and unapplied when reviewed. A later approval was bound
to this SHA-256, but the temporary artifact was no longer present when its hash
was checked immediately before apply. No apply command ran and no AWS resource
was changed by that attempt. A new saved plan requires separate plan approval
and review; the expired hash-bound apply approval must not be reused.

Under separate replacement-plan approval on `2026-08-08`, Terraform `1.10.5`
created a new saved plan at the Git-ignored workspace path
`infrastructure/environments/development/rds-cpu-alarm-remediation-20260808.tfplan`.
Its SHA-256 is
`db143549fe551a397afac6b88248b8be74b48b689fa8a685c6868af43816f331`.
Offline JSON review reconfirmed account `736956442295`, Region
`ap-southeast-1`, threshold `90`, exactly the same alarm create and in-place
observability KMS policy update, no replacement paths, no destroy, and no other
managed-resource action. The exact alarm contract and KMS statement match the
earlier review; the existing root and CloudWatch Logs KMS statements remain
unchanged. The replacement artifact exists locally and is Git-ignored.

Under separate hash-bound approval, Terraform applied that exact artifact as
`1 added, 1 changed, 0 destroyed`. It updated the observability KMS key policy
in place and created alarm `ask-david-development-rds-cpu-high`; no replacement,
destroy, or task ran.

Immediate read-only CloudWatch inspection confirmed `AWS/RDS`
`CPUUtilization`, DB identifier `ask-david-development-postgres`, `Average`,
`Percent`, `GreaterThanThreshold`, five of five 60-second periods, threshold
`90`, `treat_missing_data = "missing"`, actions enabled, the existing encrypted
alert topic as the only alarm action, and empty OK/insufficient-data action
lists. The new alarm naturally reported `INSUFFICIENT_DATA`; no alarm-state
mutation or synthetic load was used. Read-only KMS inspection confirmed the
exact `cloudwatch.amazonaws.com` publisher statement, actions, source account,
and alarm ARN, while the root and CloudWatch Logs statements remained present.
No notification was published. A separately approved final zero-drift plan is
still required at this chronological checkpoint and is recorded next.

## Final post-remediation zero-drift plan — 2026-08-08

Under separate plan-only approval, Terraform `1.10.5` refreshed development
state for account `736956442295` in `ap-southeast-1` and exited `0` with
`No changes. Your infrastructure matches the configuration.` The Git-ignored
saved artifact SHA-256 is
`db9ec9f069bf03d724689d1cf2a3347a43dd63c18df81f99463f18bf649d78be`.
Offline `terraform show -json` review reconfirmed account
`736956442295`, Region `ap-southeast-1`, threshold `90`, zero non-no-op
managed-resource changes, and zero non-no-op output changes. No apply, destroy,
or task ran during this checkpoint.

## Final offline blocker remediation — 2026-08-10

The final change-set review accepted deterministic connected configuration
inspection as the unauthorized-path rejection proof. RDS is non-public; RDS
and Redis occupy private data subnets; their security groups have no CIDR
ingress and name only the exact workload/smoke source groups on their service
ports. The ALB is internal with private-CIDR ingress, and the AOSS policy
disables public access and names only the approved VPC endpoint. These enforced
default-deny controls prove that other network sources are rejected without
running another billable or transient negative task.

The review also removed the runtime-smoke wrapper's race-prone EC2 ENI lookup
after task stop. The wrapper now fixes `assignPublicIp=DISABLED` in the launch
request and validates the stopped task's durable ECS attachment contains both
an ENI ID and private IPv4 address. A Python regression test requires that
contract and rejects reintroduction of `describe-network-interfaces`.

Final commit-candidate validation passed: recursive Terraform formatting;
strict preflight; bootstrap/development validation; 9 Terraform contract runs;
TFLint; Trivy with zero HIGH/CRITICAL findings; Ruff formatting/lint; strict
mypy; 15 pytest tests with 96.67% coverage; Bandit; detect-secrets; checked-in
environment validation; `pip-audit` with no known vulnerabilities; pre-commit
large-file, merge-conflict, YAML, end-of-file, and trailing-whitespace hooks;
and `git diff --check`. Terraform format, Ruff, mypy, detect-secrets, and pytest
were run directly and therefore skipped rather than duplicated in the final
pre-commit invocation. PowerShell was not available, so the wrapper received
static regression coverage rather than a local PowerShell execution. No AWS
API, Terraform connected plan/apply/destroy, ECS task, alarm mutation, or
notification occurred during this remediation and validation.

## Connected verification results

| Check | Result | Evidence |
| --- | --- | --- |
| Approved IAM identity, account, and region | PASS | STS returned the approved non-root IAM user in account `736956442295`; all Terraform/AWS checks used `ap-southeast-1`. |
| Development state backend | PASS | Bootstrap created an encrypted/versioned/public-blocked S3 state bucket, and development state was read successfully through its distinct `development/terraform.tfstate` key. A lock-contention test was not run. |
| S3 foundation | PASS | All seven managed buckets report `aws:kms`, versioning `Enabled`, and all four public-access-block controls `true`; each returned `KeyCount: 0`. |
| PostgreSQL foundation | PASS | PostgreSQL 16.13 on `db.t4g.micro` is storage-encrypted, deletion-protected, not publicly accessible, and uses only the intended RDS security group. |
| Redis foundation | PASS | The `cache.t4g.micro` replication group is `available`, encrypted in transit and at rest, and uses the private data-subnet group and Redis security group. |
| ECS and ALB foundation | PASS | ECS cluster is active with zero tasks and zero services; the Application Load Balancer is active with `scheme=internal`. |
| IAM and secret containers | PASS (foundation) | Dedicated ECS execution/workload roles trust only `ecs-tasks.amazonaws.com`; workload access is limited to runtime logging/X-Ray. Three KMS-encrypted secret containers exist; no secret value was retrieved. |
| OpenSearch Serverless foundation | PASS | Private AOSS endpoint is active in the two application subnets; network policy allows only that endpoint and `AllowFromPublic=false`; encryption/network policies exist; no `ask-david` collection exists. |
| Observability | PASS | KMS rotation is enabled; the runtime and VPC Flow Log encryption contexts remain present; both log groups exist with 30-day retention and that key; the alert topic and VPC Flow Log exist. The deployed base RDS CPU alarm matches the accepted metric, dimension, five-of-five evaluation, threshold `90`, missing-data, and action contract. The observability KMS policy contains the exact-account, exact-alarm CloudWatch publisher grant while preserving its prior root and Logs statements. |
| VPC Flow Log delivery | PASS | Terraform state and AWS show an `ALL`-traffic VPC Flow Log targeting the approved log group, `ACTIVE`, and `DeliverLogsStatus=SUCCESS`. Streams for the three latest task ENIs have current ingestion timestamps. No flow-record payload was retrieved. |
| Dynamic runtime smoke tests | PASS | PostgreSQL revision 2 passed TLS `SELECT 1`; S3 revision 2 passed Raw allow / Curated deny; Redis revision 4 passed TLS `PING` with the corrected `-h ... -p 6379` command. Each task used a private application subnet, the dedicated smoke security group, and `assignPublicIp=DISABLED`; the cluster returned to zero running tasks. |
| Unauthorized-path rejection | PASS — DETERMINISTIC CONFIGURATION ENFORCEMENT | Connected inspection confirmed RDS is not public and both RDS and Redis are in private data subnets. Their security groups have no CIDR ingress and allow only the exact future-workload and dedicated synthetic-smoke security groups on ports `5432` and `6379`; security-group default deny rejects every other source. The internal ALB allows only `10.42.0.0/16`. The AOSS network policy has `AllowFromPublic=false` and names only the approved VPC endpoint. The S3 smoke actively proved Curated access was denied to the Raw-list-only task role. An additional negative Fargate task would retest these deterministic controls while adding cost and transient execution scope, so it was not required or run. |
| ECR foundation | PASS | Both repositories are immutable, scan-on-push enabled, and encrypted with ECR server-side encryption. |
| Goal-boundary review | PASS | No Databricks, Unity Catalog, Doris, AOSS collection/index/document, agent, tool-service, application task definition, ECS service, or Green SM business-data resource was created. Exactly three static synthetic smoke task definitions exist only for Goal 3B validation. The ECR repository named `langgraph-runtime` is an empty runtime foundation only, not a deployed LangGraph agent. |

## Result and required remediation

**Goal 3B connected acceptance passes. Repository status remains PARTIALLY
VERIFIED until the evidence is committed.** PostgreSQL TLS, Redis TLS, S3
authorization, private task launch configuration, VPC Flow Log delivery, the
base RDS CPU alarm, its exact KMS publisher grant, read-only alarm inspection,
and the final post-remediation zero-drift plan all have passing evidence. Redis
revision 4 passed with the reviewed `-h ... -p 6379` correction. No Goal 4
resource or real Green SM data was introduced.

Before a repository-level `GOAL 3B VERIFIED` claim, review and commit the
current Goal 3B source, tests, documentation, and durable verification evidence
as an isolated checkpoint. No infrastructure destroy or additional task
execution is authorized.
