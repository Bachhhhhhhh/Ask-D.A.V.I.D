-- Goal 4 only: neutral synthetic structures. All tables are Unity Catalog managed
-- Apache Iceberg tables. Deliberately omit LOCATION to prevent unmanaged tables.
CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events') (
  event_id STRING NOT NULL,
  entity_id STRING NOT NULL,
  event_type STRING NOT NULL,
  event_timestamp TIMESTAMP NOT NULL,
  technical_value DOUBLE NOT NULL,
  revision INT NOT NULL,
  source_system STRING NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-04'
);

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_events') (
  event_id STRING NOT NULL,
  entity_id STRING NOT NULL,
  event_type STRING NOT NULL,
  event_timestamp TIMESTAMP NOT NULL,
  technical_value DOUBLE NOT NULL,
  revision INT NOT NULL
)
USING ICEBERG
TBLPROPERTIES ('data_classification' = 'synthetic-only', 'goal' = 'goal-04');

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_entities') (
  entity_id STRING NOT NULL,
  entity_label STRING NOT NULL,
  entity_state STRING NOT NULL,
  effective_timestamp TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES ('data_classification' = 'synthetic-only', 'goal' = 'goal-04');

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_business.synthetic_metrics') (
  metric_date DATE NOT NULL,
  event_type STRING NOT NULL,
  event_count BIGINT NOT NULL,
  average_technical_value DOUBLE NOT NULL
)
USING ICEBERG
TBLPROPERTIES ('data_classification' = 'synthetic-only', 'goal' = 'goal-04');

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_ai.synthetic_document_metadata') (
  document_id STRING NOT NULL,
  document_title STRING NOT NULL,
  media_type STRING NOT NULL,
  content_checksum STRING NOT NULL,
  created_timestamp TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES ('data_classification' = 'synthetic-only', 'goal' = 'goal-04');

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_platform.synthetic_agent_execution_audit') (
  execution_id STRING NOT NULL,
  workflow_name STRING NOT NULL,
  execution_state STRING NOT NULL,
  started_timestamp TIMESTAMP NOT NULL,
  completed_timestamp TIMESTAMP NOT NULL,
  record_count BIGINT NOT NULL
)
USING ICEBERG
TBLPROPERTIES ('data_classification' = 'synthetic-only', 'goal' = 'goal-04');

CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_platform.synthetic_data_quality_results') (
  validation_run_id STRING NOT NULL,
  check_name STRING NOT NULL,
  check_state STRING NOT NULL,
  observed_value DOUBLE NOT NULL,
  expected_value DOUBLE NOT NULL,
  checked_timestamp TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES ('data_classification' = 'synthetic-only', 'goal' = 'goal-04');
