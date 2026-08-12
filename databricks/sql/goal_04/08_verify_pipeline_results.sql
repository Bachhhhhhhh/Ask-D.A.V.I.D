SELECT assert_true(COUNT(*) = 3, 'Raw synthetic record count must be three')
FROM IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events');

SELECT assert_true(COUNT(*) = 3, 'Curated synthetic record count must be three')
FROM IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_events');

SELECT assert_true(COUNT(*) = 3, 'Business synthetic metric count must be three')
FROM IDENTIFIER(:catalog_name || '.green_sm_business.synthetic_metrics');

SELECT assert_true(
  COUNT(*) = 10
    AND COUNT_IF(check_state <> 'PASS') = 0
    AND COUNT_IF(
      check_name = 'managed_iceberg_test_table_count'
      AND observed_value = 7.0D
      AND expected_value = 7.0D
      AND check_state = 'PASS'
    ) = 1,
  'Exactly ten quality checks, including the seven-table managed Iceberg check, must pass'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_platform.synthetic_data_quality_results')
WHERE validation_run_id = 'goal-04-static-run-001';
