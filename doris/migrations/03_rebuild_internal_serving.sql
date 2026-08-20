-- Goal 6 destructive rebuild procedure. Execute only from the separate,
-- explicitly approved private admin operation after source verification.
-- It drops no Unity Catalog object and no S3 object.
DROP VIEW IF EXISTS ask_david_serving_development.serving_data_freshness;
DROP TABLE IF EXISTS ask_david_serving_development.goal6_authorization_probe;
DROP TABLE IF EXISTS ask_david_serving_development.serving_refresh_state;
DROP TABLE IF EXISTS ask_david_serving_development.serving_metric_daily;
DROP DATABASE IF EXISTS ask_david_serving_development;
