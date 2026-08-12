# Goal 4 history SQL parse remediation

## Scope and boundary

This report records the failed one-shot history verification and the approved
offline-only SQL remediation. It does not authorize connected bundle
validation/deployment, another job/SQL run, table/data mutation, Terraform, or
AWS operation.

## Failed run evidence

- Job ID: `695423086105630`.
- Run ID: `952431524488579`.
- Trigger: `ONE_TIME`.
- Run state: `INTERNAL_ERROR / FAILED`.
- Task: `inspect_managed_iceberg_history`.
- Task state: `TERMINATED / FAILED`.
- Attempt number: `0`.
- Active runs after failure: none.

The SQL parser stopped on the first statement, before any table detail,
history, or time-travel result was produced:

```text
[PARSE_SYNTAX_ERROR] Syntax error at or near '||'
DESCRIBE DETAIL IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events')
```

The warehouse remained `RUNNING` only inside its configured 10-minute
auto-stop window. No retry, redeployment, lineage/negative job, table mutation,
Terraform, or AWS operation followed.

## Root cause and declarative remediation

Databricks documents the `IDENTIFIER` clause for both `USE CATALOG` and the
target of a `DESCRIBE` statement. The deployed SQL passed a concatenated
expression through the `DESCRIBE DETAIL` parser, which the current Serverless
SQL environment rejected.

The approved minimal remediation changes only
`09_verify_iceberg_history.sql`:

1. select the Terraform-derived approved catalog with
   `USE CATALOG IDENTIFIER(:catalog_name)`;
2. use static schema-qualified names for all seven `DESCRIBE DETAIL`
   statements, Raw `DESCRIBE HISTORY`, and the Raw version-1 read;
3. preserve read-only semantics and the existing time-travel assertion.

The deterministic validator now rejects loss of the parameterized catalog
context, concatenated `IDENTIFIER` expressions in `DESCRIBE`/`FROM`, missing
table-detail statements, missing Raw history, or missing Raw version-1 read.
Two mutation tests cover the catalog-context and parse-failure regressions.

## Offline verification

Completed on `2026-08-11` without a connected command or cloud operation:

| Gate | Result |
| --- | --- |
| Goal 4 deterministic static validator | PASS |
| History SQL regression tests | PASS — 16 Goal 4 tests total |
| Full offline pytest suite | PASS — 34 tests |
| Branch coverage | PASS — 96.67%, threshold 90% |
| Bundle/resource YAML parsing | PASS |
| Ruff format and lint | PASS — 67 files |
| Strict mypy | PASS — 5 source files |
| Bandit | PASS |
| detect-secrets over remediation files | PASS |
| ADR, tracked-artifact, merge-marker, and `git diff --check` hygiene | PASS |

`pip-audit` was not rerun because this gate was explicitly offline and the
remediation changes no dependency or lock file.

## Strict connected validation

Exactly one separately approved strict connected validation ran against
aggregate source SHA-256
`9714d971417979d131d23f051519f10cb83392b9aa7927a33af4d68840691c4e`
and history SQL SHA-256
`7b521c1f5d4a24d55a0c6658a87c7d0703b35994ee58bc98f01e1062cdfa3927`.
It used target `development`, profile `ask-david-development`, the reviewed
Terraform-derived variables, and no `workspace_host` variable. Databricks CLI
`1.11.0` exited `0` with `Validation OK!`, no warning, and no recommendation.
No deployment or job/SQL run occurred.

## Next approval boundaries

Strict validation is complete. Separately approve redeployment of aggregate
source SHA-256
`9714d971417979d131d23f051519f10cb83392b9aa7927a33af4d68840691c4e`.
Only the synchronized history SQL content is expected to change; the five job
identities and other 11 SQL files must remain unchanged, and no job may run.
Only after redeployment and read-only inspection may a separately approved
one-shot history retry occur.

## Redeployment and read-only inspection

The separately approved redeployment of aggregate source SHA-256
`9714d971417979d131d23f051519f10cb83392b9aa7927a33af4d68840691c4e`
completed with exit `0` and `Deployment complete!`. Bundle summary and direct
job inspection confirmed that all five job IDs, names, and task counts remained
unchanged.

The first file-export inspection requested `RAW` through JSON output. Workspace
API rejected that combination because direct download was false; the resulting
empty-stream hash is invalid and is not evidence. The corrected read-only
inspection exported the deployed file with `AUTO --file` into `/tmp` and
produced SHA-256
`7b521c1f5d4a24d55a0c6658a87c7d0703b35994ee58bc98f01e1062cdfa3927`,
exactly matching the reviewed local history SQL. Its inspected content begins
with `USE CATALOG IDENTIFIER(:catalog_name)` and contains static names for all
approved read-only statements.

No job/SQL run, compute creation, Terraform operation, or AWS mutation occurred
during redeployment or inspection.

## History retry approval boundary

The remediated history source is deployed. Separately approve exactly one retry
of job `695423086105630`, source-set SHA-256
`cfe6d0f047dd9a42e0550f51b9acd1352b17182e8d061184c68610c469631572`.
It may perform only the deployed read-only `DESCRIBE DETAIL`, `DESCRIBE HISTORY`,
and version-1 assertion. Stop without retry on any failure.

## Successful history retry

The separately approved remediated history retry ran exactly once:

- job ID: `695423086105630`;
- run ID: `966938583513350`;
- trigger: `ONE_TIME`;
- task attempt: `0`;
- final state: `TERMINATED / SUCCESS`;
- active runs after completion: none.

Pre-run warehouse inspection showed the approved Small Serverless SQL warehouse
`STOPPED`. The successful task selected the approved catalog, executed all
seven `DESCRIBE DETAIL` statements, executed Raw `DESCRIBE HISTORY`, and passed
the version-1 assertion requiring three Raw records and revision `1` for
`event-001`. Immediate post-run inspection showed the warehouse `RUNNING`
inside its 10-minute auto-stop window.

This provides connected evidence that the seven tables are inspectable and a
prior managed-Iceberg snapshot remains readable. No implicit retry,
redeployment, table mutation, lineage/negative job, new compute, Terraform, or
AWS operation occurred.

## References

- [Databricks `IDENTIFIER` clause](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names-identifier-clause)
- [Databricks `DESCRIBE TABLE` and `DESCRIBE DETAIL`](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-table)
