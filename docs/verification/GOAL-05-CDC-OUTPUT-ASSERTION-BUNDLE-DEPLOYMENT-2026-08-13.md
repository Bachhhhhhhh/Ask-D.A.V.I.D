# Goal 5 CDC output-assertion bundle deployment

Date: 2026-08-13
Scope: one approved redeployment of the source set that passed the fresh strict
bundle validation. No workflow, job/SQL execution, table/data mutation,
Terraform operation, or AWS operation was performed as part of this checkpoint.

## Reviewed source and environment

| Item | Result |
| --- | --- |
| Bundle aggregate | `e06e5e26ac83aa0ea30c93f12b747686cef67e3d80f9cb862998f931477dd507` |
| Corrected output SQL | `databricks/sql/goal_05/05_verify_goal5_outputs.sql` |
| Output SQL hash | `594824b4b647de6451cf57fdd83bf927137a4122f4b0010aff09042b7596cb30` |
| Target/profile | `development` / `ask-david-development` |
| Workspace/principal | `7474644358733471` / `bachvxuan@gmail.com` |
| Existing warehouse | `757e0335c6efb51e`, Small/PRO Serverless, auto-stop 10 minutes |
| Active Goal 5 runs before deploy | none |

The existing warehouse was already `RUNNING` before deployment. No new
warehouse or compute was created.

## Deployment result

The one approved deployment completed successfully:

```text
Uploading bundle files to /Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development/files...
Deploying resources...
Updating deployment state...
Deployment complete!
```

## Immediate read-only inspection

- Goal 5 job identity remains `382877731318442`, with name
  `ask-david-development-goal5-synthetic-ingestion`.
- It remains a six-task SQL workflow with no new job identity or compute.
- Run-as remains workflow service principal
  `b2bdec62-62db-432d-bc6f-1f92b78053b0`.
- Every task retains warehouse `757e0335c6efb51e` and its approved source or
  catalog parameters.
- The synchronized output-verification file was exported read-only from the
  bundle workspace path. Its SHA-256 exactly matched the reviewed local source:
  `594824b4b647de6451cf57fdd83bf927137a4122f4b0010aff09042b7596cb30`.
- Run history still contains only runs `149148676670509`, `616649104578361`,
  and `1025066514456351`; deployment did not trigger a workflow.

## Boundary and next checkpoint

The numeric CDC output assertion is now deployed. The next separately
approved step is exactly one workflow run of job `382877731318442`, followed
by immediate run/task inspection. No implicit retry, second workflow,
Terraform, AWS operation, or ad-hoc SQL is authorized. Subsequent idempotency,
output/quality/provenance, and authoritative Tables API evidence remain
required.
