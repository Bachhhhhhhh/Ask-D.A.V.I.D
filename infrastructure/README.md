# AWS infrastructure foundation

Goal 3 provides Terraform code only; it has not created AWS resources. The
development root is in `environments/development`; no staging or production
root exists. Modules provide private application/data subnets, controlled NAT
egress and VPC endpoints, internal ALB/ECS/ECR foundations, private RDS/Redis,
encrypted S3 purpose buckets, KMS, secret *containers*, IAM roles, CloudWatch,
and an optional OpenSearch Serverless VPC endpoint with encryption/network
policy foundations. It creates no collections, indexes, mappings, ingestion,
RAG, services, agents, Databricks resources, Doris, or data.

## Commands

```powershell
.\scripts\dev.ps1 infra-format
.\scripts\dev.ps1 infra-preflight
.\scripts\dev.ps1 infra-validate
.\scripts\dev.ps1 infra-test
.\scripts\dev.ps1 infra-lint
.\scripts\dev.ps1 infra-security
.\scripts\dev.ps1 infra-plan
```

`infra-plan` is read-only but deliberately requires a user-created ignored
`terraform.tfvars`, `backend.hcl`, an AWS identity, and
`ASK_DAVID_AWS_PLAN_APPROVED=true`. It never runs `apply`.

`infra-preflight` is fully offline. It checks that the ignored bootstrap and
development variable files contain every required assignment, mandatory
ownership/cost tags agree, backend bucket/account/region values agree, state
keys cannot collide, and no non-KMS placeholder remains. The development
backend `kms_key_id` is intentionally allowed to remain unresolved until the
approved state bootstrap apply returns `state_kms_key_arn`.
`infra-plan` reruns the same checks in strict mode and refuses a connected
plan while that KMS ARN is still deferred.

Remote state is bootstrapped only after separate Checkpoint 3B approval; see
`bootstrap/state/README.md`. State and plans are sensitive and ignored.

Install the static validation prerequisites before running the full gate:

```powershell
winget install Hashicorp.Terraform
winget install TerraformLint.TFLint
winget install AquaSecurity.Trivy
```

The bootstrap root deliberately uses local state until its approved first
apply. The development root declares a partial S3 backend and Checkpoint 3A
must initialize it with `-backend=false`; connected backend initialization is
reserved for Checkpoint 3B. The development lock file is committed to pin the AWS provider; `.terraform/`,
state, plans, local backend settings, and real variable values are ignored.
