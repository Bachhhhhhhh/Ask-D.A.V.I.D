MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_platform.synthetic_data_quality_results') AS target
USING (
  SELECT
    'goal-04-static-run-001' AS validation_run_id,
    'raw_event_count' AS check_name,
    CASE WHEN COUNT(*) = 3 THEN 'PASS' ELSE 'FAIL' END AS check_state,
    CAST(COUNT(*) AS DOUBLE) AS observed_value,
    3.0D AS expected_value,
    TIMESTAMP'2026-01-02 00:10:00' AS checked_timestamp
  FROM IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events')
  UNION ALL
  SELECT
    'goal-04-static-run-001',
    'curated_event_count',
    CASE WHEN COUNT(*) = 3 THEN 'PASS' ELSE 'FAIL' END,
    CAST(COUNT(*) AS DOUBLE),
    3.0D,
    TIMESTAMP'2026-01-02 00:10:00'
  FROM IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_events')
  UNION ALL
  SELECT
    'goal-04-static-run-001',
    'business_metric_count',
    CASE WHEN COUNT(*) = 3 THEN 'PASS' ELSE 'FAIL' END,
    CAST(COUNT(*) AS DOUBLE),
    3.0D,
    TIMESTAMP'2026-01-02 00:10:00'
  FROM IDENTIFIER(:catalog_name || '.green_sm_business.synthetic_metrics')
  UNION ALL
  SELECT
    'goal-04-static-run-001',
    'raw_required_fields_null_count',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    CAST(COUNT(*) AS DOUBLE),
    0.0D,
    TIMESTAMP'2026-01-02 00:10:00'
  FROM IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events')
  WHERE event_id IS NULL OR entity_id IS NULL OR event_type IS NULL OR event_timestamp IS NULL
  UNION ALL
  SELECT
    'goal-04-static-run-001',
    'duplicate_event_id_count',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    CAST(COUNT(*) AS DOUBLE),
    0.0D,
    TIMESTAMP'2026-01-02 00:10:00'
  FROM (
    SELECT event_id
    FROM IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events')
    GROUP BY event_id
    HAVING COUNT(*) > 1
  )
  UNION ALL
  SELECT
    'goal-04-static-run-001',
    'duplicate_entity_id_count',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    CAST(COUNT(*) AS DOUBLE),
    0.0D,
    TIMESTAMP'2026-01-02 00:10:00'
  FROM (
    SELECT entity_id
    FROM IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_entities')
    GROUP BY entity_id
    HAVING COUNT(*) > 1
  )
  UNION ALL
  SELECT
    'goal-04-static-run-001',
    'invalid_entity_state_count',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    CAST(COUNT(*) AS DOUBLE),
    0.0D,
    TIMESTAMP'2026-01-02 00:10:00'
  FROM IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_entities')
  WHERE entity_state NOT IN ('ACTIVE', 'INACTIVE')
  UNION ALL
  SELECT
    'goal-04-static-run-001',
    'curated_rejection_count',
    CASE WHEN raw_count - curated_count = 0 THEN 'PASS' ELSE 'FAIL' END,
    CAST(raw_count - curated_count AS DOUBLE),
    0.0D,
    TIMESTAMP'2026-01-02 00:10:00'
  FROM (
    SELECT
      (SELECT COUNT(*) FROM IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events')) AS raw_count,
      (SELECT COUNT(*) FROM IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_events')) AS curated_count
  )
  UNION ALL
  SELECT
    'goal-04-static-run-001',
    'business_reconciliation_difference',
    CASE WHEN business_count - curated_count = 0 THEN 'PASS' ELSE 'FAIL' END,
    CAST(business_count - curated_count AS DOUBLE),
    0.0D,
    TIMESTAMP'2026-01-02 00:10:00'
  FROM (
    SELECT
      (SELECT SUM(event_count) FROM IDENTIFIER(:catalog_name || '.green_sm_business.synthetic_metrics')) AS business_count,
      (SELECT COUNT(*) FROM IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_events')) AS curated_count
  )
  UNION ALL
  SELECT
    'goal-04-static-run-001',
    'managed_iceberg_test_table_count',
    CASE WHEN COUNT(*) = 7 THEN 'PASS' ELSE 'FAIL' END,
    CAST(COUNT(*) AS DOUBLE),
    7.0D,
    TIMESTAMP'2026-01-02 00:10:00'
  FROM IDENTIFIER(:catalog_name || '.information_schema.tables')
  WHERE table_schema IN (
    'green_sm_raw',
    'green_sm_curated',
    'green_sm_business',
    'green_sm_ai',
    'green_sm_platform'
  )
    AND table_name LIKE 'synthetic_%'
    AND table_type = 'MANAGED'
    AND data_source_format = 'ICEBERG'
) AS source
ON target.validation_run_id = source.validation_run_id AND target.check_name = source.check_name
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

SELECT assert_true(
  COUNT(*) = 10 AND COUNT_IF(check_state <> 'PASS') = 0,
  'Goal 4 deterministic data-quality checks failed'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_platform.synthetic_data_quality_results')
WHERE validation_run_id = 'goal-04-static-run-001';
