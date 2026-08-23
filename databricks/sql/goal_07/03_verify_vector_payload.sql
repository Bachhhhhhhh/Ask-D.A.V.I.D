-- Goal 7 read-only payload contract before the controlled OpenSearch upsert.
SELECT assert_true(
  COUNT(*) > 0,
  'Goal 7 must produce at least one synthetic embedded document chunk'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_ai.goal7_document_chunks');

SELECT assert_true(
  COUNT(*) = 0,
  'Goal 7 chunks must use one canonical embedding model and dimension'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_ai.goal7_document_chunks')
WHERE embedding_model_id <> :embedding_model_id
   OR SIZE(embedding) <> CAST(:embedding_dimension AS INT);

SELECT assert_true(
  COUNT(*) = 0,
  'Goal 7 chunks must retain source URI, document identity, and an ACL role'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_ai.goal7_document_chunks')
WHERE chunk_id IS NULL
   OR document_id IS NULL
   OR source_uri IS NULL
   OR SIZE(allowed_roles) = 0;
