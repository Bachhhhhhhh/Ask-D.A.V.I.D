# Goal 7 private indexer task failure R7 — 2026-08-21

## Approved boundary

Exactly one private ECS task was approved from
`ask-david-development-goal7-indexer:5`, with no retry. After it stopped, only
read-only ECS, ENI/attachment, and CloudWatch inspection was performed. No new
task, Terraform operation, ECR operation, Databricks operation, bundle/SQL
operation, or direct AOSS inspection was performed.

## Task and network evidence

| Attribute | Result |
| --- | --- |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/9ab8ffde9811465295d0ad6f5e31af86` |
| Task definition | `ask-david-development-goal7-indexer:5` |
| Image digest | `sha256:c48ee41c63f36a6d42b4494ceba363e37754f08da60fb50e0a2e0906facc47b0` |
| Cluster | `ask-david-development-cluster` |
| Subnet / private IP | `subnet-0a1aad220d82ef879` / `10.42.32.28` |
| ENI / SG | `eni-01b42196656f9cf2f` / `sg-0ff2bcb1d5175c931` |
| Public IP | Disabled |
| Started / stopped | `2026-08-21T10:55:46.208000+07:00` / `2026-08-21T10:56:21.528000+07:00` |
| Container exit | `1`, `EssentialContainerExited` |
| Running/retried tasks | `[]` |

The Fargate attachment was deleted after stop, as expected. No retry was
launched.

## Failure evidence

CloudWatch stream:
`goal7-indexer/goal7-indexer/9ab8ffde9811465295d0ad6f5e31af86`

The bounded log contains:

`RuntimeError: AOSS vector search failed`

The corrected Databricks embedding parser was therefore reached successfully;
this run progressed beyond the previous embedding-response failure and stopped
at the AOSS vector-search request. The current `AossClient.search()` raises a
generic error without recording bounded HTTP status/error details, so the exact
AOSS rejection cannot be independently reconstructed from this task log.

## Current checkpoint

Goal 7 remains **UNVERIFIED / STOPPED FOR OFFLINE AOSS VECTOR-SEARCH FAILURE
ANALYSIS**. The next step requires an offline source/test/documentation
remediation to add bounded non-secret AOSS search error diagnostics and
regression coverage before any new image, plan, or task approval.
