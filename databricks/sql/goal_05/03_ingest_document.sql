-- goal-05 document metadata: the original object is preserved in approved S3.
SELECT assert_true(
  :document_source_uri RLIKE '^s3://[^/]+/unity-catalog/development/goal5/documents/[^/]+\\.(md|txt)$',
  'document source must be an approved development Goal 5 text URI'
);

CREATE OR REPLACE TEMP VIEW goal5_document_run_context AS
SELECT CONCAT('goal5-document-', REPLACE(CAST(uuid() AS STRING), '-', '')) AS run_id,
  current_timestamp() AS started_at;

WITH source_document AS (
  SELECT
    :document_source_uri AS source_uri,
    value AS content,
    _metadata.file_path AS physical_path
  FROM read_files(
    :document_source_uri,
    format => 'text',
    wholeText => true
  )
), metadata AS (
  SELECT
    'goal5.synthetic.documents' AS dataset_id,
    SHA2(CONCAT('goal5.synthetic.documents:', :document_source_uri), 256) AS document_id,
    SHA2(content, 256) AS document_version,
    element_at(SPLIT(physical_path, '/'), -1) AS filename,
    CASE WHEN LOWER(physical_path) LIKE '%.md' THEN 'text/markdown' ELSE 'text/plain' END AS content_type,
    :document_source_uri AS source_uri,
    'goal5-synthetic-fixture' AS source_system,
    (SELECT run_id FROM goal5_document_run_context) AS ingestion_run_id,
    current_timestamp() AS ingested_at,
    'synthetic_technical' AS classification,
    SHA2(content, 256) AS content_sha256,
    LENGTH(CAST(content AS STRING)) AS content_size_bytes,
    'ACCEPTED' AS validation_status,
    'none' AS validation_reason
  FROM source_document
)
MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_ai.goal5_document_metadata') AS target
USING metadata AS source
ON target.dataset_id = source.dataset_id
 AND target.document_id = source.document_id
 AND target.document_version = source.document_version
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_ingestion_runs') AS target
USING (
  SELECT
    (SELECT run_id FROM goal5_document_run_context) AS run_id,
    'goal5.synthetic.documents' AS dataset_id,
    'document' AS source_type,
    :document_source_uri AS source_uri,
    :document_contract_version AS source_version,
    (SELECT started_at FROM goal5_document_run_context) AS started_at,
    MAX(ingested_at) AS completed_at,
    'SUCCEEDED' AS status,
    COUNT(*) AS input_count,
    COUNT(*) AS accepted_count,
    0 AS rejected_count,
    CAST(NULL AS STRING) AS error_summary
  FROM IDENTIFIER(:catalog_name || '.green_sm_ai.goal5_document_metadata')
  WHERE dataset_id = 'goal5.synthetic.documents'
    AND source_uri = :document_source_uri
) AS source
ON target.run_id = source.run_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_quality_results') AS target
USING (
  SELECT
    (SELECT run_id FROM goal5_document_run_context) AS run_id,
    'goal5.synthetic.documents' AS dataset_id,
    'goal5_document_metadata' AS table_name,
    'required_fields' AS rule_name,
    CASE WHEN COUNT(*) = 1 AND COUNT_IF(document_id IS NULL OR document_version IS NULL OR source_uri IS NULL) = 0
      THEN 'PASS' ELSE 'FAIL' END AS status,
    COUNT_IF(document_id IS NULL OR document_version IS NULL OR source_uri IS NULL) AS observed_value,
    0 AS expected_value,
    'document identity, version, and source URI are required' AS detail,
    current_timestamp() AS checked_at
  FROM IDENTIFIER(:catalog_name || '.green_sm_ai.goal5_document_metadata')
  WHERE dataset_id = 'goal5.synthetic.documents' AND source_uri = :document_source_uri
) AS source
ON target.run_id = source.run_id AND target.dataset_id = source.dataset_id AND target.rule_name = source.rule_name
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
