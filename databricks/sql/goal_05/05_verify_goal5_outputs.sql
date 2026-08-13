-- Goal 5 read-only acceptance assertions. Tables API format inspection is external.
SELECT assert_true(
  COUNT(*) = 3,
  'structured Raw must contain three valid source rows'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_raw_events')
WHERE dataset_id = 'goal5.synthetic.events';

SELECT assert_true(
  COUNT(*) = 1 AND COUNT_IF(reason_code = 'INVALID_TYPE') = 1,
  'structured invalid row must be quarantined with a reason'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_quarantine')
WHERE dataset_id = 'goal5.synthetic.events';

SELECT assert_true(
  COUNT(*) = 2 AND COUNT(*) = COUNT(DISTINCT event_id),
  'structured Curated must be deduplicated by event_id'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_structured_curated_events')
WHERE dataset_id = 'goal5.synthetic.events';

SELECT assert_true(
  COUNT(*) >= 1 AND SUM(event_count) = 2,
  'generic Business aggregation must reconcile to Curated'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_business.goal5_structured_business_metrics')
WHERE dataset_id = 'goal5.synthetic.events';

SELECT assert_true(
  COUNT(*) = 1 AND COUNT_IF(content_type IN ('text/plain', 'text/markdown')) = 1
    AND COUNT_IF(source_uri = :document_source_uri) = 1,
  'document metadata and original source provenance must exist'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_ai.goal5_document_metadata')
WHERE dataset_id = 'goal5.synthetic.documents'
  AND source_uri = :document_source_uri;

SELECT assert_true(
  COUNT(*) = 1 AND COUNT_IF(validation_status = 'ACCEPTED' AND validation_reason = 'none') = 1,
  'document validation status and reason must be recorded'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_ai.goal5_document_metadata')
WHERE dataset_id = 'goal5.synthetic.documents';

SELECT assert_true(
  COUNT(*) = 4 AND MAX(duplicate_occurrence_count) = 2,
  'CDC raw history must preserve four unique events and duplicate occurrence count'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_cdc_history')
WHERE dataset_id = 'goal5.synthetic.entity_changes';

SELECT assert_true(
  COUNT(*) = 4 AND COUNT_IF(validation_status = 'ACCEPTED' AND validation_reason = 'none') = 4,
  'CDC validation status and reason must be recorded for unique history'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_cdc_history')
WHERE dataset_id = 'goal5.synthetic.entity_changes';

SELECT assert_true(
  SUM(CASE
    WHEN entity_id = 'entity-001'
      AND is_deleted = false
      AND TRY_CAST(get_json_object(payload_json, '$.metric_value') AS DOUBLE) = CAST(120 AS DOUBLE)
    THEN 1 ELSE 0
  END) = 1
    AND SUM(CASE WHEN entity_id = 'entity-002' AND is_deleted = true THEN 1 ELSE 0 END) = 1,
  'CDC current state must reflect UPDATE and DELETE tombstone semantics'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_cdc_current_state')
WHERE dataset_id = 'goal5.synthetic.entity_changes';

SELECT assert_true(
  COUNT(*) >= 3 AND COUNT_IF(status <> 'SUCCEEDED') = 0,
  'all three Goal 5 ingestion runs must be auditable and successful'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_ingestion_runs')
WHERE dataset_id IN ('goal5.synthetic.events', 'goal5.synthetic.documents', 'goal5.synthetic.entity_changes');

SELECT assert_true(
  COUNT(*) > 0 AND COUNT_IF(status = 'FAIL') = 0
    AND COUNT(DISTINCT dataset_id) = 3,
  'Goal 5 quality and validation results must be queryable and passing for all paths'
)
FROM (
  SELECT dataset_id, status
  FROM IDENTIFIER(:catalog_name || '.green_sm_platform.goal5_quality_results')
  WHERE dataset_id IN (
    'goal5.synthetic.events',
    'goal5.synthetic.documents',
    'goal5.synthetic.entity_changes'
  )
  UNION ALL
  SELECT dataset_id, validation_status AS status
  FROM IDENTIFIER(:catalog_name || '.green_sm_ai.goal5_document_metadata')
  WHERE dataset_id = 'goal5.synthetic.documents'
  UNION ALL
  SELECT dataset_id, validation_status AS status
  FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_cdc_history')
  WHERE dataset_id = 'goal5.synthetic.entity_changes'
);
