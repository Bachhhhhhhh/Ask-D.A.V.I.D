# Terraform state handling

Terraform state may contain sensitive resource metadata. It must never be
committed, printed in verbose logs, or stored as a CI artifact.

Goal 3 provides a separate `infrastructure/bootstrap/state` root that creates
the development state bucket only after explicit Checkpoint 3B approval. The
bucket uses S3 versioning, public-access blocking, SSE-KMS, a TLS-only bucket
policy, and native S3 lockfiles. The development backend example uses
`use_lockfile = true`; no DynamoDB lock table is required.

The bootstrap begins with local state solely for the approved bootstrap step.
Both roots declare an empty partial S3 backend. Checkpoint 3A initializes them
with `-backend=false`. Immediately after the approved bootstrap apply, create
an ignored bootstrap `backend.hcl` from its example and migrate that state to
the new encrypted bucket with `terraform init -migrate-state
-backend-config=backend.hcl`.

Bootstrap and development use the same approved state bucket and KMS key but
different object keys: `bootstrap/terraform.tfstate` and
`development/terraform.tfstate`. The KMS ARN comes from the bootstrap output
`state_kms_key_arn`; it cannot be known before the bootstrap apply. Keep both
`backend.hcl` files, real `.tfvars`, state, plans, and provider caches local;
they are covered by `.gitignore`.

Checkpoint 3A never applies the bootstrap or development roots. Checkpoint 3B
requires explicit approval for one named development account and region.
