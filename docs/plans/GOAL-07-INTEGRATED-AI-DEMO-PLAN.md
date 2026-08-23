# Goal 7 — Minimal integrated AI retrieval and agent demo plan

## Scope

This plan combines only the reduced Goal 7 OpenSearch, controlled-service, and
LangGraph demo responsibilities. It is development-only and synthetic-only.
It does not implement keyword/hybrid retrieval, reranking, PDF/OCR, advanced
ACLs, frontend/authentication, observability, memory, reflection, benchmarks,
or later roadmap goals.

## Components

1. Reuse the Goal 3 private AOSS endpoint and encryption/network policies.
   Terraform gates exactly one `VECTORSEARCH` collection, one least-
   privilege data policy, and the workload role's collection-conditioned
   `aoss:APIAccessAll` data-plane permission. `opensearch/index-mapping.json`
   defines the single 1024-dimensional `knn_vector` index contract.
2. Reuse the Goal 5 Markdown document. Databricks Serverless SQL normalizes it,
   splits deterministic paragraph chunks, calls the canonical
   `databricks-gte-large-en` embedding model, and writes managed Goal 7 chunk
   and indexing-outbox tables.
3. The controlled indexing service consumes that governed outbox and performs
   deterministic upserts. Retrieval uses the same model ID/dimension and
   filters `allowed_roles` before returning chunks.
4. `QueryService` generates only an approved SELECT against the Goal 6 Doris
   serving mart. `AnalyticsService` exposes only latest-versus-previous and
   contributor calculation. `MetadataService` is a minimal lookup boundary.
5. The Supervisor routes one question to exactly three specialized agents.
   Structured Data calls Query Service, Unstructured/RAG calls Retrieval
   Service, and Analytics calls Analytics Service. Supervisor synthesis merges
   values, contributor, evidence, and provenance.

## Private indexing boundary

The first connected indexing checkpoint is deliberately a single, gated ECS
Fargate task. It runs in the existing private application subnets with the
existing workload security group and a narrowly scoped workload-to-AOSS
TCP/443 security-group rule. The task uses the existing ECS workload role for
the AOSS data plane and an ECS-injected, KMS-encrypted Secrets Manager value
containing the Terraform-created workflow service-principal OAuth credentials.
It must not use the Doris external-read principal, static keys, an agent
credential, or a public address.

The task performs only this fixed sequence:

1. Read at most 100 rows from the governed
   `green_sm_ai.goal7_vector_index_outbox` through the Databricks SQL
   Statements API and validate the canonical model ID and 1024-dimensional
   vector contract.
2. Create the one approved index from `opensearch/index-mapping.json` if it
   does not exist, then deterministically upsert the synthetic chunks.
3. Generate one canonical query embedding through the same Databricks model
   and run one role-filtered AOSS vector search for `business-reader`.
4. Emit only a bounded success marker containing counts and contract metadata;
   credentials and document content are never logged.

After the index exists, the integrated demo uses a second separately gated,
one-shot private ECS task built from the same digest-pinned runtime image. It
injects only the workflow OAuth secret and the existing Goal 6 read-only Doris
query secret. Its fixed entry point constructs the three controlled services,
invokes the LangGraph Supervisor graph, and runs the approved question once.
The only additional private network path is workload security group to the
Doris FE TCP/9030, with explicit SG-scoped ingress and egress rules; no BE,
S3, Unity Catalog, or public path is opened.

The indexer image is digest-pinned and built from the repository's
`Dockerfile.goal7-indexer`. `goal_7_indexer_task_enabled` remains false by
default. Enabling it is a separate connected Terraform approval boundary; the
expected reviewed change set is limited to the workflow OAuth secret path,
its task-execution read/decrypt policy, the gated indexer task definition, the
gated integrated-demo task definition, the private workload-to-AOSS TCP/443
rule, and the private workload-to-Doris-FE TCP/9030 rule. Any public exposure,
replacement, destroy, unrelated service-principal change, or production change
stops the checkpoint.

