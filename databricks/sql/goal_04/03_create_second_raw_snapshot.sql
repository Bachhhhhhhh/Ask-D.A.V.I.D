-- A deterministic second write makes Iceberg history/snapshot verification meaningful.
UPDATE IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events')
SET revision = 2
WHERE event_id = 'event-001' AND revision = 1;
