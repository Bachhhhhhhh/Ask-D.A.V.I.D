WITH goal4_lineage AS (
  SELECT source_table_full_name, target_table_full_name
  FROM system.access.table_lineage
  WHERE source_table_catalog = :catalog_name
    AND target_table_catalog = :catalog_name
)
SELECT
  assert_true(
    COUNT_IF(
      source_table_full_name = :catalog_name || '.green_sm_raw.synthetic_events'
      AND target_table_full_name = :catalog_name || '.green_sm_curated.synthetic_events'
    ) > 0,
    'Unity Catalog lineage must contain the Raw to Curated synthetic-events edge'
  ) AS raw_to_curated_lineage_present,
  assert_true(
    COUNT_IF(
      source_table_full_name = :catalog_name || '.green_sm_curated.synthetic_events'
      AND target_table_full_name = :catalog_name || '.green_sm_business.synthetic_metrics'
    ) > 0,
    'Unity Catalog lineage must contain the Curated to Business synthetic-metrics edge'
  ) AS curated_to_business_lineage_present
FROM goal4_lineage;
