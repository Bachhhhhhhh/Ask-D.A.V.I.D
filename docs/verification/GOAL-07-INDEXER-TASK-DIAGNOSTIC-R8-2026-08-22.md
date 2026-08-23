# Goal 7 private indexer diagnostic task R8 — 2026-08-22

## Approved boundary

Exactly one private ECS indexer task was run from revision 8, with no command
override and no retry. After it stopped, only ECS/ENI and CloudWatch
read-only inspection was performed. No Terraform, ECR, Databricks, SQL, AOSS
control-plane, or additional task operation was performed.

## Task evidence

| Field | Result |
| --- | --- |
| Account / region | `736956442295` / `ap-southeast-1` |
| Cluster | `ask-david-development-cluster` |
| Task definition | `ask-david-development-goal7-indexer:8` |
| Image digest | `sha256:1be0e8d301f136230795d16bc086a0a90823646f4ca239155924ca13837e5779` |
| Subnet / ENI / private IP | `subnet-034f5f1c9bca753f1` / `eni-0739b67f391f5e352` / `10.42.28.93` |
| Public IP | Disabled |
| Container exit code | `0` |
| Final task status | `STOPPED` |

CloudWatch stream:
`goal7-indexer/goal7-indexer/6fa87db116564f38b79a153c31f685de`

## Result contract

The task emitted:

```json
{"collection":"ask-david-development-knowledge","embedding_dimension":1024,
"embedding_model_id":"databricks-gte-large-en","goal":"goal-07",
"index":"synthetic-document-chunks","indexed_chunks":1,"role_filter":"business-reader",
"search_hits":1,"status":"index-and-search-ready"}
```

This is PASS evidence for the Databricks outbox → embedding → AOSS index and
role-filtered vector-search path for the neutral synthetic chunk.

## Current checkpoint

The dedicated indexer acceptance is PASS. Goal 7 as a whole remains
UNVERIFIED until the integrated Supervisor + three-agent demo and its required
negative authorization checks pass.
