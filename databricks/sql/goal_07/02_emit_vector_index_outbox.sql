-- Goal 7: controlled handoff from Databricks to the indexing service.
-- This does not call OpenSearch or expose credentials from an agent.  The
-- separately controlled indexing service reads this governed outbox and
-- performs deterministic upserts into the one approved AOSS vector index.
CREATE TABLE IF NOT EXISTS IDENTIFIER(:catalog_name || '.green_sm_ai.goal7_vector_index_outbox') (
  chunk_id STRING NOT NULL,
  document_id STRING NOT NULL,
  title STRING NOT NULL,
  content STRING NOT NULL,
  source_uri STRING NOT NULL,
  allowed_roles ARRAY<STRING> NOT NULL,
  embedding_model_id STRING NOT NULL,
  embedding ARRAY<FLOAT> NOT NULL,
  target_collection STRING NOT NULL,
  target_index STRING NOT NULL,
  emitted_at TIMESTAMP NOT NULL
)
USING ICEBERG
TBLPROPERTIES (
  'data_classification' = 'synthetic-only',
  'goal' = 'goal-07',
  'table_format_policy' = 'iceberg-or-delta-uniform-iceberg'
);

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_ai.goal7_vector_index_outbox') AS target
USING (
  SELECT
    chunk_id,
    document_id,
    title,
    content,
    source_uri,
    allowed_roles,
    embedding_model_id,
    embedding,
    :collection_name AS target_collection,
    :index_name AS target_index,
    current_timestamp() AS emitted_at
  FROM IDENTIFIER(:catalog_name || '.green_sm_ai.goal7_document_chunks')
  WHERE embedding_model_id = :embedding_model_id
    AND SIZE(embedding) = CAST(:embedding_dimension AS INT)
) AS source
ON target.chunk_id = source.chunk_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
