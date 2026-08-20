-- Goal 6 read-only proof that the source fixture reached Raw, Curated, Business.
SELECT assert_true(
  COUNT(*) = 1,
  'Goal 6 synthetic increment must reach Raw exactly once'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_raw.goal5_structured_raw_events')
WHERE dataset_id = 'goal6.synthetic.serving.increment';

SELECT assert_true(
  COUNT(*) = 1 AND COUNT_IF(quality_status = 'PASS') = 1,
  'Goal 6 synthetic increment must reach Curated with a passing quality status'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_curated.goal5_structured_curated_events')
WHERE dataset_id = 'goal6.synthetic.serving.increment';

SELECT assert_true(
  COUNT(*) = 1 AND SUM(metric_total) = CAST(42 AS DOUBLE),
  'Goal 6 synthetic increment must reach Business with its deterministic aggregate'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_business.goal5_structured_business_metrics')
WHERE dataset_id = 'goal6.synthetic.serving.increment';
