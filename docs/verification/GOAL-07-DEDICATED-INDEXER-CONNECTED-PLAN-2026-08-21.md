# Goal 7 dedicated indexer image — connected saved plan — 2026-08-21

## Status

**SAVED PLAN CREATED AND REVIEWED — NO APPLY**

The approved image-input update was applied only to ignored local development
variables, followed by a connected Terraform refresh and saved plan against the
existing development remote state. No apply, destroy, ECS task, ECR push,
Databricks operation, or AOSS data-plane mutation occurred in this checkpoint.

## Identity and inputs

| Item | Value |
| --- | --- |
| AWS account | `736956442295` |
| AWS region | `ap-southeast-1` |
| Terraform root | `infrastructure/environments/development` |
| Backend | Existing encrypted S3 development state, key `development/terraform.tfstate` |
| Indexer image | `.../langgraph-runtime@sha256:08ef16bfbd3e4dbd6a940227a6fd7afab14385644eec617d02da7c8f46714669` |
| Demo image | `.../langgraph-runtime@sha256:c854fe57c92ad16be5cdb9935cfa16736164749a9812c9183157ad9417fae84f` |
| Task gates | `goal_7_indexer_task_enabled=true`, `goal_7_demo_task_enabled=true` |

The two task inputs are distinct, as required by the offline image/source
contract remediation.

## Saved artifact

- Plan: `/tmp/goal7-dedicated-indexer-plan/goal-07-dedicated-indexer.tfplan`
- JSON review: `/tmp/goal7-dedicated-indexer-plan/plan.json`
- Plan SHA-256:
  `735bfa4dac33aececb61d5672ca04514677c27e3105fef36cc5496c5208b1b33`
- Terraform data directory: `/tmp/goal7-dedicated-indexer-plan/tfdata`
- Local repository state/backend files were not modified.

## Exact action review

The filtered `terraform show -json` action set contains exactly one managed
resource change:

| Address | Provider | Actions | Reason |
| --- | --- | --- | --- |
| `module.goal7_indexer.aws_ecs_task_definition.this[0]` | AWS | `delete, create` replacement | Register the dedicated indexer image digest |

Plan summary: **1 to add, 0 to change, 1 to destroy**, representing only that
single ECS task-definition replacement. The integrated-demo task definition
does not change because its runtime digest remains the existing reviewed
digest. There are zero actions for IAM, KMS, security groups, networking,
ECR, EC2, EBS, S3, Secrets Manager, AOSS, Databricks, production, public
exposure, or Goal 8+ resources.

The first plan attempt encountered a state-lock precondition. Read-only
inspection found no active Terraform process and no lock object; the retry
used the normal lock with a bounded timeout and produced the saved artifact.
No force-unlock or lock deletion was performed.

## Validation

| Check | Result |
| --- | --- |
| Offline infrastructure preflight | PASS |
| Terraform init against approved backend | PASS |
| Connected refresh/plan | PASS |
| Saved plan hash | PASS |
| JSON action filtering | PASS — exactly one replacement |
| Apply/destroy | NOT RUN |
| ECS task | NOT RUN |
| Databricks/AOSS mutation | NOT RUN |

## Next approval boundary

Applying this exact plan requires separate approval bound to SHA-256
`735bfa4dac33aececb61d5672ca04514677c27e3105fef36cc5496c5208b1b33`.
After apply, inspect the new task definition read-only; running the private
indexer task requires another explicit no-retry approval.
