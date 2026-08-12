# Development environment

This is the only environment declared in Goal 3. `terraform.tfvars` and
`backend.hcl` are local, ignored files. `infra-plan` deliberately refuses to
contact AWS unless `ASK_DAVID_AWS_PLAN_APPROVED=true`, a profile or workload
identity is available, and both files exist. Checkpoint 3B requires separate
written approval before `terraform apply`.

Goal 4 adds a three-state rollout gate that is inert unless explicitly set in
the ignored `terraform.tfvars`:

- `disabled` (checked-in default): no Goal 4 resource or connected data lookup;
- `bootstrap`: storage credential plus AWS IAM/KMS integration and seven
  zero-byte, SSE-KMS managed-root markers only, split into an initial-role
  apply with self-assumption disabled and a later trust-policy-only apply with
  self-assumption enabled;
- `active`: strict storage validation plus approved development namespace,
  identities, bindings, and grants.

The two bootstrap sub-steps and the active stage each require separate
saved-plan review and apply approval. Keep
`goal_4_storage_role_self_assumption_enabled = false` for initial role
creation. Only after that apply succeeds may the ignored input be changed to
`true` for an in-place trust-policy-only plan. Validate the credential only
after that second apply. The `active` stage is rejected while the flag is
false. Do not jump directly to `active`, and do not use a targeted apply.
If validation reports `PATH_EXISTS = FAIL` for the otherwise empty approved
prefixes, the marker remediation requires its own reviewed saved plan, apply,
and one-shot revalidation approvals. Markers are Terraform-owned and must not
be created ad hoc.
The exact local inputs and stopping conditions are documented in
`docs/runbooks/GOAL-04-DATABRICKS-LAKEHOUSE.md`.

Run `infra-preflight` before requesting Goal 3B approval. It does not contact
AWS and permits only `kms_key_id` to remain deferred. That ARN must come from
the approved bootstrap root's `state_kms_key_arn` output; it must not come from
the development KMS module. Development state must use the key
`development/terraform.tfstate` so it cannot overwrite bootstrap state.
