-- Expected evidence: this task fails with the principal-specific Unity Catalog error
-- INSUFFICIENT_PERMISSIONS (SQLSTATE 42501) after the workspace file is loaded.
SELECT *
FROM IDENTIFIER(:catalog_name || '.green_sm_business.synthetic_metrics')
LIMIT 1;
