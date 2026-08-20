# Goal 6 Doris serving-state rebuild — connected plan

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Plan artifact: `infrastructure/environments/development/goal-06-doris-serving-state-rebuild-20260814.tfplan`
Plan SHA-256: `ce05eb8cd3b1a90b3c80b424bdae8bf99bc6a909e9a7e55dd27b3cd0c976da6c`

## Read-only plan execution

Terraform refreshed the existing S3-backed development state and AWS/
Databricks provider state. The plan used the CLI-only input
`goal_6_rebuild_serving_state=true`; the ignored `terraform.tfvars` file was
not modified. No apply, destroy, task, SQL/job, bundle, ECR, or ad-hoc AWS/
Databricks mutation occurred.

The plan was generated from a temporary provider-cache/configuration copy of
the exact repository source and copied byte-for-byte to the ignored repository
artifact. Both copies have the SHA-256 above.

## Exact managed-resource action set

| Address | Action | Purpose |
| --- | --- | --- |
| `module.doris_serving.aws_ebs_volume.fe_data_rebuild[0]` | create | New encrypted 20 GiB FE metadata volume |
| `module.doris_serving.aws_ebs_volume.be_data_rebuild[0]` | create | New encrypted 50 GiB BE serving-state volume |
| `module.doris_serving.aws_instance.fe[0]` | replace | Mount the new FE volume and rerun declarative bootstrap |
| `module.doris_serving.aws_instance.be[0]` | replace | Mount the new BE volume and rerun declarative bootstrap |
| `module.doris_serving.aws_volume_attachment.fe[0]` | replace | Detach old FE attachment and attach new volume |
| `module.doris_serving.aws_volume_attachment.be[0]` | replace | Detach old BE attachment and attach new volume |

Machine-readable action inspection reported exactly six non-no-op resource
addresses: two creates, two instance replacements, and two attachment
replacements. It reported zero in-place updates and zero standalone deletes.
The existing FE volume `vol-012bc3410278ed85e` and BE volume
`vol-01e9b0ed05f7b92b9` are not deleted; their Terraform resources remain
protected by `prevent_destroy=true`.

## Stop/approval boundary

This is a saved plan only. A separate exact-hash approval is required before
applying it. Before approval, the expected invariants are:

- old FE/BE volumes: zero delete;
- IAM, KMS, networking, security groups, S3, ECR, Databricks, task
  definitions, public exposure, and production: zero action;
- no volume format/reset or Doris metadata-recovery flag;
- no verifier task until both replacement hosts emit `doris-port-ready`.

After any approved apply, inspect private IPs, instance health, new volume IDs,
encryption, attachment paths, `DeleteOnTermination=false`, and both readiness
markers before proceeding to Goal 6 task verification.
