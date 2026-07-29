# Terraform state handling

Terraform state may contain sensitive resource metadata. It must never be
committed, printed in verbose logs, or stored as a CI artifact.

Goal 3 provides a separate `infrastructure/bootstrap/state` root that creates
the development state bucket only after explicit Checkpoint 3B approval. The
bucket uses S3 versioning, public-access blocking, SSE-KMS, a TLS-only bucket
policy, and native S3 lockfiles. The development backend example uses
`use_lockfile = true`; no DynamoDB lock table is required.

The bootstrap begins with local state solely for the approved bootstrap step.
Immediately migrate that state to the new encrypted bucket with
`terraform init -migrate-state`. Keep `backend.hcl`, real `.tfvars`, state,
plans, and provider caches local; they are covered by `.gitignore`.

Checkpoint 3A never applies the bootstrap or development roots. Checkpoint 3B
requires explicit approval for one named development account and region.
