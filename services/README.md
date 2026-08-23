# Goal 7 controlled services

The typed implementation lives in the `ask-david-goal7` workspace package.
It exposes only the thin operations needed by the demo:

- `QueryService.query_metric`: generated SELECT-only SQL against the approved
  Doris serving mart, with table allowlist and row limit;
- `RetrievalService.retrieve`: canonical query embedding, model/dimension
  checks, vector search, and role filtering;
- `AnalyticsService.compare_periods`: one allowlisted latest-versus-previous
  calculation through the Databricks adapter;
- `MetadataService.describe`: minimal Unity Catalog-backed metadata lookup.

Adapters are injected through typed protocols. Agents never receive a
database, Databricks, OpenSearch, S3, or AWS credential. The offline harness
uses in-memory adapters; connected adapters remain a separate approval-bound
deployment step.
