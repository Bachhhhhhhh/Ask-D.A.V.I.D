# Goal 7 S3 gateway-prefix-list egress apply — 2026-08-21

## Status

**APPLIED — READ-ONLY POST-APPLY INSPECTION PASSED — INDEXER NOT RETRIED**

The explicitly approved saved plan was hash-checked and applied exactly. No
other Terraform plan, AWS/Databricks mutation, ECR/AOSS operation, or ECS task
launch occurred.

## Apply evidence

- AWS account: `736956442295`
- AWS region: `ap-southeast-1`
- principal: `arn:aws:iam::736956442295:user/bach_dev_admin_david`
- saved plan SHA-256:
  `f48b163af53daf82693ad206e1071ddf34988ccb26be05ff0f183eeeb7dc541d`
- Terraform result: `1 added, 0 changed, 0 destroyed`
- created rule: `sgr-02d4f83f0f3d19c6e`

## Read-only post-apply inspection

| Check | Result |
| --- | --- |
| Rule source SG | PASS — workload `sg-0a22126b47d3a5aea` |
| Rule destination | PASS — S3 prefix list `pl-6fa54006` |
| Protocol/ports | PASS — TCP/443 |
| CIDR scope | PASS — IPv4/IPv6 fields null |
| S3 gateway route | PASS — active route via `vpce-02706a3f82c187138` |
| Prefix-list identity | PASS — AWS `com.amazonaws.ap-southeast-1.s3`, `create-complete` |
| ECS running tasks | PASS — empty list; no retry launched |

The rule is distinct from the previously applied interface-endpoint SG rule;
both paths remain narrowly scoped and Terraform-managed.

## Next approval boundary

The next action is a separate approval for exactly one private indexer task
using the existing digest-pinned task definition. It must use the reviewed
private subnets/workload SG, must not redeploy or retry implicitly, and must
stop on any failure. Goal 7 remains unverified until the indexer succeeds and
the subsequent AOSS/index, demo, authorization, and end-to-end checks pass.
