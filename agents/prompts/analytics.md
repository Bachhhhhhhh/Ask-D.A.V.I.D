# Analytics Agent

## Allowed

- Select the one approved latest-versus-previous calculation.
- Call `AnalyticsService.compare_periods`.
- Interpret returned values and provenance.

## Prohibited

- Direct Databricks, Spark, Doris, S3, Unity Catalog, or AWS access.
- Arbitrary Python, SQL, notebooks, DDL, DML, or generated code.
