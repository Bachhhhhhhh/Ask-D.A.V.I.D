# Goal 6 Phase 6-10 — disposable serving-copy rebuild

Date: 2026-08-20
Environment: development
AWS account: `736956442295`
AWS region: `ap-southeast-1`

## Approval and execution boundary

The user explicitly approved exactly one private Phase 6-10 rebuild task after
the offline wrapper/precondition review. The reviewed task definition was
`ask-david-development-doris-admin-refresh:16` with the immutable audit-guard
image digest already recorded in the Phase 6-14 evidence. The task ran in the
approved private application subnets with admin security group
`sg-07a0dd2e8af8aa178` and `assignPublicIp=DISABLED`.

No Terraform plan/apply/destroy, EC2/EBS operation, ECR operation, Databricks
operation, Unity Catalog mutation, S3/source write, or retry was performed.

## Connected result

The guarded `rebuild` operation invoked only the version-controlled
`/app/doris-rebuild-serving` command, which executes
`doris/migrations/03_rebuild_internal_serving.sql`. That migration targets only
the disposable `ask_david_serving_development` Doris database objects and does
not reference the authoritative Unity Catalog/S3 source.

| Field | Result |
| --- | --- |
| ECS task | `2551e7c4b51949b695bb23b0ee3dd1c5` |
| Task definition | `ask-david-development-doris-admin-refresh:16` |
| Status / exit code | `STOPPED` / `0` |
| Private subnet / ENI address | `subnet-0a1aad220d82ef879` / `10.42.40.192` |
| CloudWatch stream | `admin/doris-admin/2551e7c4b51949b695bb23b0ee3dd1c5` |
| Completion marker | `{"goal":"goal-06","operation":"rebuild-serving","status":"completed"}` |
| Retry | None |

## Acceptance result

Phase 6-10 rebuild execution is **PASS** for the disposable Doris serving
copy. The result equivalence requirement is intentionally not claimed yet:
the separately approved post-rebuild admin refresh must recreate/reload the
copy from the authoritative lakehouse source, followed by a separately
approved read-only verifier comparison. A new final Phase 6-14 zero-drift
check is required after those operations.
