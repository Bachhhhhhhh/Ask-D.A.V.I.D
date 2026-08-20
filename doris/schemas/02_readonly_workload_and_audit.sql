-- Goal 6 operational guardrails for the internal, disposable serving copy.
-- The admin runner binds the generated query user to this group; this file
-- has no Unity Catalog, S3, or source-of-truth mutation.
CREATE WORKLOAD GROUP IF NOT EXISTS goal6_readonly
PROPERTIES (
  "max_cpu_percent" = "25%",
  "max_memory_percent" = "25%",
  "max_concurrency" = "2",
  "max_queue_size" = "2",
  "queue_timeout" = "5000"
);

-- Doris writes the resulting audit records to __internal_schema.audit_log.
SET GLOBAL enable_audit_plugin = true;
