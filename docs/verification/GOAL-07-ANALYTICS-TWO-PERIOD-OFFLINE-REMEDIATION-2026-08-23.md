# Goal 7 Analytics two-period blocker — offline remediation — 2026-08-23

## Status

`OFFLINE IMPLEMENTED / CONNECTED BUNDLE VALIDATION PASS / GOAL 7 NOT VERIFIED`

## Approved boundary

This checkpoint permits source, tests, documentation, and offline validation
only. It does not authorize a connected bundle validation or deployment,
Databricks SQL/job run, image build/push, ignored Terraform input change,
Terraform plan/apply/destroy, ECS task, or AWS/Databricks mutation.

## Failure evidence

The reviewed diagnostics image was registered as task definition
`ask-david-development-goal7-integrated-demo:3`. Its one approved private run,
task `e9959050378f4e9d8dcde75040a75d4d`, exited `1`. The bounded CloudWatch
diagnostic marker reported:

| Agent | Result |
| --- | --- |
| Structured Data Agent | `success` |
| Unstructured Data / RAG Agent | `success` |
| Analytics Agent | `error`, category `analytics_insufficient_periods` |

No retry occurred after this evidence was collected.

## Root cause

The Analytics Agent does not need a Databricks job to execute each request.
Its fixed path is:

```text
Analytics Agent
  -> AnalyticsService
  -> DatabricksAnalyticsExecutor
  -> Databricks SQL Statements API
  -> governed Unity Catalog Business table
```

`DatabricksAnalyticsExecutor` filtered the Business table to only
`goal5.synthetic.events`. The Goal 5 fixture contributes only one distinct
`metric_date`, so `AnalyticsService` correctly rejected the response because a
latest-versus-previous comparison requires at least two periods.

The required second governed period already exists. Goal 6 job
`ask-david-development-goal6-controlled-increment` (`227623174725080`) ran once
successfully as run `438156863255366` and created
`goal6.synthetic.serving.increment` through the approved Goal 5 Raw to Curated
to Business path. Durable evidence is in
`GOAL-06-PHASE-6-9-INCREMENT-CONNECTED-2026-08-20.md`. The blocker was therefore
an over-narrow query allowlist, not a missing agent-callable job and not
missing business data.

## Minimal durable correction

- Define exactly two approved analytics datasets:
  `goal5.synthetic.events` and `goal6.synthetic.serving.increment`.
- Query only those IDs from the existing governed Business table.
- Include `dataset_id` in the response, cap results at 100 rows, and fail
  closed if the response contains an unapproved dataset.
- Keep the Analytics Agent behind the typed service boundary. It receives no
  general SQL, job-run, Databricks, AWS, Doris, or OpenSearch capability.
- Add `ask-david-development-goal7-analytics-readiness`, a read-only SQL job
  that reuses the existing Serverless SQL Warehouse and asserts both dataset
  IDs, at least two distinct periods, and non-null metric fields.
- Treat the readiness job as an operator pre-run gate only. The Analytics
  Agent never invokes it.

## Security and architecture review

| Check | Result |
| --- | --- |
| Exactly three specialized agents | Preserved |
| Controlled tool-service boundary | Preserved and narrower than job execution |
| Arbitrary SQL/job execution | Not introduced |
| Unity Catalog governance | Preserved; reads the existing governed Business table |
| S3/Iceberg system of record | Unchanged |
| Doris responsibility | Unchanged; Analytics remains a governed Databricks read |
| Real Green SM data | Not introduced; both IDs are neutral synthetic fixtures |
| New compute | Not declared; readiness reuses the existing Serverless SQL Warehouse |
| Goal 8+ scope | Not introduced |

## Offline validation

| Command | Result |
| --- | --- |
| `python3 scripts/validate_goal7.py` | PASS |
| `python3 -m pytest -p no:cacheprovider -o addopts='' -q tests/unit/test_goal7_static.py` | PASS — 39 tests |
| `python3 -m compileall -q packages/goal7-runtime/src/ask_david_goal7 scripts/validate_goal7.py tests/unit/test_goal7_static.py` | PASS |
| `git diff --check` | PASS |
| Ruff | NOT RUN — neither `uv` nor a system Ruff module is available in this execution environment |
| mypy | NOT RUN — neither `uv` nor a system mypy module is available in this execution environment |

The focused tests cover the two-dataset query, row bound, unexpected-dataset
rejection, malformed-response rejection, and read-only readiness SQL. These
offline results do not prove live table contents, bundle validity, deployment,
or a successful Analytics Agent run.

The deterministic aggregate over the files below is
`f6eac785a71b8ae090007c92c71795c0c1dceec2056b6f71e12e8a4edef4cbd3`:

