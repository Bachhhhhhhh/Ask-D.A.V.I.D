MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_business.synthetic_metrics') AS target
USING (
  SELECT
    CAST(event_timestamp AS DATE) AS metric_date,
    event_type,
    COUNT(*) AS event_count,
    AVG(technical_value) AS average_technical_value
  FROM IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_events')
  GROUP BY CAST(event_timestamp AS DATE), event_type
) AS source
ON target.metric_date = source.metric_date AND target.event_type = source.event_type
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
