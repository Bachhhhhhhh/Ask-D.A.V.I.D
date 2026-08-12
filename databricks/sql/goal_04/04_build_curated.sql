MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_events') AS target
USING (
  SELECT event_id, entity_id, event_type, event_timestamp, technical_value, revision
  FROM IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events')
  WHERE event_id IS NOT NULL
    AND entity_id IS NOT NULL
    AND event_type IS NOT NULL
    AND technical_value BETWEEN -1000.0D AND 1000.0D
) AS source
ON target.event_id = source.event_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
