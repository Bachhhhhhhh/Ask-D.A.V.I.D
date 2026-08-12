# Goal 4 lineage acceptance remediation

## Scope and boundary

This report records the approved offline-only remediation of the Goal 4
lineage acceptance contract. It does not authorize connected bundle
validation/deployment, a lineage job or SQL run, table/data mutation,
Terraform, or any AWS or Databricks operation.

## Acceptance gap

The deployed `10_verify_lineage.sql` selected only Raw-to-Curated lineage rows.
It had two acceptance defects:

1. zero result rows still completed successfully because there was no
   assertion;
2. it did not inspect the required Curated-to-Business edge.

No lineage job was run after this gap was identified. Consequently, no prior
lineage result is being promoted as verification evidence.

## Deterministic remediation

The read-only query against `system.access.table_lineage` now filters source
and target catalogs to the Terraform-managed `:catalog_name` and uses exactly
two `assert_true` checks. It fails unless these directed edges exist:

- `green_sm_raw.synthetic_events` ->
  `green_sm_curated.synthetic_events`;
- `green_sm_curated.synthetic_events` ->
  `green_sm_business.synthetic_metrics`.

The static validator requires the lineage system table, both exact directed
edge contracts, and exactly two assertions. It also rejects `INSERT`,
`UPDATE`, `DELETE`, or `MERGE` in the lineage verification SQL. Regression
tests independently remove each required edge and one assertion to prove that
the validator fails closed.

This remediation asserts deterministic table-level lineage only. It does not
claim connected visibility, workspace execution, or acceptance until the
reviewed source passes strict connected validation, is separately redeployed,
and the lineage job succeeds under a separate approval.

## Offline verification

Completed on `2026-08-11` without a connected command or cloud operation:

| Gate | Result |
| --- | --- |
| Goal 4 deterministic static validator | PASS |
| Lineage regression tests | PASS — 19 Goal 4 tests total |
| Full offline pytest suite | PASS — 37 tests |
| Branch coverage | PASS — 96.67%, threshold 90% |
| Bundle/resource YAML parsing | PASS |
| Ruff format and lint | PASS — 68 files |
| Strict mypy | PASS — 5 source files |
| Bandit | PASS |
| detect-secrets over remediation files | PASS |
| ADR, artifact, merge-marker, and diff hygiene | PASS |

`pip-audit` is not rerun because the approved gate is offline and this
remediation changes no dependency or lock file.

Reviewed source hashes after remediation:

- all bundle source files aggregate SHA-256:
  `fc68749ff6f26741212ea9a4763844c5ad7c91bdaf26cf3084070103366ee257`;
- lineage SQL SHA-256:
  `0be1b989978af4bb467fde8e336ef15a2b9cad78be62ae76c1d4fb5ad81f6a4e`;
- validation source-set SHA-256 (`databricks.yml`, `resources.yml`, and
  lineage SQL):
  `0e11799d2fb2add67c7cedd25a5bc9d74af3462f53253f8a8a819536e752e3bc`.

## Next approval boundary

The separately approved strict connected bundle validation completed with exit
`0` and `Validation OK!`. It used target `development`, profile
`ask-david-development`, the reviewed Terraform-derived variables, no
`workspace_host` variable, aggregate source SHA-256
`fc68749ff6f26741212ea9a4763844c5ad7c91bdaf26cf3084070103366ee257`,
and lineage SQL SHA-256
`0be1b989978af4bb467fde8e336ef15a2b9cad78be62ae76c1d4fb5ad81f6a4e`.
The CLI reported no warning, error, or recommendation. It resolved governance
user `bachvxuan@gmail.com` and the expected user-scoped development root.

No deployment, SQL/job run, compute creation, Terraform operation, AWS
operation, or data mutation occurred. The next boundary is a separate approval
to redeploy this exact reviewed source. Only synchronized
`10_verify_lineage.sql` content is expected to change; the five job identities
and other 11 SQL files must remain unchanged. Stop after immediate read-only
inspection and before any lineage run.

## Redeployment and read-only inspection

The separately approved redeployment of the same reviewed aggregate source
completed with exit `0` and `Deployment complete!`. It uploaded bundle files,
deployed resources, and updated deployment state without running a job or SQL
task.

Read-only inspection confirmed:

- the bundle summary resolves the same five job IDs and names;
- pipeline job `967410491586823` retains eight tasks and the workflow service
  principal;
- history job `695423086105630` retains one task and the workflow service
  principal;
- lineage job `825751066015430` retains one task, governance user
  `bachvxuan@gmail.com`, existing warehouse `757e0335c6efb51e`, and the
  expected synchronized lineage-file path;
- denied-table job `187789722076444` and denied-path job `992194321630936`
  each retain one task and the denied-test service principal;
- exported deployed `10_verify_lineage.sql` matches local source byte for byte
  and has SHA-256
  `0be1b989978af4bb467fde8e336ef15a2b9cad78be62ae76c1d4fb5ad81f6a4e`.

The first bundle-summary inspection was issued from the repository root and
failed locally because `databricks.yml` was not in that working directory. All
five direct job inspections and the file export still succeeded. The corrected
read-only summary was then run once from the `databricks/` bundle root and
passed. This was not a deploy retry or cloud mutation.

No job/SQL run, compute creation, Terraform operation, AWS operation, or table
mutation occurred during inspection. The next boundary is separate approval
for a read-only pre-run warehouse check followed by exactly one run of lineage
job `825751066015430`. Stop without retry on any task failure.

## Successful lineage verification

The separately approved lineage verification ran exactly once:

- job ID: `825751066015430`;
- run ID: `764855862302905`;
- task run ID: `628839951620135`;
- task: `inspect_table_lineage`;
- run type: `JOB_RUN`;
- task attempt: `0`;
- final run and task state: `TERMINATED / SUCCESS`;
- active runs after completion: `0`.

Pre-run inspection showed the existing approved warehouse `STOPPED`, Small,
PRO, serverless enabled, one cluster maximum, and 10-minute auto-stop. The
single read-only task ran on that warehouse as governance user
`bachvxuan@gmail.com`. Because the deployed query consists solely of two
fail-closed `assert_true` expressions, task success proves that
`system.access.table_lineage` contained both exact directed edges:

1. Raw `synthetic_events` -> Curated `synthetic_events`;
2. Curated `synthetic_events` -> Business `synthetic_metrics`.

Jobs output inspection returned no error or error trace. The API did not expose
the SQL result rows, so the deterministic assertion contract and successful
task state are the durable acceptance evidence. Immediate post-run inspection
showed the warehouse `RUNNING` only inside its configured auto-stop window.

The first active-run result was an array while the local `jq` expression
expected an object; the read-only API call itself succeeded. One corrected
read-only inspection then returned an empty active-run list. No job retry,
redeployment, table/data mutation, negative job, compute creation, Terraform,
or AWS operation occurred.

Lineage acceptance is now PASS. The protected-table and direct-path negative
jobs remain separate approval boundaries.

## References

- [Databricks Unity Catalog data lineage](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-lineage)
- [Databricks lineage system tables](https://docs.databricks.com/aws/en/admin/system-tables/lineage)
