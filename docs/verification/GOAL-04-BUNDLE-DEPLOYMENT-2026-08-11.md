# Goal 4 bundle deployment

## Scope and approval boundary

This is a historical deployment record. A later read-only inspection found
that the deployment also synchronized the nested remediation file despite the
non-recursive include pattern; the original 12-file inventory statement below
is superseded by that finding. The file was not referenced by a job and was not
executed.

This report records the separately approved deployment of the strictly
validated Goal 4 development bundle. The approval covered aggregate source
SHA-256
`022cebf1d12e8a22d5e9f7f57b1a5d9d4ca28dede7f71666b09ea1bfc318ec7e`,
target `development`, profile `ask-david-development`, five job definitions,
12 synchronized SQL files, and immediate read-only inspection. It did not
authorize a job/SQL run, compute creation, Terraform operation, or AWS
mutation.

## Deployment result

Databricks CLI `1.11.0` completed all deployment stages:

1. uploaded files to
   `/Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development/files`;
2. deployed resources;
3. updated bundle deployment state;
4. returned `Deployment complete!` with exit `0`.

## Deployed resource inventory

| Bundle resource | Job ID | Run as | Tasks |
| --- | ---: | --- | ---: |
| Synthetic managed-Iceberg pipeline | `967410491586823` | Workflow service principal | 8 |
| Managed-Iceberg history verification | `695423086105630` | Workflow service principal | 1 |
| Lineage verification | `825751066015430` | `bachvxuan@gmail.com` | 1 |
| Denied table-access verification | `187789722076444` | Denied-test service principal | 1 |
| Denied direct-path verification | `992194321630936` | Denied-test service principal | 1 |

Every task references existing Serverless SQL Warehouse
`757e0335c6efb51e`. The later inspection found 13 top-level SQL files plus the
nested `remediation/01_drop_delta_uniform_synthetic_tables.sql`; this is the
bundle-sync leak being remediated.

## Post-deployment inspection

| Check | Result |
| --- | --- |
| Bundle summary resolves exactly five jobs | PASS |
| Job names, task files, run-as identities, and warehouse IDs match source | PASS |
| Synchronized SQL file count at original inspection | SUPERSEDED — 12 top-level files |
| Nested destructive remediation file absent | FAIL — file was present |
| Active job runs | PASS — empty list |
| Existing warehouse state | PASS — `STOPPED` |
| Warehouse size/type | `Small`, `PRO`, serverless enabled |
| Warehouse cost controls | Maximum 1 cluster; auto-stop 10 minutes |
| Cluster inventory | PASS — empty list |

The first active-runs inspection used `--active-only true`, which CLI `1.11.0`
rejected as an extra positional argument. The corrected read-only command used
the boolean flag `--active-only` and returned an empty list. No task was
started by either inspection command.

## Next approval boundary

Bundle deployment is complete. Before any billable SQL execution, separately
approve one run of job `967410491586823`, the eight-task authorized synthetic
managed-Iceberg pipeline. Its source-set SHA-256 is
`651e9779baf3e230230e6c948860d281e2bc2fd527cf35b1fc551fe76e1b4165`.
The run must use the existing Small Serverless SQL warehouse, stop on failure,
and must not implicitly retry, redeploy, run verification/negative jobs,
create compute, execute Terraform, or mutate AWS outside normal governed table
I/O through Unity Catalog.
