# Goal 5 corrected CDC bundle deployment

Date: 2026-08-13
Scope: one approved deployment of the exact source set that passed strict
connected validation. No workflow, job, SQL, table/data mutation, compute
creation, Terraform operation, or AWS operation was performed as part of this
checkpoint.

## Reviewed source

| Item | Result |
| --- | --- |
| Bundle aggregate | `bd4cd49ee07147f9f240a10b936c78dad76b9dca62622b10f0fb62f6318eb3cd` |
| Corrected CDC SQL | `databricks/sql/goal_05/04_ingest_cdc.sql` |
| Corrected CDC SQL hash | `9ce80b73ec48bf0a7568fad81faf791f286dbfbae4c66ca0a9af84fe013f66fd` |
| Target/profile | `development` / `ask-david-development` |
| Workspace | `7474644358733471`; principal `bachvxuan@gmail.com` |
| Warehouse | `757e0335c6efb51e`, existing Small/PRO Serverless, auto-stop 10 minutes |

The deployment used the reviewed Terraform-derived variables and did not pass
`workspace_host`.

## Deployment result

The one approved command completed successfully:

```text
Uploading bundle files to /Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development/files...
Deploying resources...
Updating deployment state...
Deployment complete!
```

Bundle summary remained `ask-david-goal-04-lakehouse`, target `development`,
with the existing six job identities. The Goal 5 job remained
`382877731318442` (`ask-david-development-goal5-synthetic-ingestion`) rather
than creating a duplicate job.

## Immediate read-only inspection

- The Goal 5 job remained `MULTI_TASK`, with six SQL tasks.
- All six tasks continued to use warehouse `757e0335c6efb51e`.
- Run-as remained workflow service principal
  `b2bdec62-62db-432d-bc6f-1f92b78053b0`.
- The deployed CDC workspace file was exported read-only from
  `/Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development/files/sql/goal_05/04_ingest_cdc.sql`.
- Exported deployed CDC SQL hash matched the reviewed local hash exactly:
  `9ce80b73ec48bf0a7568fad81faf791f286dbfbae4c66ca0a9af84fe013f66fd`.
- Exported SQL contained the shared temporary view
  `goal5_cdc_unique_events` and all three downstream references to that view.
- Job run history contained only the two pre-deployment runs
  `616649104578361` and `1025066514456351`; no run was triggered by this
  deployment.

## Boundary and next checkpoint

Deployment and read-only inspection passed. This does not prove the corrected
CDC SQL executes successfully. The next separately approved step is exactly
one workflow run of job `382877731318442` on the existing warehouse, followed
by immediate task/run inspection. Any failed task stops the sequence; no
implicit retry is allowed. Idempotency and output/quality/provenance and
authoritative Tables API checks remain subsequent evidence requirements.
