MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_raw.synthetic_events') AS target
USING (
  SELECT * FROM VALUES
    ('event-001', 'entity-001', 'temperature', TIMESTAMP'2026-01-01 00:00:00', 21.5D, 1, 'goal-04-generator'),
    ('event-002', 'entity-001', 'pressure',    TIMESTAMP'2026-01-01 00:05:00',  1.2D, 1, 'goal-04-generator'),
    ('event-003', 'entity-002', 'temperature', TIMESTAMP'2026-01-02 00:00:00', 19.0D, 1, 'goal-04-generator')
  AS source(event_id, entity_id, event_type, event_timestamp, technical_value, revision, source_system)
) AS source
ON target.event_id = source.event_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_curated.synthetic_entities') AS target
USING (
  SELECT * FROM VALUES
    ('entity-001', 'Synthetic Entity 001', 'ACTIVE', TIMESTAMP'2026-01-01 00:00:00'),
    ('entity-002', 'Synthetic Entity 002', 'ACTIVE', TIMESTAMP'2026-01-01 00:00:00')
  AS source(entity_id, entity_label, entity_state, effective_timestamp)
) AS source
ON target.entity_id = source.entity_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO IDENTIFIER(:catalog_name || '.green_sm_ai.synthetic_document_metadata') AS target
USING (
  SELECT * FROM VALUES
    ('document-001', 'Neutral Synthetic Document', 'text/plain', 'sha256:synthetic-001', TIMESTAMP'2026-01-01 00:00:00')
  AS source(document_id, document_title, media_type, content_checksum, created_timestamp)
) AS source
ON target.document_id = source.document_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
