# Goal 7 workload endpoint egress apply — 2026-08-21

## Status

**APPLIED — READ-ONLY POST-APPLY INSPECTION PASSED — INDEXER NOT RETRIED**

The explicitly approved saved plan was applied after rechecking its SHA-256,
AWS account, and region. No other Terraform plan, AWS mutation, Databricks
operation, AOSS index mutation, or ECS task launch occurred.

## Approval and apply evidence

- AWS account: `736956442295`
- AWS region: `ap-southeast-1`
- principal: `arn:aws:iam::736956442295:user/bach_dev_admin_david`
- saved plan SHA-256:
  `80fa254bb6a62f8c23f257651c92ad935a8fba008e33697427198fc670c018e6`
- Terraform result: `1 added, 0 changed, 0 destroyed`
- created rule: `sgr-0c5b69beec0bb6fc7`

The applied plan was the exact reviewed artifact; no implicit replacement plan
was generated.

## Read-only post-apply inspection

| Check | Result |
| --- | --- |
| New rule source SG | PASS — workload `sg-0a22126b47d3a5aea` |
| New rule destination SG | PASS — AWS endpoints `sg-09df4c29eba7991fa` |
| New rule protocol/ports | PASS — TCP/443 |
| New rule CIDR scope | PASS — IPv4/IPv6 CIDR fields are null |
| Existing endpoint ingress | PASS — `sgr-0a6582981c3911ad6`, endpoint SG ← workload SG, TCP/443 |
| ECS running tasks after apply | PASS — empty list; no task launched |
| Goal 6/AOSS/Databricks/public/production mutation | PASS — none in apply |

The endpoint-side rule's source was verified through
`ReferencedGroupInfo.GroupId`, not by assuming a flattened CLI field.

## Remaining boundary

The workload-to-Secrets-Manager network path is now declaratively present, but
the indexer task has not been retried. A separate approval is required to run
exactly one private indexer task with the previously reviewed task definition;
that retry must stop on any failure and must not implicitly redeploy or retry.
