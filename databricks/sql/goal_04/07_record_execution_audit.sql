MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_platform.synthetic_agent_execution_audit') AS target
USING (
  SELECT
    'goal-04-static-run-001' AS execution_id,
    'synthetic-managed-iceberg-pipeline' AS workflow_name,
    'SUCCEEDED' AS execution_state,
    TIMESTAMP'2026-01-02 00:00:00' AS started_timestamp,
    TIMESTAMP'2026-01-02 00:10:00' AS completed_timestamp,
    COUNT(*) AS record_count
  FROM IDENTIFIER(:catalog_name || '.green_sm_business.synthetic_metrics')
) AS source
ON target.execution_id = source.execution_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