### Private endpoint egress remediation

The first approved indexer task stopped before container startup because the
existing workload security group had no egress rules. Read-only inspection
confirmed that the Secrets Manager interface endpoint was healthy and already
allowed workload-SG ingress, so the minimal declarative correction is exactly
one standalone TCP/443 egress rule from the existing workload SG to the
existing AWS interface-endpoints SG. The rule is security-group scoped and
must not use `0.0.0.0/0` or broaden endpoint ingress. This remediation is
source/test/documentation-only until a separate saved connected development
plan is reviewed and approved; the failed task is not retried implicitly.

The subsequent single indexer attempt reached the ECR image-layer path but
timed out at a public S3 address. The S3 gateway route was healthy, while the
workload SG had no S3 prefix-list egress. The offline correction therefore
adds exactly one separate TCP/443 egress rule targeting the existing
`aws_vpc_endpoint.s3.prefix_list_id`. It must not add public CIDR egress or
change the existing interface-endpoint rule. A new saved connected plan and a
separate task approval are required after this offline change.

### Dedicated task-image contract

The first post-egress indexer task started but exited before indexing because
the deployed digest requested `DORIS_FE_HOST`, while the checked-in indexer
entry point has no Doris dependency. This is an image/source-set mismatch, not
a reason to broaden the indexer environment. The indexer and integrated demo
therefore have separate immutable image inputs: `goal_7_indexer_image` must be
built from `docker/Dockerfile.goal7-indexer` and may contain only the outbox
indexer entry point; `goal_7_demo_image` must be built from
`docker/Dockerfile.goal7-runtime` and contains the later Doris-backed demo
entry point. Terraform now requires both inputs when their corresponding task
gates are enabled and rejects sharing the same digest when both tasks are
enabled. This source-level correction is offline-only until separate image
promotion, ignored-variable update, saved-plan, and task approvals are
granted. `DORIS_FE_HOST` must never be added to the indexer task as a
workaround.

### Integrated-demo Doris egress remediation

The first integrated-demo task reached its private ENI but timed out while
connecting to the FE query port `10.42.64.238:9030`. The existing FE ingress
rule was present, but the dedicated Goal 7 task security group had no matching
TCP/9030 egress rule; its explicit egress allowlist covered only HTTPS and
S3. The minimal offline correction is exactly one standalone SG-to-SG TCP/9030
egress rule, gated only by `goal_7_demo_task_enabled`, targeting the existing
Doris FE security group. No CIDR, BE, public, or shared-workload rule is
introduced. A saved connected plan and a separate task approval are required
before applying or retrying the demo.

## Connected-planability safeguards

Goal 7 must not make the already verified Goal 6 serving state appear
replaceable. The selected Goal 6 data subnet's CIDR and availability zone are
resolved by the development root and passed into the Doris module as explicit
inputs. The module must not resolve that subnet through a data source whose
evaluation can be deferred by Goal 7 secret dependencies. The existing
`goal_6_rebuild_serving_state=true` boundary, fresh data-volume IDs,
attachments, and `prevent_destroy` protections remain unchanged.

The Goal 7 task-execution secret policy is gated by the plan-known booleans
`goal_7_indexer_task_enabled` and `goal_7_demo_task_enabled` (wired as
`goal7_secrets_enabled`). It must not derive a Terraform `count` from secret
ARN resource outputs, because those values are unknown during planning. The
policy itself remains least-privilege and contains only the exact workflow
OAuth and Doris query secret ARNs required by the enabled tasks.

Offline mock tests explicitly disable Goal 6 and Goal 7 task gates so ignored
local development inputs cannot contaminate provider-mock assertions. The
first connected retry must be a saved development plan, not a targeted plan;
it must show zero Goal 6 EBS replacement/destroy actions and only the reviewed
Goal 7 task-boundary resources. Any unexpected replacement, destroy, public,
production, or unrelated resource action stops the checkpoint.

## Approval boundary

