# Goal 6 stable FE/BE private-IP remediation — connected plan review

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Workspace/backend: Terraform development S3 backend

## Saved artifact

- Artifact: `infrastructure/environments/development/goal-06-doris-private-ip-remediation-20260814.tfplan`
- SHA-256: `5e1cf1ae3be48d2565635da4cd1d73bbb14e3addd90d4ce71ff93511c55729d1`
- Plan result: `4 to add, 0 to change, 4 to destroy`
- Action semantics: four destroy/create replacements, not standalone volume deletion

## Expected action review

The plan JSON contains exactly these four non-no-op addresses:

1. `module.doris_serving.aws_instance.fe[0]` — replacement for the rendered
   Terraform-owned bootstrap and stable FE private-IP contract.
2. `module.doris_serving.aws_instance.be[0]` — replacement for the rendered
   Terraform-owned bootstrap and stable BE private-IP contract.
3. `module.doris_serving.aws_volume_attachment.fe[0]` — attachment recreation
   to the replacement FE, retaining volume `vol-012bc3410278ed85e` at `/dev/sdf`.
4. `module.doris_serving.aws_volume_attachment.be[0]` — attachment recreation
   to the replacement BE, retaining volume `vol-01e9b0ed05f7b92b9` at `/dev/sdf`.

The planned instances retain:

| Role | Private IP | Subnet | Public IP |
| --- | --- | --- | --- |
| FE | `10.42.69.177` | `subnet-09bc95f43115dca3e` | disabled |
| BE | `10.42.77.49` | `subnet-09bc95f43115dca3e` | disabled |

The action-contract check over the saved plan passed: exactly four
`["delete", "create"]` changes, no in-place changes, and no other resource
address. No ECS task definition, IAM, KMS, network, security-group, S3, ECR,
Databricks, production, or public-exposure action is present.

## Safety boundary

- The plan only refreshed/read AWS and Databricks state and wrote a local saved
  artifact.
- No Terraform apply, destroy, task launch, SQL run, bundle operation, or
  volume reset was performed.
- The exact SHA-256-bound apply was approved and completed successfully on
  `2026-08-14`: `4 added, 0 changed, 4 destroyed`.
- New FE `i-07092c079553a0e63` is running at `10.42.69.177`; new BE
  `i-0747c1f2e6dd51c1d` is running at `10.42.77.49`. Both are private in
  `subnet-09bc95f43115dca3e` with no public IP.
- Existing encrypted volumes remain attached at `/dev/sdf`:
  `vol-012bc3410278ed85e` to FE and `vol-01e9b0ed05f7b92b9` to BE. Immediate
  read-only EC2 inspection confirmed `running` and `attached` states.
- No Goal 6 task, SQL run, bundle operation, or additional AWS mutation was
  performed. Goal 6 remains blocked until both hosts emit `doris-port-ready`;
  prior evidence remains `doris-port-unavailable`.
