-- goal-05 CDC: raw history keeps unique events and duplicate occurrence counts.
SELECT assert_true(
  :cdc_source_uri RLIKE '^s3://[^/]+/unity-catalog/development/goal5/cdc/[^/]+\\.jsonl$',
  'CDC source must be an approved development Goal 5 JSONL URI'
);

CREATE OR REPLACE TEMP VIEW goal5_cdc_run_context AS
SELECT CONCAT('goal5-cdc-', REPLACE(CAST(uuid() AS STRING), '-', '')) AS run_id,
  current_timestamp() AS started_at;

CREATE OR REPLACE TEMP VIEW goal5_cdc_unique_events AS
WITH source_events AS (
  SELECT
    event_id,
    entity_id,
    UPPER(operation) AS operation,
    CAST(event_time AS TIMESTAMP) AS event_time,
    CAST(sequence AS BIGINT) AS sequence,
    source,
    TO_JSON(payload) AS payload_json,
    SHA2(TO_JSON(named_struct('event_id', event_id, 'entity_id', entity_id, 'operation', operation, 'event_time', event_time, 'sequence', sequence, 'source', source, 'payload', payload)), 256) AS source_hash
  FROM read_files(
    :cdc_source_uri,
    format => 'json',
    schema => 'event_id STRING, entity_id STRING, operation STRING, event_time STRING, sequence BIGINT, source STRING, payload STRUCT<metric_value:DOUBLE>'
  )
), grouped_events AS (
  SELECT *, COUNT(*) OVER (PARTITION BY event_id) AS duplicate_occurrence_count,
    ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY sequence, event_time, source_hash) AS selected
  FROM source_events
), unique_events AS (
  SELECT * FROM grouped_events WHERE selected = 1
)
SELECT * FROM unique_events;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_cdc_history') AS target
USING (
  SELECT
    'goal5.synthetic.entity_changes' AS dataset_id,
    event_id, entity_id, operation, event_time, sequence, source, payload_json,
    duplicate_occurrence_count,
    (SELECT run_id FROM goal5_cdc_run_context) AS ingestion_run_id,
    source_hash,
    'ACCEPTED' AS validation_status,
    'none' AS validation_reason,
    current_timestamp() AS recorded_at
  FROM goal5_cdc_unique_events
) AS source
ON target.dataset_id = source.dataset_id AND target.event_id = source.event_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_cdc_current_state') AS target
USING (
  SELECT dataset_id, entity_id, operation AS operation_applied, event_id, event_time, sequence,
    CASE WHEN operation = 'DELETE' THEN NULL ELSE payload_json END AS payload_json,
    operation = 'DELETE' AS is_deleted, source,
    (SELECT run_id FROM goal5_cdc_run_context) AS ingestion_run_id,
    current_timestamp() AS updated_at
  FROM (
    SELECT
      'goal5.synthetic.entity_changes' AS dataset_id,
      entity_id, operation, event_id, event_time, sequence, payload_json, source,
      ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY event_time DESC, sequence DESC, event_id DESC) AS latest
    FROM goal5_cdc_unique_events
  )
  WHERE latest = 1
) AS source
ON target.dataset_id = source.dataset_id AND target.entity_id = source.entity_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_ingestion_runs') AS target
USING (
  SELECT
    (SELECT run_id FROM goal5_cdc_run_context) AS run_id,
    'goal5.synthetic.entity_changes' AS dataset_id,
    'cdc' AS source_type,
    :cdc_source_uri AS source_uri,
    :cdc_contract_version AS source_version,
    current_timestamp() AS started_at,
    current_timestamp() AS completed_at,
    'SUCCEEDED' AS status,
    COUNT(*) AS input_count,
    COUNT(*) AS accepted_count,
    0 AS rejected_count,
    CAST(NULL AS STRING) AS error_summary
  FROM goal5_cdc_unique_events
) AS source
ON target.run_id = source.run_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_quality_results') AS target
USING (
  SELECT
    (SELECT run_id FROM goal5_cdc_run_context) AS run_id,
    'goal5.synthetic.entity_changes' AS dataset_id,
    'goal5_cdc_history' AS table_name,
    'required_fields' AS rule_name,
    CASE WHEN COUNT(*) = 4 AND COUNT_IF(event_id IS NULL OR entity_id IS NULL OR operation IS NULL) = 0
      THEN 'PASS' ELSE 'FAIL' END AS status,
    COUNT_IF(event_id IS NULL OR entity_id IS NULL OR operation IS NULL) AS observed_value,
    0 AS expected_value,
    'CDC identity and operation fields are required' AS detail,
    current_timestamp() AS checked_at
  FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_cdc_history')
  WHERE dataset_id = 'goal5.synthetic.entity_changes'
) AS source
ON target.run_id = source.run_id AND target.dataset_id = source.dataset_id AND target.rule_name = source.rule_name
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
