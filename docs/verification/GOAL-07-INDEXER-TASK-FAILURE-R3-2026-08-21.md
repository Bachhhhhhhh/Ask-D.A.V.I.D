# Goal 7 indexer task failure — runtime contract mismatch — 2026-08-21

## Status

**TASK STARTED, THEN FAILED — NO RETRY**

After the S3 gateway-prefix-list egress remediation, the separately approved
private indexer retry passed image pull and started the container. It then
exited with code `1`. No second retry was performed.

## Task evidence

- cluster: `ask-david-development-cluster`
- task definition: `ask-david-development-goal7-indexer:1`
- task ARN:
  `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/d55cce4db81641db8f0801118211ffc1`
- image digest:
  `sha256:c854fe57c92ad16be5cdb9935cfa16736164749a9812c9183157ad9417fae84f`
- network: private application subnets, workload SG,
  `assignPublicIp=DISABLED`
- started: `2026-08-21T01:18:47+07:00`
- stopped: `2026-08-21T01:19:11+07:00`
- final status: `STOPPED`
- stop code: `EssentialContainerExited`
- container exit code: `1`
- task ENI private IP: `10.42.45.18`
- image pull: **PASS**

CloudWatch stream `goal7-indexer/goal7-indexer/d55cce4db81641db8f0801118211ffc1`
contained 15 events. The sanitized diagnostic was:

```text
RuntimeError: missing required environment variable: DORIS_FE_HOST
```

## Contract analysis

The checked-in `packages/goal7-runtime/.../indexer.py` indexer entry point
requires only the Goal 7 catalog/index/AOSS/Databricks variables and does not
require `DORIS_FE_HOST`. Doris access belongs to the later integrated-demo
controlled Query Service, not the indexer. Adding a Doris variable to the
indexer would violate that boundary.

The deployed digest is therefore behaviorally inconsistent with the current
indexer contract. The task definition uses a command override to invoke
`ask_david_goal7.indexer`, but the running artifact still requested the Doris
demo variable. This is evidence of an image/source-set mismatch (or stale
image content), not a network failure.

## What did not occur

- no second retry;
- no task-definition mutation;
- no ECR push or image replacement;
- no AOSS index creation/upsert;
- no Databricks SQL/bundle operation;
- no Terraform or other AWS mutation.

## Next approval boundary

Perform an offline-only remediation to enforce a dedicated indexer image/source
contract using `docker/Dockerfile.goal7-indexer`, static checks, regression
tests, and documentation. Building/pushing a replacement image, changing the
ignored digest, creating a saved Terraform plan, and running another task each
require their own explicit approvals. Do not add `DORIS_FE_HOST` to the
indexer task as a workaround.
