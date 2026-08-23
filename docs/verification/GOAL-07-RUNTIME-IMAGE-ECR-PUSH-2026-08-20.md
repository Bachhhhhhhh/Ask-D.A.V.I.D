# Goal 7 runtime image — ECR push checkpoint — 2026-08-20

## Status

**PUSHED — NOT DEPLOYED**

This checkpoint records the separately approved image promotion. It does not
edit ignored Terraform variables, create a Terraform plan, register ECS task
definitions, run ECS tasks, create an OpenSearch index, or mutate Databricks.

## Preflight

| Check | Result |
| --- | --- |
| AWS account | PASS — `736956442295` |
| AWS region | PASS — `ap-southeast-1` |
| Repository | PASS — `ask-david-development/langgraph-runtime` |
| Tag mutability | PASS — `IMMUTABLE` |
| Scan-on-push | PASS — enabled |
| Destination tag before push | PASS — `goal7-runtime-17a425d0` was absent |

## Promoted artifact

| Attribute | Observed value |
| --- | --- |
| Source aggregate | `17a425d0ddbcd5c3d4056eabf370357cdc6a43ef5e11f1504823176372df1633` |
| Immutable tag | `goal7-runtime-17a425d0` |
| ECR image | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/langgraph-runtime:goal7-runtime-17a425d0` |
| Remote digest | `sha256:c854fe57c92ad16be5cdb9935cfa16736164749a9812c9183157ad9417fae84f` |
| Local digest | `sha256:c854fe57c92ad16be5cdb9935cfa16736164749a9812c9183157ad9417fae84f` |
| Digest equality | PASS |

## Scan inspection

The immediate `describe-images` inspection returned no scan status, and
`describe-image-scan-findings` returned `ScanNotFoundException`. This is
recorded as **UNVERIFIED**, not as a clean scan result. No retry or alternate
scanner was run in this checkpoint.

## Boundary

The next approval is required before:

- setting `goal_7_indexer_task_enabled=true` and
  `goal_7_demo_task_enabled=true` in ignored development variables;
- setting the exact ECR digest as the image input;
- creating a saved connected Terraform plan.

Docker's local ECR login token was removed with `docker logout` after the
push. No credential was written to the repository.
