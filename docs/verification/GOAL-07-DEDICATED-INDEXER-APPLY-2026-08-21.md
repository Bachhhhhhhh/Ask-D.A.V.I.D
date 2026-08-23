# Goal 7 dedicated indexer task definition — apply — 2026-08-21

## Status

**APPLIED — READ-ONLY POST-APPLY INSPECTION PASS — TASK NOT RUN**

The exact approved saved plan was hash-checked and applied. It contained only
the dedicated Goal 7 indexer ECS task-definition replacement. No ECS task was
launched and no unrelated AWS, Databricks, AOSS, or Terraform operation was
performed.

## Approval and apply evidence

| Item | Value |
| --- | --- |
| AWS account | `736956442295` |
| AWS region | `ap-southeast-1` |
| Saved plan SHA-256 | `735bfa4dac33aececb61d5672ca04514677c27e3105fef36cc5496c5208b1b33` |
| Terraform result | One ECS task-definition replacement |
| New revision | `ask-david-development-goal7-indexer:2` |
| Old revision | `ask-david-development-goal7-indexer:1` (INACTIVE) |
| Running ECS tasks after apply | `0` |

## Read-only revision inspection

Revision `2` is `ACTIVE` and has:

- image digest
  `sha256:08ef16bfbd3e4dbd6a940227a6fd7afab14385644eec617d02da7c8f46714669`;
- command `python -m ask_david_goal7.indexer`;
- Docker image entry point inherited (`entryPoint=null` at task level);
- `awsvpc` network mode;
- existing ECS workload task role;
- no public task was launched.

Revision `1` is `INACTIVE` and still references the previous runtime digest,
confirming that the image change was isolated to the intended indexer task
definition. The integrated-demo task definition was not part of the approved
plan and was not changed.

## Boundaries

- No `aws ecs run-task` occurred.
- No ECR push occurred in this checkpoint.
- No Terraform plan retry or destroy occurred.
- No Databricks SQL/bundle operation or AOSS data-plane mutation occurred.

## Next approval boundary

Run exactly one private, no-retry Goal 7 indexer task from revision `2` only
after a separate explicit approval. The task must use the reviewed private
subnets/workload security group, `assignPublicIp=DISABLED`, and immediate
read-only task/ENI/CloudWatch inspection. Any non-zero exit or contract failure
must stop without retry.