Offline source validation may proceed without credentials. For every remaining
connected mutation, produce and review a saved development Terraform plan
before applying it or running the private indexer. Unexpected
destroy/replacement, production changes, duplicate collection/metastore, broad
network exposure, or any non-reviewed resource action stops the work and
requires approval.

The AOSS collection and synthetic Databricks outbox are present from their
separately approved checkpoints, and the digest-pinned runtime image has been
pushed to the private ECR repository. A first connected plan attempt was
stopped before producing a valid saved plan because it exposed four protected
Goal 6 EBS replacements and an unknown Goal 7 secret-policy count. Those
planability defects are corrected offline and recorded in
`docs/verification/GOAL-07-CONNECTED-PLAN-BLOCKER-REMEDIATION-2026-08-21.md`.
The next connected approval is therefore a new saved development Terraform
plan using the safeguards above. The private indexer task and integrated demo
task each require their own later approval and may run exactly once only after
that plan is applied and read-only identity/network checks pass.

### Databricks workspace network-path blocker

The dedicated private indexer revision-2 task reached `RUNNING` but failed
closed in `DatabricksSqlClient._token()` while connecting to the workspace
OAuth endpoint. It failed before reading the governed outbox or touching
OpenSearch. The current workload SG has only the reviewed AWS interface-endpoint
TCP/443 egress and S3 gateway-prefix-list TCP/443 egress; the private subnet
route does use the existing NAT gateway, but no workload SG rule authorizes the
Databricks host. This is recorded in
`docs/verification/GOAL-07-INDEXER-TASK-FAILURE-R4-2026-08-21.md`.

The offline design in
`docs/verification/GOAL-07-DATABRICKS-NETWORK-PATH-OFFLINE-DESIGN-2026-08-21.md`
requires read-only verification of an existing Databricks PrivateLink/private
connectivity path before any Terraform change. A generic `0.0.0.0/0:443`
workload rule, static SaaS IP allowlist, static credentials, new proxy, or
Network Firewall is not an approved shortcut. Connected identity/path
inspection, source implementation, saved Terraform planning, plan apply, and
the next one-shot indexer task are separate approval boundaries.

The connected revalidation is recorded in
`docs/verification/GOAL-07-DATABRICKS-NETWORK-PATH-READONLY-REVALIDATION-2026-08-21.md`.
It confirms the approved workspace is Premium and the account APIs reject
Databricks VPC endpoint/private-access inspection because the required pricing
tier is Enterprise. The project VPC has no Databricks endpoint; only the
existing NAT route can reach the public workspace hostname, while the workload
SG intentionally had no public-CIDR egress at that pre-decision checkpoint.
Goal 7 therefore stopped for an explicit architecture/security decision before
any network source change.

The Premium + NAT architecture decision has now been approved. Offline
implementation is recorded in
`docs/verification/GOAL-07-PREMIUM-NAT-OFFLINE-REMEDIATION-2026-08-21.md`.
It uses a dedicated Goal 7 task SG with explicit AWS-endpoint, S3-prefix-list,
and TCP/443 NAT paths; the shared workload SG remains unchanged. The next
boundary is a new saved connected development Terraform plan with zero Goal 6,
production, unrelated, or additional public changes. Plan apply and the next
one-shot indexer task remain separately approved checkpoints.

### AOSS vector-search diagnostic blocker

The latest private indexer attempt (R7) reached the AOSS vector-search request
but stopped with `AOSS vector search failed`. The deployed log did not preserve
the bounded HTTP/transport detail needed to distinguish authorization,
request-shape, endpoint, and response failures. The approved offline
remediation adds sanitized transport diagnostics, JSON response-shape
diagnostics, and an explicit expected-chunk acceptance diagnostic. It must not
log endpoints, request bodies, vectors, credentials, or response content.

The remediation is source/tests/documentation-only. A replacement image,
ignored digest update, saved Terraform plan, and one-shot indexer retry remain
separate approval boundaries. Goal 7 remains unverified until a fresh indexer
run produces `index-and-search-ready` and the integrated demo succeeds.

