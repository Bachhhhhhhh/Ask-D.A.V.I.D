-- Goal 6 source fixture: neutral synthetic data flows only through governed
-- Goal 5 Raw -> Curated -> Business tables; no Doris SQL or external storage.
SELECT assert_true(
  :increment_source_uri RLIKE '^s3://[^/]+/unity-catalog/development/goal5/structured/goal6_increment\.csv$',
  'Goal 6 increment must use its approved synthetic Goal 5 source prefix'
);

CREATE OR REPLACE TEMP VIEW goal6_increment_source AS
SELECT
  event_id,
  entity_id,
  CAST(event_time AS TIMESTAMP) AS event_time,
  category,
  CAST(metric_value AS DOUBLE) AS metric_value
FROM read_files(
  :increment_source_uri,
  format => 'csv',
  header => true,
  schema => 'event_id STRING, entity_id STRING, event_time STRING, category STRING, metric_value STRING'
);

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_raw_events') AS target
USING (
  SELECT
    'goal6.synthetic.serving.increment' AS dataset_id,
    :increment_source_uri AS source_uri,
    1 AS source_row_number,
    SHA2(CONCAT_WS('|', event_id, entity_id, CAST(event_time AS STRING), category, CAST(metric_value AS STRING)), 256) AS record_hash,
    event_id, entity_id, event_time, category, metric_value,
    CONCAT('goal6-', REPLACE(CAST(uuid() AS STRING), '-', '')) AS ingestion_run_id,
    'ACCEPTED' AS validation_status,
    'none' AS validation_reason,
    current_timestamp() AS ingested_at
  FROM goal6_increment_source
) AS source
ON target.dataset_id = source.dataset_id AND target.record_hash = source.record_hash
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_structured_curated_events') AS target
USING (
  SELECT
    dataset_id, event_id, entity_id, event_time, category, metric_value,
    source_uri, source_row_number, record_hash, ingestion_run_id,
    'PASS' AS quality_status, current_timestamp() AS curated_at
  FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_raw_events')
  WHERE dataset_id = 'goal6.synthetic.serving.increment'
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
    'goal6-serving-increment-v1' AS transformation_version,
    MAX(ingestion_run_id) AS ingestion_run_id,
    current_timestamp() AS transformed_at
  FROM IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_structured_curated_events')
  WHERE dataset_id = 'goal6.synthetic.serving.increment'
  GROUP BY dataset_id, CAST(event_time AS DATE), category
) AS source
ON target.dataset_id = source.dataset_id AND target.metric_date = source.metric_date AND target.category = source.category
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
