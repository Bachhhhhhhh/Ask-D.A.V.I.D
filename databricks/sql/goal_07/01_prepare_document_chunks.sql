-- Goal 7: normalize and deterministically chunk the approved synthetic Goal 5
-- Markdown document, then call the canonical Databricks embedding model.
-- The table is a governed managed table; it is not an unmanaged LOCATION.
CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_ai.goal7_document_chunks') (
  chunk_id STRING NOT NULL,
  document_id STRING NOT NULL,
  title STRING NOT NULL,
  content STRING NOT NULL,
  source_uri STRING NOT NULL,
  allowed_roles ARRAY<STRING> NOT NULL,
  embedding_model_id STRING NOT NULL,
  embedding ARRAY<FLOAT> NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-07',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

WITH source_document AS (
  SELECT
    :document_source_uri AS source_uri,
    value AS raw_content,
    _metadata.file_path AS physical_path
  FROM read_files(
    :document_source_uri,
    format => 'text',
    wholeText => true
  )
), normalized AS (
  SELECT
    SHA2(CONCAT('goal5.synthetic.documents:', source_uri), 256) AS document_id,
    element_at(SPLIT(physical_path, '/'), -1) AS title,
    source_uri,
    REGEXP_REPLACE(TRIM(raw_content), '\\r?\\n\\s*\\r?\\n+', '\\n\\n') AS normalized_content
  FROM source_document
), chunks AS (
  SELECT
    document_id,
    title,
    source_uri,
    pos AS ordinal,
    TRIM(chunk_content) AS content
  FROM normalized
  LATERAL VIEW POSEXPLODE(SPLIT(normalized_content, '\\n\\n+')) exploded AS pos, chunk_content
  WHERE TRIM(chunk_content) <> ''
), embedded AS (
  SELECT
    SHA2(CONCAT(document_id, ':', CAST(ordinal AS STRING), ':', content), 256) AS chunk_id,
    document_id,
    title,
    content,
    source_uri,
    ARRAY('business-reader') AS allowed_roles,
    :embedding_model_id AS embedding_model_id,
    CAST(ai_query(:embedding_model_id, content) AS ARRAY<FLOAT>) AS embedding
  FROM chunks
)
MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_ai.goal7_document_chunks') AS target
USING embedded AS source
ON target.chunk_id = source.chunk_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
