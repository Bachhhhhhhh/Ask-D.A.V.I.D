# Goal 7 Databricks network-path read-only revalidation — 2026-08-21

## Status

**READ-ONLY REVALIDATION COMPLETE — PRIVATE PATH NOT AVAILABLE; NO MUTATION**

This checkpoint used only Databricks CLI discovery, AWS STS/EC2 read-only
inspection, and DNS resolution. No Terraform plan/apply/destroy, AWS mutation,
Databricks mutation, ECS task, ECR operation, SQL run, or AOSS operation was
performed.

## Identity and workspace

| Check | Result |
| --- | --- |
| AWS account | PASS — `736956442295` |
| AWS region | PASS — `ap-southeast-1` |
| Databricks account | PASS — `e7e97bc6-a872-4312-9a43-c0eb305b1b2e` |
| Workspace | PASS — `7474644358733471`, `dbc-7f3363e3-d129.cloud.databricks.com` |
| Workspace status | PASS — `RUNNING` |
| Workspace pricing tier | PASS — `PREMIUM` |
| Workspace AWS region | PASS — `ap-southeast-1` |
| Current principal | PASS — `bachvxuan@gmail.com` with workspace access and SQL access |
| Unity Catalog assignment | PASS — metastore `3a7f7e7a-680b-4bd6-907a-6d5e77b43178` |
| Existing SQL warehouse | PASS — `757e0335c6efb51e`, Small, Serverless, `RUNNING`, healthy |

The named workspace and account OAuth profiles were used without printing any
token or secret. `databricks current-user me`, account workspace listing,
metastore listing, and metastore-assignment inspection succeeded. The CLI
profile summary itself reported `Valid: NO`, but the authenticated read-only
API calls above succeeded; this is recorded as a CLI validity-display
inconsistency, not treated as a credential value.

## Databricks private-connectivity result

| Inspection | Result |
| --- | --- |
| Account VPC endpoint configurations | UNAVAILABLE — API reports the account must have `ENTERPRISE` pricing |
| Account private-access settings | UNAVAILABLE — API reports the account must have `ENTERPRISE` pricing |
| Account customer-managed network configurations | PASS — list is empty |
| Workspace endpoint configuration | UNVERIFIED/NOT AVAILABLE through the Premium account API |
| Existing AWS VPC endpoint for Databricks | FAIL — none found in the project VPC |

The account-level `vpc-endpoints list` and `private-access list` calls were
read-only and returned the explicit `ENTERPRISE` pricing requirement. The
workspace is Premium, so the approved Databricks PrivateLink/private-access
path cannot be enabled or verified within the current account capability. The
AWS VPC contains only the existing AOSS endpoint, ECR API/DKR, Logs,
Secrets Manager, and S3 gateway endpoints; no Databricks endpoint service or
Databricks private DNS entry is present.

The configured workspace hostname resolves to public AWS load-balancer
addresses (`13.214.1.106` and `13.214.1.108` at inspection time). These
addresses are observational only and must not be converted into a static
security-group allowlist.

## AWS private task path

| Resource | Read-only result |
| --- | --- |
| VPC | `vpc-007ba758b98a9ab9e`, `10.42.0.0/16`, DNS support/hostnames enabled |
| Private route table | `rtb-0c590f3acb40e43d7` associated with both indexer application subnets |
| Default route | `0.0.0.0/0` → existing NAT `nat-089ff95a2bbde917f` |
| S3 route | Prefix list `pl-6fa54006` → existing S3 gateway endpoint |
| NAT | `available`, public connectivity type, public EIP `13.213.128.175` |
| Workload SG | `sg-0a22126b47d3a5aea` |
| Workload egress | TCP/443 only to endpoint SG `sg-09df4c29eba7991fa` and S3 prefix list `pl-6fa54006`; no CIDR egress |
| Endpoint SG ingress | TCP/443 from the workload SG is present |

Therefore the route table can send public Databricks traffic toward NAT, but
the workload SG intentionally has no matching egress rule. This exactly
explains the OAuth timeout observed in the revision-2 indexer task. It does not
indicate an OAuth secret, Unity Catalog grant, AOSS policy, or image failure.

## Decision and next approval boundary

The preferred private Databricks path is not available in the current Premium
workspace/account and no existing endpoint can be reused. Do not add
`0.0.0.0/0:443` egress, a static IP allowlist, static credentials, or a new
proxy/firewall as an implicit fix.

Goal 7 is stopped and remains **NOT VERIFIED**. Continuing requires an explicit
architecture/security decision and separate approval for one of these choices:

1. upgrade/configure an approved Databricks Enterprise private-connectivity
   architecture; or
2. explicitly approve a narrowly documented NAT HTTPS egress boundary, with
   its cost and security impact, before any Terraform source change.

No source implementation, connected Terraform plan, apply, or ECS retry is
authorized by this revalidation.