- `databricks/bundles/goal_07_retrieval/**`;
- `databricks/sql/goal_07/**`.

Individual bundle inputs for the next validation boundary are:

| File | SHA-256 |
| --- | --- |
| `databricks/databricks.yml` | `517004df0021baf4e8e558108dbee05292952392aa9262dd38c7e5956ff12312` |
| `databricks/bundles/goal_07_retrieval/resources.yml` | `75cb6ba0dbc7f545b4700bad8dcf658e6e9d1cb3b316647457f61393a041c1b9` |
| `databricks/sql/goal_07/04_verify_analytics_source.sql` | `e9e67a089e5512eaa8ac702da4ca7ea90c06aa259fbaf4eb76124f72b60b2a56` |

## Remaining approval boundaries

Strict connected bundle validation is PASS. Remaining boundaries are:

1. Bundle deployment review; expected persistent change includes the new
   readiness job and synchronized SQL file only.
2. Replacement runtime image build/promotion and digest inspection.
3. Ignored tfvars update and a saved Terraform plan limited to the integrated
   demo task-definition revision.
4. Separate apply approval.
5. Exactly one private integrated-demo retry.

Any readiness failure, unexpected bundle resource change, unapproved dataset,
Terraform drift, task failure, or architecture mismatch stops the sequence.

## Strict connected bundle validation

The separately approved validation ran exactly once from `databricks/` with
target `development`, profile `ask-david-development`, and no
`workspace_host` variable. The reviewed bundle source aggregate was
`f6eac785a71b8ae090007c92c71795c0c1dceec2056b6f71e12e8a4edef4cbd3`.

| Check | Result |
| --- | --- |
| Target/profile | PASS — `development` / `ask-david-development` |
| Workspace path | PASS — user-scoped development bundle path |
| Validation result | PASS — `Validation OK!`, exit code `0` |
| Warning/error | PASS — none reported |
| Deployment | NOT RUN |
| Job/SQL execution | NOT RUN |
| Compute creation | NOT RUN |
| Terraform/AWS operation | NOT RUN |

The next boundary is a separately approved bundle deployment. It must be
reviewed for the expected Goal 7 readiness-job and synchronized SQL resource
changes only; no job or SQL run is implied by validation success.

## Bundle deployment and read-only inspection

The separately approved deployment of the same aggregate source completed once
with exit code `0` and `Deployment complete!`. Read-only inspection confirmed
the expected readiness job only:

| Check | Result |
| --- | --- |
| Job name | `ask-david-development-goal7-analytics-readiness` |
| Job ID | `853752024319384` |
| Task | `verify_analytics_source` only |
| SQL path | `/Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development/files/sql/goal_07/04_verify_analytics_source.sql` |
| Warehouse | Existing `757e0335c6efb51e` |
| New compute | None declared |
| Concurrent runs / queue | `1` / disabled |
| SQL execution | NOT RUN |

The exported deployed SQL SHA-256 is
`e9e67a089e5512eaa8ac702da4ca7ea90c06aa259fbaf4eb76124f72b60b2a56`, matching
the reviewed local source. No job retry, SQL execution, Terraform, AWS
operation, or additional bundle mutation occurred.

## Readiness-job execution

The separately approved readiness job ran exactly once as a one-time run:

| Check | Result |
| --- | --- |
| Job ID / run ID | `853752024319384` / `207820321246503` |
| Trigger | `ONE_TIME` |
| Run state | `TERMINATED / SUCCESS` |
| Task | `verify_analytics_source`, task run `506288770663965` |
| Task state | `TERMINATED / SUCCESS`, attempt `0` |
| Warehouse | `757e0335c6efb51e` |
| Retry/repair | None |

The readiness contract passed for both approved datasets, at least two metric
periods, and non-null metric fields. No other job or SQL task was run.

## Runtime image promotion

The separately approved local build and ECR push completed successfully.

