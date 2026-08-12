-- Defense in depth before any synthetic data mutation. Final acceptance also requires
-- the fail-closed raw Tables API inventory verifier because SQL and API metadata
-- disagreed during the 2026-08-11 final inventory.
SELECT assert_true(
  COUNT(*) = 7
    AND COUNT_IF(table_type <> 'MANAGED') = 0
    AND COUNT_IF(data_source_format <> 'ICEBERG') = 0,
  'Exactly seven native Unity Catalog managed Iceberg tables must exist before data writes'
)
FROM IDENTIFIER(:catalog_name || '.information_schema.tables')
WHERE
  (table_schema = 'green_sm_raw' AND table_name = 'synthetic_events')
  OR (table_schema = 'green_sm_curated' AND table_name = 'synthetic_events')
  OR (table_schema = 'green_sm_curated' AND table_name = 'synthetic_entities')
  OR (table_schema = 'green_sm_business' AND table_name = 'synthetic_metrics')
  OR (table_schema = 'green_sm_ai' AND table_name = 'synthetic_document_metadata')
  OR (
    table_schema = 'green_sm_platform'
    AND table_name = 'synthetic_agent_execution_audit'
  )
  OR (
    table_schema = 'green_sm_platform'
    AND table_name = 'synthetic_data_quality_results'
  );
