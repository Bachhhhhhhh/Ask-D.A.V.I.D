# Goal 7 indexer preflight — blocked — 2026-08-21

## Status

**BLOCKED BEFORE TASK RUN — DATABRICKS AUTHENTICATION INVALID**

The separately approved read-only readiness preflight was fail-closed before
any ECS task execution. The Databricks CLI inventory reported the named
development profile as `Valid: NO`, and the warehouse inspection could not
authenticate. No credentials or token values were printed.

## Consequences

- ECS indexer task run: **NOT RUN**
- ECS retry: **NOT RUN**
- Databricks SQL: **NOT RUN**
- OpenSearch index creation/upsert/search: **NOT RUN**
- Terraform/AWS mutation: **NOT RUN**

The AWS task-definition foundation remains applied from the separately
approved plan. The next action requires the user to complete interactive
Databricks OAuth login for the existing `ask-david-development` profile. After
login, readiness must be revalidated in a new approval boundary; this failed
preflight is not permission to retry the task.
