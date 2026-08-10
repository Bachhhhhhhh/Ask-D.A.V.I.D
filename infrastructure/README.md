# AWS infrastructure foundation

Goal 3 provides the Terraform source for a single development environment; no
staging or production root exists. Its connected execution state is recorded
in `docs/verification/GOAL-03B-CONNECTED-EXECUTION-2026-08-05.md`, not
inferred from this README. Modules provide private application/data subnets,
controlled NAT egress and VPC endpoints, internal ALB/ECS/ECR foundations,
private RDS/Redis, encrypted S3 purpose buckets, KMS, secret *containers*, IAM
roles, CloudWatch, and an optional OpenSearch Serverless VPC endpoint with
encryption/network policy foundations. It creates no collections, indexes,
mappings, ingestion, RAG, ECS services, agents, Databricks resources, Doris,
or data.

The CloudWatch foundation contains exactly one base RDS CPU alarm. It evaluates
five consecutive one-minute average `CPUUtilization` datapoints for the managed
DB instance and uses the existing encrypted alert topic as its only action.
`rds_cpu_alarm_threshold_percent` is required; the reviewed development value
and committed example are `90`. No SNS subscription is created. The
observability KMS policy permits only the exact same-account alarm to use the
key for encrypted topic publishing.

The only task definitions are the three static, one-off private Fargate smoke
checks described in `docs/INFRASTRUCTURE.md`. Their reviewed upstream image
digests are pulled through the account-private `ecr-public` ECR pull-through
cache. A dedicated smoke-only security group has a documented temporary
TCP/443 NAT fallback after Fargate did not use the configured private ECR
endpoint DNS during a connected retry. The tasks have no public IP and the
fallback must never be reused by an application, service, agent, or general
workload. They are never attached to a service, and must be created/applied
and launched only through the separately approved Goal 3B checkpoint.

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

The ignored development `terraform.tfvars` must include the approved
`rds_cpu_alarm_threshold_percent` before preflight or a connected plan. The
read-only `infrastructure/scripts/smoke.ps1` accepts the Terraform alarm name,
threshold, and alert-topic ARN and validates the exact alarm contract without
changing alarm state or publishing a notification.

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