| Check | Result |
| --- | --- |
| Source aggregate | `58af38676b6478c8fa8df3a388dee0b29148595251c58cd1338ac1f990fe133c` |
| Local image ID | `sha256:5ae9ece53e396313ea0a2dbfae4476933230a892eeebfb6c0ff9fbae84cd6c4f` |
| ECR tag | `goal7-analytics-two-period-58af3867` |
| ECR digest | `sha256:5ae9ece53e396313ea0a2dbfae4476933230a892eeebfb6c0ff9fbae84cd6c4f` |
| Repository | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/langgraph-runtime` |
| Image contract | PASS — non-root `65532:65532`; network-disabled import PASS |
| Registry scan status | UNVERIFIED — registry returned `null`; no scan retry |

No ignored Terraform input, task definition, ECS task, Databricks resource,
or AWS resource other than the approved ECR image push was changed.

## Saved Terraform plan for runtime promotion

Under the separately approved plan-only boundary, the ignored development
`terraform.tfvars` was updated only for `goal_7_demo_image` to the promoted
immutable digest
`sha256:5ae9ece53e396313ea0a2dbfae4476933230a892eeebfb6c0ff9fbae84cd6c4f`.
Offline Goal 7 preflight and the focused regression suite remained PASS.

The connected development plan was then created and inspected without apply:

| Check | Result |
| --- | --- |
| Saved plan | `/tmp/goal7-analytics-two-period-taskdef-20260823.tfplan` |
| Plan SHA-256 | `f9b98f34474a4dc0bda8f7e564c3013e43d1be8fd2ff4fa1591a993e63d86d23` |
| Account / region | `736956442295` / `ap-southeast-1` |
| Non-no-op action count | `1` |
| Managed action | `module.goal7_demo.aws_ecs_task_definition.this[0]`: `delete` + `create` replacement |
| Reason | Integrated-demo task definition image digest update only |
| Other AWS/Databricks actions | `0` |
| Apply / ECS task | NOT RUN |

The machine-readable saved-plan inspection used the initialized Terraform
provider cache and returned exactly the single replacement above. The plan is
unchanged and awaits a separate hash-bound apply approval. A successful plan
does not verify the runtime; one private integrated-demo retry remains after
apply.

## Saved-plan apply and post-apply inspection

The hash-bound apply was approved and executed directly from the saved plan.
Terraform revalidated account `736956442295` and region `ap-southeast-1`, then
reported `1 added, 0 changed, 1 destroyed`, corresponding to the reviewed
replacement of the integrated-demo task definition only.

Read-only ECS inspection confirmed:

| Check | Result |
| --- | --- |
| Task definition | `ask-david-development-goal7-integrated-demo:4` |
| Status | `ACTIVE` |
| Image | `.../langgraph-runtime@sha256:5ae9ece53e396313ea0a2dbfae4476933230a892eeebfb6c0ff9fbae84cd6c4f` |
| Network mode / size | `awsvpc` / `512` CPU / `1024` MiB |
| Running tasks immediately after apply | `0` |
| ECS task run | NOT RUN |

No additional Terraform, AWS, Databricks, SQL, or bundle operation occurred.
The next and separate boundary is exactly one private integrated-demo retry;
runtime success remains unverified until that run produces all three successful
agent results and its acceptance evidence.

## Integrated-demo retry result

The separately approved one-shot private retry then ran from revision `4` with
the reviewed application subnets, Goal 7 task security group, and
`assignPublicIp=DISABLED`. No command override or retry was used.

| Check | Result |
| --- | --- |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/c49fcf39a9574162867dc934a4cc9d46` |
| Task definition | `ask-david-development-goal7-integrated-demo:4` |
| Subnet / private IP | `subnet-0a1aad220d82ef879` / `10.42.33.233` |
| Public IP | Disabled |
| Final status | `STOPPED` |
| Container exit code | `0` |
| Retry/repair | None |

The bounded CloudWatch result was:

```json
{"agent_statuses":{"analytics":"success","structured":"success","unstructured":"success"},"embedding_dimension":1024,"embedding_model_id":"databricks-gte-large-en","goal":"goal-07","status":"integrated-demo-completed"}
```

The answer contained the latest-versus-previous synthetic metric comparison,
contributor, and neutral document evidence. This is PASS evidence for the
Supervisor and exactly three-agent controlled-service path. The dedicated
indexer acceptance is already PASS in
`GOAL-07-INDEXER-TASK-DIAGNOSTIC-R8-2026-08-22.md`; the remaining Goal 7
checkpoint is a final connected zero-drift/acceptance review before any status
claim of VERIFIED.

## Final connected zero-drift plan

After the successful integrated-demo retry, the separately approved final
connected Terraform plan revalidated account `736956442295`, region
`ap-southeast-1`, and the complete development state. Terraform reported
`No changes. Your infrastructure matches the configuration.`

| Check | Result |
| --- | --- |
| Saved plan | `/tmp/goal7-final-zero-drift-20260823.tfplan` |
| Plan SHA-256 | `f7e12fa235a79406de3dceb0daf4a4dd509dbc0367c50c1828720bfda5aa503b` |
| Total resource changes inspected | `280` |
| Non-no-op actions | `0` |
| Creates / updates / replacements / destroys | `0 / 0 / 0 / 0` |
| Apply / destroy / ECS task | NOT RUN |

Machine-readable inspection returned an empty non-no-op action list. This is
the final infrastructure zero-drift evidence; no Terraform mutation followed.
