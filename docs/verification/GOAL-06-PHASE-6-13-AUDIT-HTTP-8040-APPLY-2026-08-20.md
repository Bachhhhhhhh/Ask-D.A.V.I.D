# Goal 6 Phase 6-13 AuditLoader HTTP/8040 — connected apply

Date: `2026-08-20`

Status: **APPLIED — AUDIT EXECUTION STILL PENDING**

## Approved scope

- AWS account: `736956442295`
- Region: `ap-southeast-1`
- Saved plan: `goal-06-audit-http-8040-20260820-r2.tfplan`
- Saved plan SHA-256: `2af16e7950852755d85e23fcdda5009673d7e39dddd0db5903a52d855bdbe661`
- Identity revalidation: `arn:aws:iam::736956442295:user/bach_dev_admin_david`

The plan contained exactly two creates, with zero updates, replacements, or
destroys. It was applied without an implicit replacement plan or task retry.

## Apply result

| Resource | Result | AWS rule ID |
| --- | --- | --- |
| FE egress → BE TCP/8040 | CREATED | `sgr-063740e24430c93e4` |
| BE ingress ← FE TCP/8040 | CREATED | `sgr-0b2283c8685f946b5` |

Terraform reported: `2 added, 0 changed, 0 destroyed`.

## Read-only post-apply inspection

Both rules are TCP/8040 SG-to-SG rules between the existing Doris groups:

- FE SG `sg-019b900ee5601c208` egress references BE SG
  `sg-0a21b2270f7fcd689`;
- BE SG `sg-0a21b2270f7fcd689` ingress references FE SG
  `sg-019b900ee5601c208`;
- both have `CidrIpv4 = null` and preserve the existing description
  `Documented Doris FE-to-BE membership traffic.`.

No EC2, EBS, IAM, KMS, ECS, Databricks, public, or production resource was
changed. No ECS task, SQL retry, or audit execution was run in this step.

## Checkpoint

The network prerequisite for the AuditLoader HTTP redirect is now applied.
Phase 6-13 remains **UNVERIFIED** until a separately approved, exactly
one-shot audit execution produces the required query-ID row evidence.
