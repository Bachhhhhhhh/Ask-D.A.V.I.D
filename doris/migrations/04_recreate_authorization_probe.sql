-- Goal 6 disposable authorization probe remediation.
--
-- The previous probe used signed TINYINT and could not store upper sentinel
-- 128. This object is intentionally disposable: each controlled admin refresh
-- recreates only this internal probe, never a lakehouse/source object.
DROP TABLE IF EXISTS ask_david_serving_development.goal6_authorization_probe;

CREATE TABLE ask_david_serving_development.goal6_authorization_probe (
  probe_id SMALLINT NOT NULL,
  marker VARCHAR(64) NOT NULL
)
UNIQUE KEY(probe_id)
DISTRIBUTED BY HASH(probe_id) BUCKETS 1
PROPERTIES ("replication_num" = "1");

-- Keep the disposable probe partition non-empty for the query-only DELETE
-- authorization test. The absent target is 127, between these two fixed
-- neutral sentinels. The target remains absent if DELETE is unexpectedly
-- allowed, so the probe still fails closed with zero affected rows.
INSERT INTO ask_david_serving_development.goal6_authorization_probe
VALUES
  (126, 'goal6_guard_lower'),
  (128, 'goal6_guard_upper');
