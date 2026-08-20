# Goal 6 BE-to-FE RPC 9020 remediation — connected plan evidence

Date: 2026-08-18

Environment: development (`736956442295`, `ap-southeast-1`)

Status: saved connected plan created and reviewed. No Terraform apply/destroy,
AWS or Databricks resource mutation, EC2 replacement, ECS task, SQL operation,
or volume operation occurred.

## Authorization and identity

The project owner separately approved read-only AWS identity/state
revalidation and creation of a saved development plan whose only acceptable
managed-resource actions were the paired TCP `9020` security-group rule
creates.

Read-only identity verification returned:

- AWS account: `736956442295`;
- AWS region: `ap-southeast-1`;
- IAM principal: `arn:aws:iam::736956442295:user/bach_dev_admin_david`.

Ignored local `terraform.tfvars` and `backend.hcl` were present and were not
printed, modified, or added to Git.

## Local Terraform initialization

The first plan attempt stopped before state refresh because the repository
cache lacked the lock-selected `random 3.9.0` and `databricks 1.122.0`
provider packages. A backend-disabled provider-cache initialization then
stopped because `.terraform/modules/modules.json` is not writable. Neither
attempt created a plan or changed a cloud resource.

The successful retry used a new `TF_DATA_DIR` under `/tmp`, initialized the
existing S3 backend and exact lock-selected providers with
`-lockfile=readonly`, then created the saved plan. The repository-local
`.terraform` directory and dependency lock file were not repaired or changed
as part of this operation.

## Saved plan identity

- artifact:
  `/tmp/ask-david-goal6-rpc-9020-plan.DGzllw/goal-06-be-fe-rpc-9020-20260818.tfplan`;
- Terraform data directory:
  `/tmp/ask-david-goal6-rpc-9020-tfdata.46Rq6Q`;
- SHA-256:
  `2e5d7aaa4889fd90865f312c3659f6ce1f41cc6a82dde8d8a3faecb56fb9ae4b`;
- repository HEAD at plan time:
  `b85088a0988329d4113b39b8c3a7e68b2a8c0d07`;
- Doris serving module SHA-256:
  `a5c6b6ac408382861daed8af53adc44c077a6cc1f969f70e431b2882af849880`.

The saved plan and temporary provider/backend data are local artifacts and
must never be committed.

## Reviewed managed-resource actions

Terraform summary: `2 to add, 0 to change, 0 to destroy`.

| Address | Action | Source SG | Destination SG | Protocol/port |
| --- | --- | --- | --- | --- |
| `module.doris_serving.aws_vpc_security_group_egress_rule.be_to_fe_rpc[0]` | create | BE `sg-0a21b2270f7fcd689` | FE `sg-019b900ee5601c208` | TCP `9020` |
| `module.doris_serving.aws_vpc_security_group_ingress_rule.be_to_fe_rpc[0]` | create | BE `sg-0a21b2270f7fcd689` | FE `sg-019b900ee5601c208` | TCP `9020` |

Filtered saved-plan JSON confirms both resources have exact
`from_port = 9020`, `to_port = 9020`, `ip_protocol = "tcp"`, and the paired
security-group references shown above.

## Negative action review

- update: zero;
- replacement: zero;
- destroy: zero;
- EC2 or user-data action: zero;
- EBS volume or attachment action: zero;
- IAM/KMS action: zero;
- ECS/task-definition action: zero;
- Databricks managed-resource action: zero;
- public ingress/CIDR exposure: zero;
- production action: zero;
- unrelated managed-resource action: zero.

The plan refresh read current AWS and Databricks state but performed no
resource mutation.

## Next approval boundary

Apply only the exact saved artifact above after a separate approval bound to
its SHA-256. Before apply, reverify the account/region, artifact hash, Terraform
data directory, and filtered two-resource action set. Do not generate an
implicit replacement plan.

After apply, immediate read-only inspection must confirm both SG rules. Then
obtain direct BE evidence that the four FE callback timeout families cease and
that BE storage/capacity is usable before resuming any admin-refresh or verifier
task. A healthy EC2 state or local listener alone is insufficient.
