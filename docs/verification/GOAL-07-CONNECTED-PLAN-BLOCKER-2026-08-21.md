# Goal 7 connected Terraform plan blocker — 2026-08-21

## Status

**BLOCKED — NO SAVED PLAN CREATED — NO APPLY**

The separately approved connected planning step refreshed the development
remote state but Terraform aborted before producing a usable saved plan. No
AWS or Databricks mutation occurred.

## Inputs

- AWS account: `736956442295`
- Region: `ap-southeast-1`
- Goal 7 image: `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/langgraph-runtime@sha256:c854fe57c92ad16be5cdb9935cfa16736164749a9812c9183157ad9417fae84f`
- `goal_7_indexer_task_enabled = true`
- `goal_7_demo_task_enabled = true`
- Terraform data directory: temporary `/tmp` path; repository cache was not modified

## Observed plan failure

Terraform displayed `10 to add, 0 to change, 4 to destroy` before aborting.
The four unexpected replacements were:

- `module.doris_serving.aws_ebs_volume.fe_data[0]`;
- `module.doris_serving.aws_ebs_volume.be_data[0]`;
- `module.doris_serving.aws_ebs_volume.fe_data_rebuild[0]`;
- `module.doris_serving.aws_ebs_volume.be_data_rebuild[0]`.

Each resource has `lifecycle.prevent_destroy`; Terraform therefore stopped
instead of producing a plan. This is outside the Goal 7 task-boundary scope
and must not be bypassed with `-target` or by disabling the guard.

Terraform also reported:

```text
Invalid count argument
module.iam.aws_iam_role_policy.task_execution_goal7_secrets
```

The policy count currently depends on secret ARN values that are unknown until
apply. The private-IP check also remained unknown until apply. These are
declarative planability issues, not evidence that an apply is safe.

## Required review before any retry

1. Resolve why the existing Goal 6 rebuild input makes all four protected
   volumes appear replaceable, without destroying or replacing any volume.
2. Make the Goal 7 task-execution policy count plan-deterministic using only
   reviewed configuration gates, while preserving exact secret ARN least
   privilege.
3. Re-run offline validation and obtain approval for a new saved connected
   plan. No retry, `-target`, apply, task run, or cloud mutation was performed
   in this checkpoint.
