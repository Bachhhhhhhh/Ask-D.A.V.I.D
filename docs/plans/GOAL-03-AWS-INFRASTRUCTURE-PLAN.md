# Goal 3 — AWS Infrastructure Foundation

## Status and scope

This is the approved implementation plan for Goal 3. It establishes a secure,
reproducible AWS development infrastructure foundation using Terraform.

It does not implement an API, LangGraph runtime, agents, controlled tool
services, Databricks, Unity Catalog, Doris, OpenSearch indexes, retrieval,
documents, embeddings, or Green SM data. Accepted ADRs remain unchanged.

Goal 2 is complete. The existing `infrastructure/` directory contains only a
placeholder README; there is no Terraform, AWS configuration, state, or
credential material in the repository.

## Approved development decisions

- The Application Load Balancer is internal only. No ECS task or ALB is
  internet-facing.
- Private application subnets use one NAT Gateway in development. The strategy
  remains configurable so a later, separately approved environment can use one
  NAT Gateway per Availability Zone.
- OpenSearch Serverless is limited to an optional VPC endpoint plus
  encryption/network policy foundations. Goal 3 creates no collection, index,
  mapping, embedding, ingestion, search, RAG behavior, or data-access binding.
- Terraform apply is prohibited in Checkpoint 3A. Checkpoint 3B requires a
  separate, explicit approval that names the development AWS account and
  region.

## Proposed Terraform structure

```text
infrastructure/
  README.md
  .tflint.hcl
  bootstrap/state/
    versions.tf providers.tf variables.tf main.tf outputs.tf
    terraform.tfvars.example README.md
  environments/development/
    versions.tf providers.tf variables.tf locals.tf main.tf outputs.tf
    backend.hcl.example terraform.tfvars.example README.md
  modules/
    network/{versions.tf,variables.tf,main.tf,outputs.tf}
    iam/{versions.tf,variables.tf,main.tf,outputs.tf}
    kms/{versions.tf,variables.tf,main.tf,outputs.tf}
    storage/{versions.tf,variables.tf,main.tf,outputs.tf}
    secrets/{versions.tf,variables.tf,main.tf,outputs.tf}
    runtime/{versions.tf,variables.tf,main.tf,outputs.tf}
    data-services/{versions.tf,variables.tf,main.tf,outputs.tf}
    observability/{versions.tf,variables.tf,main.tf,outputs.tf}
    opensearch-foundation/{versions.tf,variables.tf,main.tf,outputs.tf}
  tests/
    network.tftest.hcl storage.tftest.hcl data-services.tftest.hcl
    development.tftest.hcl
```

The implementation will also update `.gitignore`, `.pre-commit-config.yaml`,
`Makefile`, `scripts/dev.py`, `scripts/dev.ps1`, `.github/dependabot.yml`,
`README.md`, `docs/DEVELOPMENT.md`, `docs/REPOSITORY_STRUCTURE.md`, and
`docs/SECURITY.md`. It will create `.github/workflows/terraform.yml`,
`docs/INFRASTRUCTURE.md`, and `docs/TERRAFORM_STATE.md`.

## Module responsibilities and dependency graph

| Module | Responsibility |
| --- | --- |
| `bootstrap/state` | Dedicated encrypted/versioned/private S3 state bucket, state KMS key, TLS-only policy, and S3 native lockfiles. |
| `network` | VPC, one NAT-only public subnet, private application/data subnets, routes, endpoints, security groups, and flow logs. |
| `iam` | ECS execution/workload roles with least privilege and no direct data-store permissions. |
| `kms` | Separate KMS keys for storage, data services, secrets, logs, and optional AOSS foundations. |
| `storage` | Encrypted/versioned/private raw, curated, business, documents, artifacts, audit, and logs buckets. |
| `secrets` | Secret containers and policies only; no secret values. |
| `runtime` | Internal ALB, ECR repositories, ECS cluster, target groups, and logging references; no task definitions or services. |
| `data-services` | Private encrypted RDS PostgreSQL and ElastiCache Redis foundations. |
| `observability` | CloudWatch log groups, retention, base alarms, alert topic without subscriptions, and X-Ray integration permissions only. |
| `opensearch-foundation` | Optional private endpoint plus encryption/network policy foundations only. |

