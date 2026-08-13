-- goal-05 structured CSV: invalid rows are quarantined before trusted writes.
SELECT assert_true(
  :structured_source_uri RLIKE '^s3://[^/]+/unity-catalog/development/goal5/structured/[^/]+\\.csv$',
  'structured source must be an approved development Goal 5 CSV URI'
);

CREATE OR REPLACE TEMP VIEW goal5_structured_run_context AS
SELECT CONCAT('goal5-structured-', REPLACE(CAST(uuid() AS STRING), '-', '')) AS run_id,
  current_timestamp() AS started_at;

CREATE OR REPLACE TEMP VIEW goal5_structured_source_rows AS
SELECT
  ROW_NUMBER() OVER (
    ORDER BY event_id, entity_id, event_time, category, metric_value, COALESCE(_rescued, '')
  ) AS source_row_number,
  event_id,
  entity_id,
  TRY_CAST(event_time AS TIMESTAMP) AS event_time,
  category,
  TRY_CAST(metric_value AS DOUBLE) AS metric_value,
  _rescued,
  TO_JSON(named_struct(
    'event_id', event_id,
    'entity_id', entity_id,
    'event_time', event_time,
    'category', category,
    'metric_value', metric_value,
    '_rescued', _rescued
  )) AS raw_record
FROM read_files(
  :structured_source_uri,
  format => 'csv',
  header => true,
  mode => 'PERMISSIVE',
  rescuedDataColumn => '_rescued',
  schema => 'event_id STRING, entity_id STRING, event_time STRING, category STRING, metric_value STRING'
);

CREATE OR REPLACE TEMP VIEW goal5_structured_valid_rows AS
SELECT * FROM goal5_structured_source_rows
WHERE _rescued IS NULL
  AND event_id IS NOT NULL AND entity_id IS NOT NULL
  AND event_time IS NOT NULL AND category IS NOT NULL AND metric_value IS NOT NULL;

CREATE OR REPLACE TEMP VIEW goal5_structured_invalid_rows AS
SELECT * FROM goal5_structured_source_rows
WHERE _rescued IS NOT NULL
   OR event_id IS NULL OR entity_id IS NULL
   OR event_time IS NULL OR category IS NULL OR metric_value IS NULL;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_ingestion_runs') AS target
USING (
  SELECT
    context.run_id,
    'goal5.synthetic.events' AS dataset_id,
    'structured_file' AS source_type,
    :structured_source_uri AS source_uri,
    :structured_contract_version AS source_version,
    context.started_at,
    current_timestamp() AS completed_at,
    'SUCCEEDED' AS status,
    (SELECT COUNT(*) FROM goal5_structured_source_rows) AS input_count,
    (SELECT COUNT(*) FROM goal5_structured_valid_rows) AS accepted_count,
    (SELECT COUNT(*) FROM goal5_structured_invalid_rows) AS rejected_count,
    CAST(NULL AS STRING) AS error_summary
  FROM goal5_structured_run_context AS context
) AS source
ON target.run_id = source.run_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_raw_events') AS target
USING (
  SELECT
    'goal5.synthetic.events' AS dataset_id,
    :structured_source_uri AS source_uri,
    source_row_number,
    SHA2(CONCAT_WS('|', event_id, entity_id, CAST(event_time AS STRING), category, CAST(metric_value AS STRING)), 256) AS record_hash,
    event_id,
    entity_id,
    event_time,
    category,
    metric_value,
    (SELECT run_id FROM goal5_structured_run_context) AS ingestion_run_id,
    'ACCEPTED' AS validation_status,
    'none' AS validation_reason,
    current_timestamp() AS ingested_at
  FROM goal5_structured_valid_rows
) AS source
ON target.dataset_id = source.dataset_id
 AND target.source_uri = source.source_uri
 AND target.source_row_number = source.source_row_number
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_quarantine') AS target
USING (
  SELECT
    'goal5.synthetic.events' AS dataset_id,
    :structured_source_uri AS source_uri,
    source_row_number,
    raw_record,
    'INVALID_TYPE' AS reason_code,
    CASE WHEN _rescued IS NOT NULL THEN 'schema/type mismatch captured by rescued data' ELSE 'required field or type is invalid' END AS reason,
    (SELECT run_id FROM goal5_structured_run_context) AS ingestion_run_id,
    current_timestamp() AS quarantined_at
  FROM goal5_structured_invalid_rows
) AS source
ON target.dataset_id = source.dataset_id
 AND target.source_uri = source.source_uri
 AND target.source_row_number = source.source_row_number
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_structured_curated_events') AS target
USING (
  SELECT dataset_id, event_id, entity_id, event_time, category, metric_value,
    source_uri, source_row_number, record_hash, ingestion_run_id,
    'PASS' AS quality_status, current_timestamp() AS curated_at
  FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY source_row_number DESC, record_hash DESC) AS selected
    FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_raw_events')
    WHERE dataset_id = 'goal5.synthetic.events'
  )
  WHERE selected = 1
) AS source
ON target.dataset_id = source.dataset_id AND target.event_id = source.event_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_business.goal5_structured_business_metrics') AS target
USING (
  SELECT
    dataset_id,
    CAST(event_time AS DATE) AS metric_date,
    category,
    COUNT(*) AS event_count,
    SUM(metric_value) AS metric_total,
    'goal5-generic-category-day-v1' AS transformation_version,
    MAX(ingestion_run_id) AS ingestion_run_id,
    current_timestamp() AS transformed_at
  FROM IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_structured_curated_events')
  WHERE dataset_id = 'goal5.synthetic.events'
  GROUP BY dataset_id, CAST(event_time AS DATE), category
) AS source
ON target.dataset_id = source.dataset_id
 AND target.metric_date = source.metric_date
 AND target.category = source.category
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_quality_results') AS target
USING (
  SELECT
    (SELECT run_id FROM goal5_structured_run_context) AS run_id,
    'goal5.synthetic.events' AS dataset_id,
    'goal5_structured_curated_events' AS table_name,
    'required_fields' AS rule_name,
    CASE WHEN COUNT_IF(event_id IS NULL OR entity_id IS NULL OR event_time IS NULL) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    COUNT_IF(event_id IS NULL OR entity_id IS NULL OR event_time IS NULL) AS observed_value,
    0 AS expected_value,
    'required fields must be non-null' AS detail,
    current_timestamp() AS checked_at
  FROM IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_structured_curated_events')
  WHERE dataset_id = 'goal5.synthetic.events'
  UNION ALL
  SELECT
    (SELECT run_id FROM goal5_structured_run_context),
    'goal5.synthetic.events', 'goal5_structured_curated_events', 'uniqueness',
    CASE WHEN COUNT(*) = COUNT(DISTINCT event_id) THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*) - COUNT(DISTINCT event_id), 0, 'event_id must be unique after curation', current_timestamp()
  FROM IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_structured_curated_events')
  WHERE dataset_id = 'goal5.synthetic.events'
) AS source
ON target.run_id = source.run_id AND target.dataset_id = source.dataset_id AND target.rule_name = source.rule_name
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
