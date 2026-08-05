# Goal 3 infrastructure foundation

The Terraform code models a single **development** environment only. It does
not create anything until an explicitly approved Checkpoint 3B apply.

The network has one egress-only public subnet for NAT, private application
subnets for an internal ALB and future ECS workloads, and private data subnets
for RDS and Redis. Gateway/interface endpoints reduce public egress for S3,
ECR, CloudWatch Logs, and Secrets Manager. Security groups allow ALB-to-
workload, workload-to-PostgreSQL, and workload-to-Redis flows only.

S3 has purpose buckets for raw, curated, business, documents, artifacts,
audit, and logs. All use KMS server-side encryption, versioning, ownership
enforcement, public-access blocking, and a TLS-only policy. Names are derived
from environment inputs rather than hard-coded globally fixed names.

RDS and Redis have no public endpoint. RDS creates an AWS-managed master
secret; Terraform never declares a secret value. Future ECS workloads use task
execution and workload IAM roles, not static keys. CloudWatch log retention is
an explicit input, with VPC flow logs, alert topic, and a base RDS CPU alarm.

OpenSearch Serverless is optional and limited to a VPC endpoint plus network
and encryption policies. No collection, data policy, index, vector mapping,
document schema, ingestion, or retrieval behavior is included; those remain
Goal 7 work.

## Required development inputs

The following are deliberately unresolved: account ID, AWS profile or workload
identity, region, CIDRs, AZ count, approved internal ingress CIDRs, bucket
prefix, RDS class, Redis node type, NAT strategy, log retention, and deletion
protection. The example file suggests a two-AZ, one-NAT development topology
with `db.t4g.micro` and `cache.t4g.micro`; these are not defaults for a real
environment and require cost review.

## Checkpoint 3B only

After written approval for an identified development account, run a reviewed
`terraform apply` from the bootstrap then development root, followed by the
read-only `infrastructure/scripts/smoke.ps1 -ConfirmCheckpoint3B` script. A
subsequent `terraform plan -input=false` must show no unexpected drift. Do not
run these commands as part of Checkpoint 3A.

Before requesting that approval, run the credential-free `infra-preflight`.
All local environment inputs and backend values must be complete except for
the state KMS ARN, which is intentionally supplied from the approved bootstrap
output before connected development initialization. Bootstrap and development
state use distinct S3 object keys.
