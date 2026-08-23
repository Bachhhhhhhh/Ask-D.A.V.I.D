-- Goal 7 read-only readiness gate for the connected Analytics Agent.
-- The agent does not invoke this job. The deployment operator runs it before
-- an integrated-demo task so a missing governed source period fails before
-- billable ECS execution. No table or source data is mutated here.
SELECT assert_true(
  COUNT_IF(dataset_id = 'goal5.synthetic.events') > 0
    AND COUNT_IF(dataset_id = 'goal6.synthetic.serving.increment') > 0,
  'Goal 7 analytics requires both approved synthetic datasets'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_business.goal5_structured_business_metrics')
WHERE dataset_id IN ('goal5.synthetic.events', 'goal6.synthetic.serving.increment');

SELECT assert_true(
  COUNT(DISTINCT metric_date) >= 2,
  'Goal 7 analytics requires at least two approved synthetic metric periods'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_business.goal5_structured_business_metrics')
WHERE dataset_id IN ('goal5.synthetic.events', 'goal6.synthetic.serving.increment');

SELECT assert_true(
  COUNT_IF(metric_date IS NULL OR category IS NULL OR metric_total IS NULL) = 0,
  'Goal 7 analytics approved source rows must satisfy the metric contract'
)
FROM IDENTIFIER(:catalog_name || '.green_sm_business.goal5_structured_business_metrics')
WHERE dataset_id IN ('goal5.synthetic.events', 'goal6.synthetic.serving.increment');