The replacement diagnostic image has since been built and pushed under the
immutable tag `goal7-indexer-aoss-diagnostics-60a6611d`; its ECR digest matches
the local digest. The ignored development digest is intentionally unchanged.
The next boundary is therefore the digest-only tfvars update followed by a
new saved connected development Terraform plan.

The integrated-demo per-agent diagnostics image was subsequently built from
source aggregate
`2e251338af4e50c40796e089c8c9c82ecb6ca3b89d272d3d25bbb65d0c317abf` and pushed
under the immutable tag
`goal7-integrated-agent-diagnostics-2e251338`. Its local and ECR digest is
`sha256:1c9b63827b30bff0783a321e95ebecb296f490d42473c81d14fed7e31747502b`.
This promotion is recorded in
`docs/verification/GOAL-07-INTEGRATED-DEMO-AGENT-DIAGNOSTICS-IMAGE-PROMOTION-2026-08-22.md`.
The ignored demo digest is intentionally unchanged. The next boundary is a
digest-only tfvars update followed by a new saved connected Terraform plan;
the task retry remains separately approved.

The digest-only update and saved plan were completed after Databricks OAuth
profiles were revalidated. Plan
`/tmp/goal7-integrated-agent-diagnostics-taskdef-20260823.tfplan` has SHA-256
`8db00b4a0f4d257ea10a34a57756007d55c4192f5118cc14295203d5986640be` and has
exactly one non-no-op action: replacement of
`module.goal7_demo.aws_ecs_task_definition.this[0]` to register the promoted
runtime digest. That exact plan was subsequently applied and registered
`ask-david-development-goal7-integrated-demo:3`; the evidence is recorded in
`docs/verification/GOAL-07-INTEGRATED-DEMO-AGENT-DIAGNOSTICS-TASKDEF-CONNECTED-PLAN-2026-08-23.md`.

### Integrated-demo per-agent diagnostics blocker

The first integrated-demo retry after the Doris FE/BE instances were started
no longer showed the earlier Doris timeout, but the task still exited with the
generic `connected Goal 7 integrated demo did not complete all agents` error.
The connected entry point previously discarded each `AgentResult.error` before
raising, so the failing controlled service could not be identified from the
CloudWatch evidence.

The approved offline remediation adds a bounded
`integrated-demo-agent-diagnostics` marker before that aggregate failure. It
reports only the fixed three agent keys, each status, whether an error exists,
and a repository-owned error category. It never logs raw errors, summaries,
provenance, SQL, endpoints, tokens, document content, or response bodies.
Missing agent results fail closed as `missing_result`, and unknown errors are
collapsed to `unclassified_error`.

This remediation changes only source, static validation, regression tests, and
documentation. Building or pushing a replacement runtime image, changing the
ignored digest, planning/applying Terraform, and running one connected retry
remain separate approval boundaries. Goal 7 remains unverified until a fresh
integrated run produces all three successful agent results and the final
acceptance evidence is recorded.

### Analytics two-period source remediation

The one approved revision-3 integrated-demo run
`e9959050378f4e9d8dcde75040a75d4d` produced bounded diagnostics showing
`structured=success`, `unstructured=success`, and
`analytics=error/analytics_insufficient_periods`. The failure is not evidence
that an Analytics Agent execution job is missing. The Analytics Agent is
intentionally behind `AnalyticsService`, whose connected adapter performs one
repository-owned, SELECT-only Databricks SQL Statements API request. Giving an
agent permission to invoke arbitrary jobs or SQL would broaden the controlled
tool boundary and is not part of this remediation.

The defect was the adapter's exact source filter: it selected only
`goal5.synthetic.events`, whose fixture contains one metric date, while the
already verified Goal 6 controlled increment supplies the second governed
period as `goal6.synthetic.serving.increment` in the same Unity Catalog
Business table. Job `227623174725080` and successful one-shot run
`438156863255366` are durable evidence that this second synthetic period was
created through the approved Goal 5 Raw to Curated to Business path.