```text
state bootstrap
  └─ development remote backend

network + kms
  ├─ endpoint / ALB / runtime security groups
  ├─ RDS and Redis private subnet groups
  ├─ VPC flow logs
  └─ OpenSearch Serverless VPC endpoint

kms ──► storage / secrets / log groups / RDS / Redis / optional AOSS policy
iam + observability ──► ECS foundation
storage + secrets + data-services + runtime ──► development outputs
```

## Environment inputs and conventions

`terraform.tfvars.example` will contain placeholders only. Terraform source
must not set or infer the following values:

- AWS account ID, profile or workload identity, and region.
- VPC CIDR, application/data subnet CIDRs, and Availability Zone count.
- Internal ingress CIDRs, DNS domain, and ACM certificate ARN.
- RDS and Redis sizing, maintenance, backups, deletion protection, and
  retention choices.
- NAT/endpoints, alarm thresholds, alert subscribers, cost center, and owner.

Safe development recommendations are two Availability Zones, one NAT Gateway,
an internal-only ALB, S3 gateway plus ECR API/DKR, CloudWatch Logs, and Secrets
Manager interface endpoints, and deletion protection/final snapshots enabled
for durable services. Exact CIDRs require collision checks before use.

Names use:

```text
<organization>-<project>-<environment>-<region>-<component>
```

S3 names append validated account ID and a stable Terraform suffix for global
uniqueness. Mandatory tags are `Project`, `Environment`, `Component`,
`ManagedBy=terraform`, `Owner`, `CostCenter`, and `DataClassification`.

Outputs expose identifiers, ARNs, endpoints, bucket names, log groups, and
secret ARNs only. They never expose password, token, or secret payload values.

## Security, state, and cost controls

- RDS and Redis are private in data subnets and accept traffic only from an
  approved future runtime security group.
- The internal ALB accepts traffic only from configured private CIDRs. ECS
  tasks have no public IPs.
- Data subnets have no direct internet route. Application subnet outbound uses
  the configured NAT and VPC endpoints reduce NAT traffic.
- Every S3 bucket enables KMS encryption, versioning, ownership controls,
  TLS-only access, and public-access blocking. `force_destroy` is prohibited.
- ECR images use immutable tags and scan on push.
- Terraform creates secret containers or references only. It never stores
  plaintext secrets in source or asks for them in chat.
- No IAM static access keys, generic administrator policies, or direct agent
  access to S3, OpenSearch, RDS, Redis, Databricks, or AWS administrative APIs
  are created.
- OpenSearch foundation is optional because it has cost. RDS/Redis sizing,
  retention, NAT strategy, VPC endpoint selection, and alarm thresholds are
  explicit inputs.

### Terraform state bootstrap strategy

Terraform state is sensitive. The strategy is an isolated S3 backend with
SSE-KMS, versioning, public-access blocking, a TLS-only bucket policy, and
Terraform S3 lockfiles (`use_lockfile = true`).

The separate `bootstrap/state` root initially uses local state only for the
first approved development bootstrap. Immediately after creation, its state is
migrated into the newly created encrypted state bucket. Development state uses
the isolated key `development/terraform.tfstate`. No staging or production
environment root is created in Goal 3.

State is never committed, printed, uploaded as a CI artifact, or read with
verbose Terraform logging. The Terraform identity alone receives state access.

## Checkpoint 3A — Code, validation, and plan

1. Create the Terraform modules, development root, bootstrap root, input
   validation, naming/tagging locals, examples, documentation, commands,
   pre-commit hooks, credential-free CI, and mocked Terraform contract tests.
2. Validate CIDR syntax and inputs, development environment name, mandatory
   tags, retention ranges, endpoint allowlists, and internal-only ALB rules.
