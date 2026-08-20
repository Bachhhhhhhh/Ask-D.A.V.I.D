-- A serving-only view. It is not a source-of-truth table or source mutation.
CREATE VIEW IF NOT EXISTS ask_david_serving_development.serving_data_freshness AS
SELECT
  source_table,
  MAX(source_transformed_at) AS source_transformed_at,
  MAX(refreshed_at) AS refreshed_at,
  TIMESTAMPDIFF(SECOND, MAX(source_transformed_at), MAX(refreshed_at)) AS refresh_lag_seconds
FROM ask_david_serving_development.serving_metric_daily
GROUP BY source_table;
