# Goal 7 integrated-demo diagnostics task definition — connected plan — 2026-08-23

## Approved boundary

The approved operation was limited to changing the ignored development
`terraform.tfvars` demo image digest, running offline preflight, and creating
and reviewing one saved connected development Terraform plan. No apply, ECS
task run, ECR push, Databricks mutation, SQL run, bundle operation, or other
AWS mutation was performed.

## Revalidation

| Check | Result |
| --- | --- |
| Databricks workspace profile | PASS — `ask-david-development`, Valid YES |
| Databricks account profile | PASS — `ask-david-account`, Valid YES |
| AWS account | PASS — `736956442295` |
| AWS region | PASS — `ap-southeast-1` |
| Demo tfvars change | PASS — only `goal_7_demo_image` changed to the promoted digest |
| Goal 7 static validation | PASS |
| Goal 7 regression tests | PASS — 34 passed |

## Saved plan

| Field | Value |
| --- | --- |
| Plan artifact | `/tmp/goal7-integrated-agent-diagnostics-taskdef-20260823.tfplan` |
| Plan SHA-256 | `8db00b4a0f4d257ea10a34a57756007d55c4192f5118cc14295203d5986640be` |
| Target account / region | `736956442295` / `ap-southeast-1` |
| Expected task image digest | `sha256:1c9b63827b30bff0783a321e95ebecb296f490d42473c81d14fed7e31747502b` |

The JSON plan contained exactly one non-`no-op` resource change:

| Address | Actions | Scope |
| --- | --- | --- |
| `module.goal7_demo.aws_ecs_task_definition.this[0]` | `delete`, `create` | Register the next integrated-demo task-definition revision with the new digest |

The previous digest was
`sha256:5ebd63499e5baaef628ebbd4ae77d8e3a714f3037b05ea2f40d1f7f60808eeb4`;
the planned replacement uses the promoted diagnostics digest above. There are
zero unrelated changes, zero production changes, zero network/IAM/KMS/S3/
Databricks/AOSS changes, and zero ECS task runs.

## Subsequent outcome

The exact saved plan was subsequently approved and applied, registering
`ask-david-development-goal7-integrated-demo:3`. One separately approved
private retry then ran as task
`e9959050378f4e9d8dcde75040a75d4d` and exited `1`. Its bounded diagnostic
marker identified `structured=success`, `unstructured=success`, and
`analytics=error/analytics_insufficient_periods`. No additional retry was
performed. The offline root-cause analysis and remediation are recorded in
`docs/verification/GOAL-07-ANALYTICS-TWO-PERIOD-OFFLINE-REMEDIATION-2026-08-23.md`.
Goal 7 remains **UNVERIFIED**.
