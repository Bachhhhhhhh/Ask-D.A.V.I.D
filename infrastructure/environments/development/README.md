# Development environment

This is the only environment declared in Goal 3. `terraform.tfvars` and
`backend.hcl` are local, ignored files. `infra-plan` deliberately refuses to
contact AWS unless `ASK_DAVID_AWS_PLAN_APPROVED=true`, a profile or workload
identity is available, and both files exist. Checkpoint 3B requires separate
written approval before `terraform apply`.
