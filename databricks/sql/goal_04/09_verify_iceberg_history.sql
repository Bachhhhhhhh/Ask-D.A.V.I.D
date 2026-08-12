USE CATALOG IDENTIFIER(:catalog_name);

DESCRIBE DETAIL green_sm_raw.synthetic_events;
DESCRIBE DETAIL green_sm_curated.synthetic_events;
DESCRIBE DETAIL green_sm_curated.synthetic_entities;
DESCRIBE DETAIL green_sm_business.synthetic_metrics;
DESCRIBE DETAIL green_sm_ai.synthetic_document_metadata;
DESCRIBE DETAIL green_sm_platform.synthetic_agent_execution_audit;
DESCRIBE DETAIL green_sm_platform.synthetic_data_quality_results;
DESCRIBE HISTORY green_sm_raw.synthetic_events;

-- The first MERGE creates version 1 and the later UPDATE creates version 2.
-- Reading version 1 proves that a prior managed-Iceberg snapshot remains usable.
SELECT assert_true(
  COUNT(*) = 3 AND MAX(CASE WHEN event_id = 'event-001' THEN revision END) = 1,
  'Managed Iceberg version 1 must preserve the first Raw write'
)
FROM green_sm_raw.synthetic_events VERSION AS OF 1;
