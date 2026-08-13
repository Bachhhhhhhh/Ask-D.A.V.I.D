-- goal-05 idempotency assertions after repeating the exact source versions.
SELECT assert_true(
  COUNT(*) = COUNT(DISTINCT CONCAT(dataset_id, '|', source_uri, '|', source_row_number)),
  'structured source idempotency key must remain unique'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_raw_events')
WHERE dataset_id = 'goal5.synthetic.events';

SELECT assert_true(
  COUNT(*) = COUNT(DISTINCT CONCAT(dataset_id, '|', document_id, '|', document_version)),
  'document version must not duplicate on repeat'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_ai.goal5_document_metadata')
WHERE dataset_id = 'goal5.synthetic.documents';

SELECT assert_true(
  COUNT(*) = COUNT(DISTINCT CONCAT(dataset_id, '|', event_id)),
  'CDC event ID must be applied at most once'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_cdc_history')
WHERE dataset_id = 'goal5.synthetic.entity_changes';

SELECT assert_true(
  COUNT(*) >= 6,
  'a repeat must create auditable runs for all three source patterns'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_ingestion_runs')
WHERE dataset_id IN ('goal5.synthetic.events', 'goal5.synthetic.documents', 'goal5.synthetic.entity_changes');