The minimal source correction is therefore:

1. retain the direct controlled Statements API adapter;
2. allow exactly the two repository-owned synthetic dataset IDs above;
3. select at most 100 rows and reject any unapproved dataset returned by the
   SQL boundary;
4. add a separate read-only Databricks SQL readiness job that asserts both
   dataset IDs, at least two distinct metric dates, and non-null metric fields;
5. run that readiness job as an operator precondition before another billable
   integrated-demo retry. The agent never invokes this job.

The readiness job reuses the existing Serverless SQL Warehouse and creates no
cluster or data. Strict connected bundle validation for the reviewed source
aggregate `f6eac785a71b8ae090007c92c71795c0c1dceec2056b6f71e12e8a4edef4cbd3`
has now passed once with `Validation OK!`, no warning, and no error. Bundle
deployment then completed once; read-only inspection found readiness job
`853752024319384` with one SQL task on the existing warehouse and no run. The
one-shot readiness run then completed successfully as run `207820321246503`
with task attempt `0` and no retry. Replacement-image promotion, saved
Terraform planning, plan apply, and the next ECS retry remain separate
approval boundaries. The corrected runtime image was separately built and
pushed under immutable tag `goal7-analytics-two-period-58af3867`, with digest
`sha256:5ae9ece53e396313ea0a2dbfae4476933230a892eeebfb6c0ff9fbae84cd6c4f`.
No other job or SQL execution operation was performed.

The separately approved digest-only Terraform planning checkpoint updated only
the ignored development `goal_7_demo_image` input and created saved plan
`/tmp/goal7-analytics-two-period-taskdef-20260823.tfplan` (SHA-256
`f9b98f34474a4dc0bda8f7e564c3013e43d1be8fd2ff4fa1591a993e63d86d23`).
Machine-readable inspection found exactly one replacement:
`module.goal7_demo.aws_ecs_task_definition.this[0]`, caused solely by the
immutable runtime image digest change. No other managed resource action was
present; the plan has not been applied and no ECS task was run. The next
checkpoint is a separate approval to apply this exact saved plan, followed by
one private integrated-demo retry.

The hash-bound plan was then applied after account and region revalidation.
Terraform reported `1 added, 0 changed, 1 destroyed`, only for the reviewed
integrated-demo task-definition replacement. Read-only ECS inspection confirmed
revision `4` is ACTIVE and uses the exact runtime image digest
`sha256:5ae9ece53e396313ea0a2dbfae4476933230a892eeebfb6c0ff9fbae84cd6c4f`;
no task was RUNNING. No unrelated AWS/Databricks operation occurred. The next
checkpoint is separate approval for exactly one private integrated-demo retry.

The separately approved private integrated-demo retry then ran exactly once
from revision `4` in the application subnets with `assignPublicIp=DISABLED`.
Task `c49fcf39a9574162867dc934a4cc9d46` stopped with exit code `0`. Its bounded
result reported success for all three fixed agents (`structured`, `unstructured`,
and `analytics`), the canonical embedding model/dimension, and
`integrated-demo-completed`; the synthesized answer contained the synthetic
metric comparison, contributor, and neutral document evidence. No retry or
additional mutation occurred. Together with the dedicated indexer result
`index-and-search-ready`, the connected Goal 7 runtime paths are PASS. A final
connected zero-drift/acceptance review is still required before Goal 7 can be
declared VERIFIED.

The separately approved final connected Terraform zero-drift plan then
returned `No changes`. Saved plan
`/tmp/goal7-final-zero-drift-20260823.tfplan` has SHA-256
`f7e12fa235a79406de3dceb0daf4a4dd509dbc0367c50c1828720bfda5aa503b`;
machine-readable inspection found 280 resources, all `no-op`, and zero
creates, updates, replacements, or destroys. No apply or task run followed.
This satisfies the final infrastructure drift gate; the project status still
requires a durable acceptance/status review before declaring Goal 7 VERIFIED.
