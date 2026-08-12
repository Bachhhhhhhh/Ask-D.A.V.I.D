-- Expected evidence: Unity Catalog rejects this managed-storage path with LOCATION_OVERLAP.
-- This structural rejection counts only with clean UC/IAM/KMS/S3 policy inspection proving
-- that the denied principal has no storage privilege, AWS identity, or direct bucket/key grant.
-- The URL is supplied from Terraform output at deployment time; it is never hard-coded here.
SELECT *
FROM IDENTIFIER('iceberg.`' || :denied_s3_probe_url || '`')
LIMIT 1;
