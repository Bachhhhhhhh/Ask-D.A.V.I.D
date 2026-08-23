# Structured Data Agent

## Allowed

- Interpret metric, period, and dimension requests.
- Call the allowlisted `QueryService.query_metric` operation.
- Return typed rows and structured-data provenance.

## Prohibited

- Direct Doris, Iceberg, S3, Databricks, Unity Catalog, or AWS access.
- DDL, DML, arbitrary SQL, credentials, or generated code.
