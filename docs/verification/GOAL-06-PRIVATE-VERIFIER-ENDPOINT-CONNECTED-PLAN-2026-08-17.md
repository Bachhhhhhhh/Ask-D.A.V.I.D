# Goal 6 Phase 6-6 private verifier endpoint remediation — connected plan

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **REVIEWED — AWAITING EXACT SAVED-PLAN APPLY APPROVAL**

## Reverification

Before planning, read-only checks confirmed:

- AWS account `736956442295`, principal
  `arn:aws:iam::736956442295:user/bach_dev_admin_david`;
- region `ap-southeast-1`;
- active development workspace principal `bachvxuan@gmail.com`;
- account-level Databricks provider refresh succeeded after interactive OAuth
  reauthentication;
- source declares only the reviewed verifier-SG-to-existing-endpoint-SG TCP/443
  rule, with no CIDR ingress.

Terraform used the configured S3 backend with `-lock=false` and a temporary
local data directory. It refreshed remote AWS and Databricks state read-only;
no apply, ECS task, SQL, ECR, or other mutation occurred.

## Saved artifact

| Item | Value |
| --- | --- |
| Artifact | `infrastructure/environments/development/goal-06-private-verifier-endpoint-remediation-20260817-r2.tfplan` |
| SHA-256 | `02d3e4f351eac916fea81a0846537d500a697ff3380c576cf5dc0681049c0031` |
| Git tracking | Ignored by `*.tfplan` |
| Plan actions | `1 to add, 0 to change, 0 to destroy` |
| No-op resources | 256 |

## Exact managed change

```text
CREATE aws_vpc_security_group_ingress_rule.goal6_verifier_to_aws_endpoints[0]
  destination SG: sg-09df4c29eba7991fa (existing private AWS interface endpoints)
  source SG:      sg-04eb1ebf613ceeadc (existing Goal 6 verifier)
  protocol/port:  TCP 443 only
  CIDR:           none
```

The create carries only standard development/synthetic Terraform tags. No
endpoint, route, security-group replacement, IAM/KMS/secret, EC2/EBS, ECS task
definition, ECR, Databricks, production, public-exposure, or Goal 7+ change is
present.

## Required next approval

Only the exact artifact and SHA above may be applied. Before apply, reverify
AWS identity/account/region and artifact hash. Do not create a replacement
plan. The subsequent one-time private ECS verifier health task is a separate
approval boundary.

## Apply outcome

After separate hash-bound approval, Terraform applied this exact artifact as
`1 added, 0 changed, 0 destroyed`. The resulting rule and immediate read-only
inspection are recorded in
[`GOAL-06-PRIVATE-VERIFIER-ENDPOINT-APPLY-2026-08-17.md`](GOAL-06-PRIVATE-VERIFIER-ENDPOINT-APPLY-2026-08-17.md).
