-- Goal 5: create only neutral, governed, managed tables. No LOCATION is used.
CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_ingestion_runs') (
  run_id STRING NOT NULL,
  dataset_id STRING NOT NULL,
  source_type STRING NOT NULL,
  source_uri STRING NOT NULL,
  source_version STRING NOT NULL,
  started_at TIMESTAMP NOT NULL,
  completed_at TIMESTAMP,
  status STRING NOT NULL,
  input_count BIGINT NOT NULL,
  accepted_count BIGINT NOT NULL,
  rejected_count BIGINT NOT NULL,
  error_summary STRING
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-05',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_quality_results') (
  run_id STRING NOT NULL,
  dataset_id STRING NOT NULL,
  table_name STRING NOT NULL,
  rule_name STRING NOT NULL,
  status STRING NOT NULL,
  observed_value BIGINT NOT NULL,
  expected_value BIGINT NOT NULL,
  detail STRING NOT NULL,
  checked_at TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-05',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_raw_events') (
  dataset_id STRING NOT NULL,
  source_uri STRING NOT NULL,
  source_row_number BIGINT NOT NULL,
  record_hash STRING NOT NULL,
  event_id STRING NOT NULL,
  entity_id STRING NOT NULL,
  event_time TIMESTAMP NOT NULL,
  category STRING NOT NULL,
  metric_value DOUBLE NOT NULL,
  ingestion_run_id STRING NOT NULL,
  validation_status STRING NOT NULL,
  validation_reason STRING NOT NULL,
  ingested_at TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-05',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_quarantine') (
  dataset_id STRING NOT NULL,
  source_uri STRING NOT NULL,
  source_row_number BIGINT NOT NULL,
  raw_record STRING NOT NULL,
  reason_code STRING NOT NULL,
  reason STRING NOT NULL,
  ingestion_run_id STRING NOT NULL,
  quarantined_at TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-05',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_structured_curated_events') (
  dataset_id STRING NOT NULL,
  event_id STRING NOT NULL,
  entity_id STRING NOT NULL,
  event_time TIMESTAMP NOT NULL,
  category STRING NOT NULL,
  metric_value DOUBLE NOT NULL,
  source_uri STRING NOT NULL,
  source_row_number BIGINT NOT NULL,
  record_hash STRING NOT NULL,
  ingestion_run_id STRING NOT NULL,
  quality_status STRING NOT NULL,
  curated_at TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-05',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_business.goal5_structured_business_metrics') (
  dataset_id STRING NOT NULL,
  metric_date DATE NOT NULL,
  category STRING NOT NULL,
  event_count BIGINT NOT NULL,
  metric_total DOUBLE NOT NULL,
  transformation_version STRING NOT NULL,
  ingestion_run_id STRING NOT NULL,
  transformed_at TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-05',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_ai.goal5_document_metadata') (
  dataset_id STRING NOT NULL,
  document_id STRING NOT NULL,
  document_version STRING NOT NULL,
  filename STRING NOT NULL,
  content_type STRING NOT NULL,
  source_uri STRING NOT NULL,
  source_system STRING NOT NULL,
  ingestion_run_id STRING NOT NULL,
  ingested_at TIMESTAMP NOT NULL,
  classification STRING NOT NULL,
  content_sha256 STRING NOT NULL,
  content_size_bytes BIGINT NOT NULL,
  validation_status STRING NOT NULL,
  validation_reason STRING NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-05',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_cdc_history') (
  dataset_id STRING NOT NULL,
  event_id STRING NOT NULL,
  entity_id STRING NOT NULL,
  operation STRING NOT NULL,
  event_time TIMESTAMP NOT NULL,
  sequence BIGINT NOT NULL,
  source STRING NOT NULL,
  payload_json STRING,
  duplicate_occurrence_count BIGINT NOT NULL,
  ingestion_run_id STRING NOT NULL,
  source_hash STRING NOT NULL,
  validation_status STRING NOT NULL,
  validation_reason STRING NOT NULL,
  recorded_at TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-05',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_cdc_current_state') (
  dataset_id STRING NOT NULL,
  entity_id STRING NOT NULL,
  operation_applied STRING NOT NULL,
  event_id STRING NOT NULL,
  event_time TIMESTAMP NOT NULL,
  sequence BIGINT NOT NULL,
  payload_json STRING,
  is_deleted BOOLEAN NOT NULL,
  source STRING NOT NULL,
  ingestion_run_id STRING NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-05',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

SELECT assert_true(
  COUNT(*) = 9 AND COUNT_IF(table_type = 'MANAGED') = 9,
  'Goal 5 requires exactly nine managed tables before ingestion'
)
FROM IDENTIFIER(:catalog_name || '.information_schema.tables')
WHERE table_schema IN ('green_sm_raw', 'green_sm_curated', 'green_sm_business', 'green_sm_ai', 'green_sm_platform')
  AND table_name LIKE 'goal5_%';
