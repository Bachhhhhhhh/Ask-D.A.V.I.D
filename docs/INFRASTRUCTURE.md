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
an explicit input, with VPC flow logs, an encrypted alert topic without
subscriptions, and one base RDS CPU alarm. The alarm monitors average
`AWS/RDS` `CPUUtilization` for the Terraform-managed DB instance over five
consecutive one-minute datapoints. Its threshold is an explicit environment
input; development uses the owner-approved value `90`.

The alarm's only action is the existing alert topic. Because that topic uses
the customer-managed observability KMS key, the key policy grants
`cloudwatch.amazonaws.com` only `kms:GenerateDataKey*` and `kms:Decrypt`,
restricted to the owning account and exact base-alarm ARN. No alarm state is
forced during validation and no notification subscription is created.

OpenSearch Serverless is optional and limited to a VPC endpoint plus network
and encryption policies. No collection, data policy, index, vector mapping,
document schema, ingestion, or retrieval behavior is included; those remain
Goal 7 work.

## Required development inputs

The following are deliberately unresolved: account ID, AWS profile or workload
identity, region, CIDRs, AZ count, approved internal ingress CIDRs, bucket
prefix, RDS class, Redis node type, NAT strategy, log retention, and deletion
protection. The RDS CPU alarm threshold is also explicit and must be greater
than `0` and no greater than `100`; the reviewed development value is `90`.
The example file suggests a two-AZ, one-NAT development topology with
`db.t4g.micro` and `cache.t4g.micro`; these are not defaults for a real
environment and require cost review.

## Checkpoint 3B only

After written approval for an identified development account, run a reviewed
`terraform apply` from the bootstrap then development root, followed by the
read-only `infrastructure/scripts/smoke.ps1 -ConfirmCheckpoint3B` script. A
subsequent `terraform plan -input=false` must show no unexpected drift. Do not
run these commands as part of Checkpoint 3A.

The read-only smoke script also verifies the exact RDS CPU alarm contract and
SNS action ARN returned by Terraform outputs. It does not call
`SetAlarmState`, publish a message, create a subscription, or prove delivery
to a human endpoint.

### Dynamic private smoke tests

The development root also defines three **Terraform-created, one-off** Fargate
task definitions for the Goal 3B dynamic checks. They do not create an ECS
service, API, LangGraph runtime, agent, tool service, database schema, S3
object, OpenSearch collection, or business data. They are static validation
programs, not agent-generated code, and must never be reused as application
task definitions.

- PostgreSQL: injects only the RDS-managed username/password into a private
  task, requires TLS, and runs the fixed read-only statement `SELECT 1`.
- Redis: runs only a TLS `PING` against the private endpoint.
- S3: uses a distinct task role that can only `ListBucket` on the Raw bucket;
  it proves the Curated bucket call is denied by default with `HeadBucket`.
  It does not list object metadata or read an object body.

All three use reviewed, content-addressed Public ECR upstream digests through
an account-private ECR pull-through-cache namespace, and the existing private
application subnets with `assignPublicIp=DISABLED`. The separate execution role
can retrieve only the RDS-managed secret ARN for injection and can import an
image only into the `ecr-public/*` cache namespace; the task role has no
Secrets Manager permission and no broad S3 permission. The script
`infrastructure/scripts/run-runtime-smoke.ps1` verifies account/region,
validates the family, roles, Fargate mode, one-container shape, and pinned
digest before launching exactly these three task definitions. It waits for zero
exit codes, fixes `assignPublicIp=DISABLED` in the launch request, and verifies
that the durable ECS task attachment reports a private IPv4 address. It does
not query an ENI after task stop because Fargate may already have deleted it.
It deliberately does not retrieve task logs or print secret values.

The smoke tasks use a dedicated security group, never the future workload or
agent group. It permits VPC-resolver DNS, PostgreSQL to the RDS security group,
and Redis TLS to the Redis security group. The corresponding endpoint, RDS,
and Redis ingress rules refer only to this dedicated group.

It also has a temporary TCP/443 egress fallback through the existing NAT
gateway. A connected retry showed Fargate resolving the digest-pinned ECR
pull-through image endpoint publicly even though the ECR PrivateLink endpoint
and private DNS were enabled; the private-endpoint-only rule therefore timed
out before a container could start. Security groups cannot limit this fallback
to an ECR hostname. The exception is documented with a resource-level Trivy
suppression, is limited to the isolated one-off synthetic task group, and does
not give a task a public IP. It must not be reused by a service, agent, or any
future workload; its continued use requires a security review before such use.

Creating these definitions requires a new reviewed connected Terraform plan
and a separate explicit apply approval. Launching the temporary tasks is only
permitted after that apply and the Goal 3B smoke-test checkpoint approval.

Before requesting that approval, run the credential-free `infra-preflight`.
All local environment inputs and backend values must be complete except for
the state KMS ARN, which is intentionally supplied from the approved bootstrap
output before connected development initialization. Bootstrap and development
state use distinct S3 object keys.

## Goal 4 declarative extension

Goal 4 extends the verified development root without redesigning Goal 3. The
safe source defaults are `goal_4_stage = "disabled"` and
`goal_4_storage_role_self_assumption_enabled = false`. The separately reviewed
`bootstrap` stage declares only one Unity Catalog storage credential, its AWS
IAM role and prefix-scoped inline policy, seven zero-byte SSE-KMS S3 root
markers, and the in-place storage KMS key policy. The markers make otherwise
empty approved prefixes addressable to Databricks `PATH_EXISTS` validation;
they contain no data records and are not Iceberg tables. IAM creation is
deliberately two-step: the initial role trust contains
only the Databricks Unity Catalog principal and exact external ID; a later
saved plan adds the role's own ARN in-place after the role exists. The `active`
stage is blocked unless that self-assumption flag is true, changes credential
validation to strict mode, and adds only the approved development identities,
bindings, external locations, catalog, schemas, and least-privilege grants.

All S3 names, ARNs, managed roots, and the KMS key are derived from the Goal 3
Terraform graph. The new role can access only the seven approved logical
managed roots: one catalog root plus the six schema roots. Those roots use the
Raw, Curated, Business, Documents, Audit, and Artifacts buckets; the Logs
bucket is deliberately excluded. List and object permissions are scoped to
the exact `unity-catalog/development/...` roots and the existing storage KMS
key. The role has no Glue, RDS, Redis, ECS, OpenSearch, Secrets Manager,
state-bucket, or non-storage permission. Users and Databricks service
principals receive no direct AWS identity or S3 grant.

The existing metastore and Serverless SQL Warehouse are data references and
checks only. There is no metastore-assignment, warehouse, cluster, or Glue
resource. See `docs/runbooks/GOAL-04-DATABRICKS-LAKEHOUSE.md`; no connected
Goal 4 plan or mutation is authorized by this source implementation.