3. Contract-test private networking, S3 encryption/public blocking,
   security-group boundaries, naming/tag output, and the AOSS non-data-plane
   boundary using mocked providers.
4. Run the following checks without AWS credentials:

```powershell
terraform -chdir=infrastructure/environments/development fmt -check -recursive
terraform -chdir=infrastructure/environments/development init -backend=false
terraform -chdir=infrastructure/environments/development validate
terraform -chdir=infrastructure/environments/development test
tflint --init
tflint --recursive infrastructure
trivy config --severity HIGH,CRITICAL --exit-code 1 infrastructure
.\scripts\dev.ps1 check
uv run pre-commit run --all-files
```

Equivalent Make targets:

```bash
make tf-fmt-check
make tf-validate
make tf-test
make tf-lint
make tf-security
make check
```

5. `tf-plan-dev` requires all non-secret development inputs and separately
   approved local AWS credentials. It validates the caller account and runs
   `terraform plan` only.
6. CI runs only formatting, backend-free validation, contract tests, TFLint,
   Trivy, and secret checks. It receives no AWS credentials and performs no
   Terraform plan or apply.

### Checkpoint 3A acceptance criteria

- Terraform formatting, offline validation, contract tests, linting, static
  IaC security scanning, pre-commit, and existing Goal 2 checks pass.
- No credentials, plaintext secret values, state files, hard-coded global S3
  names, public RDS/Redis paths, ECS services, agent code, Databricks, Doris,
  or OpenSearch collection/index resources are present.
- A connected development plan is produced only when approved credentials and
  all required values are available. Otherwise the exact blocker is reported.

### Checkpoint 3A stopping condition

Stop for review. Do not run `terraform apply`, bootstrap state, create AWS
resources, or access a local AWS profile/workload identity without new explicit
approval.

## Checkpoint 3B — Apply and smoke test

Checkpoint 3B requires explicit approval that names the development AWS account
and region.

1. Verify caller identity, approved account, region, plan digest, resource
   count, and budget-sensitive inputs.
2. Bootstrap remote state, migrate bootstrap state, run a fresh development
   plan, and apply only the reviewed plan.
3. Smoke-test:
   - VPC, route tables, endpoint placement, and VPC Flow Log delivery.
   - RDS/Redis private placement and rejection of unauthorized paths.
   - Internal-only ALB and absence of deployed application targets.
   - S3 encryption, versioning, TLS-only policy, and public-access blocks.
   - ECR encryption, scanning, and immutable tags.
   - Secret containers/references without exposing secret values.
   - AOSS endpoint private-network reachability and unauthorized-path rejection
     only; no collection/index/data-plane test.
   - CloudWatch retention, alarms, and a second Terraform plan with no drift.
4. Run `terraform plan -detailed-exitcode`; exit code `0` is required.

### Checkpoint 3B acceptance criteria

- Resources are confined to the approved development AWS account and region.
- RDS and Redis are private, encrypted, and reachable only through intended
  security-group paths.
- All S3 buckets are unique, encrypted, versioned, TLS-only, and public-blocked.
- Runtime foundations exist without API, LangGraph, agents, tool services,
  Databricks, Doris, or OpenSearch knowledge-layer deployment.
- AOSS contains only the approved endpoint/policy foundation and no collection,
  index, document, embedding, or retrieval behavior.
- No unplanned drift, public data path, plaintext secret, or unauthorized
  network path is observed.

## Rollback and destroy strategy

- Before Checkpoint 3B, rollback is a Git revert because no cloud state exists.
- After Checkpoint 3B, correct configuration with reviewed Terraform changes;
  never automatically destroy state buckets, S3 data, RDS, Redis, KMS keys, or
  secrets.
- Any destroy requires separate explicit approval, state-backup verification,
  backup/snapshot review, and deletion-protection confirmation.

## Final stopping condition

Goal 3 stops after Checkpoint 3A review. Checkpoint 3B begins only after the
user explicitly approves the reviewed apply for the named development account
and region.
