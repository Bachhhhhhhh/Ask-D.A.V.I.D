# Goal 6 Phase 6-6 private verifier endpoint remediation — apply

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **APPLIED — PRIVATE VERIFIER HEALTH CHECK STILL REQUIRES SEPARATE APPROVAL**

## Approval and revalidation

The project owner approved applying only saved plan SHA-256
`02d3e4f351eac916fea81a0846537d500a697ff3380c576cf5dc0681049c0031`.
Immediately before apply, read-only checks reconfirmed:

- AWS account `736956442295` and approved region `ap-southeast-1`;
- active development workspace principal `bachvxuan@gmail.com`;
- exact artifact hash;
- plan JSON with one create only: the verifier-to-endpoint TCP/443 SG rule;
- no update, replacement, destroy, CIDR/public exposure, IAM/KMS, task
  definition, ECS, Databricks, or production change.

## Result

Terraform applied the exact saved plan successfully:

```text
Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

The created security-group rule is `sgr-0e3ed4747a11d3b1d`.

## Immediate read-only verification

AWS EC2 security-group-rule inspection confirms:

| Attribute | Verified value |
| --- | --- |
| Direction | Ingress |
| Destination SG | `sg-09df4c29eba7991fa` — existing private AWS interface endpoints |
| Referenced source SG | `sg-04eb1ebf613ceeadc` — existing Goal 6 verifier |
| Protocol / port | TCP `443` to `443` |
| IPv4 CIDR | none |
| IPv6 CIDR | none |
| Description | Goal 6 read-only verifier access to existing private AWS interface endpoints only |
| Ownership tags | Terraform-managed, development, synthetic-only |

No ECS task, SQL, ECR, Databricks, or further Terraform operation ran during
or after this apply.

## Next boundary

The previously approved verifier task stopped before container start and cannot
be treated as a health result. The endpoint path has now been repaired, but
Phase 6-6 remains unverified until exactly one separately approved bounded
private Fargate verifier task performs the non-mutating MariaDB health ping to
FE `10.42.64.238:9030` and exits `0`. No retry is implicitly authorized.
