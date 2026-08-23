# Goal 7 strict connected bundle validation — 2026-08-20

## Scope

One strict connected `databricks bundle validate` was run from the `databricks/`
bundle root with target `development` and profile `ask-david-development`.
Validation is read-only: no bundle deployment, job/SQL run, compute creation,
Terraform operation, AWS mutation, or data mutation occurred.

## Identity and target

| Check | Result |
| --- | --- |
| Databricks profile | PASS — `ask-david-development` |
| Workspace | PASS — `7474644358733471`, development host |
| Target/mode | PASS — `development` / `production` mode |
| Current principal | PASS — `bachvxuan@gmail.com`, governance administrator |
| Existing SQL warehouse | PASS — `757e0335c6efb51e`, reused; no new compute declared |
| Exact Goal 7 collection variable | PASS — `ask-david-development-knowledge` |
| Canonical embedding config | PASS — `databricks-gte-large-en`, dimension `1024` |
| Strict result | PASS — `Validation OK!`; no warning or error |

## Scope checks

The resolved bundle includes the existing Goal 4/5/6 resources plus one Goal 7
job, `ask-david-development-goal7-document-embedding`, with the three expected
SQL tasks: chunk preparation, vector-index outbox emission, and payload
verification. Tasks use only the existing Serverless SQL Warehouse. The
resolved run-as service principal and top-level permissions match the reviewed
development contract; no `workspace_host` variable was supplied.

## Read-only deployment plan review

A first bundle plan showed an unrelated Goal 4 update caused only by supplying
the managed-storage probe URL with a trailing slash. That plan was not
approved or deployed. A corrected read-only plan used the existing remote value
without the trailing slash and produced this exact action set:

| Action | Count | Resource |
| --- | ---: | --- |
| Create | 2 | `resources.jobs.goal7_document_embedding`; its bundle permissions |
| Update | 0 | — |
| Replace | 0 | — |
| Destroy | 0 | — |
| Skip/no-op | 14 | Existing Goal 4/5/6 resources and permissions |

Local plan artifact SHA-256:
`69ba965b1b6ed06ed82b5fb6d5aa14a94c3f5999d3f4ed0a3a9f174b128ef729`.
The artifact is local and ignored; it is not committed. The plan was later
deployed under separate approval; post-deployment evidence is recorded in
`GOAL-07-BUNDLE-DEPLOYMENT-2026-08-20.md`.

## Gate decision

Bundle configuration is **VALIDATED**, but Goal 7 is **NOT VERIFIED**. The
remaining gates are the approved Databricks SQL job run, actual synthetic
chunk/embedding writes, one OpenSearch index and document upsert/search path,
the four minimum negative tests, and the single integrated Supervisor/three
agent demo. Those operations must remain development-only and stop on any
unexpected mutation or failure.
