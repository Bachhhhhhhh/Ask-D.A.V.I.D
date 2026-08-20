-- Goal 6: internal, disposable serving objects only; no Unity Catalog mutation.
CREATE DATABASE IF NOT EXISTS ask_david_serving_development;

CREATE TABLE IF NOT EXISTS ask_david_serving_development.serving_metric_daily (
  metric_date DATE NOT NULL,
  category VARCHAR(128) NOT NULL,
  event_count BIGINT NOT NULL,
  metric_total DOUBLE NOT NULL,
  source_table VARCHAR(256) NOT NULL,
  source_transformed_at DATETIME NOT NULL,
  refreshed_at DATETIME NOT NULL
)
UNIQUE KEY(metric_date, category)
DISTRIBUTED BY HASH(category) BUCKETS 1
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS ask_david_serving_development.serving_refresh_state (
  refresh_name VARCHAR(128) NOT NULL,
  source_table VARCHAR(256) NOT NULL,
  source_watermark DATETIME,
  refreshed_at DATETIME NOT NULL,
  status VARCHAR(32) NOT NULL,
  row_count BIGINT NOT NULL,
  detail VARCHAR(1024) NOT NULL
)
UNIQUE KEY(refresh_name)
DISTRIBUTED BY HASH(refresh_name) BUCKETS 1
PROPERTIES ("replication_num" = "1");

-- Disposable authorization target. Negative RBAC tests use this isolated
-- object so an unexpected privilege can never mutate a serving result or an
-- authoritative lakehouse object.
CREATE TABLE IF NOT EXISTS ask_david_serving_development.goal6_authorization_probe (
  probe_id SMALLINT NOT NULL,
  marker VARCHAR(64) NOT NULL
)
UNIQUE KEY(probe_id)
DISTRIBUTED BY HASH(probe_id) BUCKETS 1
PROPERTIES ("replication_num" = "1");

-- The disposable probe is recreated and seeded by the versioned
-- 04_recreate_authorization_probe migration after the base schema is applied.
