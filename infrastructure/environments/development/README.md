# Development environment

This is the only environment declared in Goal 3. `terraform.tfvars` and
`backend.hcl` are local, ignored files. `infra-plan` deliberately refuses to
contact AWS unless `ASK_DAVID_AWS_PLAN_APPROVED=true`, a profile or workload
identity is available, and both files exist. Checkpoint 3B requires separate
written approval before `terraform apply`.

Run `infra-preflight` before requesting Goal 3B approval. It does not contact
AWS and permits only `kms_key_id` to remain deferred. That ARN must come from
the approved bootstrap root's `state_kms_key_arn` output; it must not come from
the development KMS module. Development state must use the key
`development/terraform.tfstate` so it cannot overwrite bootstrap state.
