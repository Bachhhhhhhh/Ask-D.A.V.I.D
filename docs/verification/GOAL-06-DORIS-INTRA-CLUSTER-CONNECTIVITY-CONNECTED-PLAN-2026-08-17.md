# Goal 6 Doris intra-cluster connectivity — connected plan evidence

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Databricks workspace: `7474644358733471`
Status: **AWAITING HASH-BOUND APPLY APPROVAL**

## Authorization and identity

The project owner approved connected read-only identity/state revalidation and
creation of one saved development plan. The approval did not authorize apply,
destroy, ECS task execution, SQL, or any other cloud mutation.

Immediate pre-plan verification passed:

- AWS account: `736956442295`;
- AWS principal: `arn:aws:iam::736956442295:user/bach_dev_admin_david`;
- AWS region: `ap-southeast-1`;
- Databricks profile: `ask-david-development`, valid OAuth authentication;
- Databricks host: `https://dbc-7f3363e3-d129.cloud.databricks.com`;
- Databricks workspace ID: `7474644358733471`;
- authenticated Databricks principal: `bachvxuan@gmail.com`;
- Unity Catalog metastore refreshed without change:
  `3a7f7e7a-680b-4bd6-907a-6d5e77b43178`;
- existing SQL warehouse refreshed without change: `757e0335c6efb51e`.

Terraform initialized the ignored development S3 backend using an isolated
`TF_DATA_DIR` under `/tmp`. The repository's pre-existing `.terraform`
directory is owned by `nobody:nogroup` and was not modified, deleted, or
repermissioned.

## Saved plan

- Artifact:
  `infrastructure/environments/development/goal-06-doris-intra-cluster-connectivity-20260817.tfplan`
- SHA-256:
  `9697f83adeced4944cc9011d7b8b39a8c675d42cfffd7859430e3ba4ecafbb7e`
- Size: `214555` bytes
- Git handling: ignored by the existing `*.tfplan` rule
- Terraform summary: `9 to add, 0 to change, 4 to destroy`
- Doris module source SHA-256:
  `832aab577e80041a86061e608028c8e34bd8d86bb92ef77d7a8cfa5cf1dfcbc3`
- Host bootstrap template SHA-256:
  `9dbbe647c45a3e3dc4b184f1981483eea2283744fd0020b900d1d82a728c6f58`

## Exact managed actions

| Address | Action | Reviewed purpose |
| --- | --- | --- |
| `module.doris_serving.aws_instance.fe[0]` | replace (`delete,create`) | deliver the Terraform-owned bootstrap/evidence source while retaining FE private IP `10.42.64.238` |
| `module.doris_serving.aws_instance.be[0]` | replace (`delete,create`) | deliver the bounded FE-registration guard while retaining BE private IP `10.42.71.97` |
| `module.doris_serving.aws_volume_attachment.fe[0]` | replace (`delete,create`) | detach and reattach the same FE data volume to the replacement FE |
| `module.doris_serving.aws_volume_attachment.be[0]` | replace (`delete,create`) | detach and reattach the same BE data volume to the replacement BE |
| `module.doris_serving.aws_vpc_security_group_ingress_rule.be_to_fe_registration[0]` | create | BE SG to FE SG TCP `9030` ingress |
| `module.doris_serving.aws_vpc_security_group_egress_rule.be_to_fe_registration[0]` | create | BE SG to FE SG TCP `9030` egress |
| `module.doris_serving.aws_vpc_security_group_egress_rule.fe_to_be["8060"]` | create | FE SG to BE SG TCP `8060` egress |
| `module.doris_serving.aws_vpc_security_group_egress_rule.fe_to_be["9050"]` | create | FE SG to BE SG TCP `9050` egress |
| `module.doris_serving.aws_vpc_security_group_egress_rule.fe_to_be["9060"]` | create | FE SG to BE SG TCP `9060` egress |

The four destroy actions are exclusively the delete halves of the two reviewed
EC2 replacements and two attachment replacements. The replacement instances'
encrypted root devices are lifecycle-coupled to those instances; they are not
the dedicated Terraform-managed Doris data volumes.

## Fail-closed review

Filtered `terraform show -json` inspection proved:

- `aws_ebs_volume` non-no-op actions: **0**;
- FE data volume remains `vol-0e8c9175fe79619be` before and after attachment
  replacement;
- BE data volume remains `vol-0b4799bdf2215d397` before and after attachment
  replacement;
- old detached volume reattachment: **0**;
- FE and BE instance types remain `m7i.xlarge`;
- both instances remain in private subnet `subnet-09bc95f43115dca3e`;
- `associate_public_ip_address` remains `false` for both instances;
- all five new network rules use referenced security groups, not CIDRs;
- public exposure changes: **0**;
- IAM/KMS/Secrets Manager/ECS task-definition changes: **0**;
- Databricks changes: **0**;
- production changes: **0**;
- unexpected non-no-op addresses: **0**.

The selected security groups are FE `sg-019b900ee5601c208` and BE
`sg-0a21b2270f7fcd689`. The plan does not broaden either group to a public or
developer CIDR.

## Apply boundary and required evidence

No apply was performed. Applying this binary plan requires a separate approval
that names its exact SHA-256. Immediately before apply, identity/account/region
and artifact hash must be reverified.

After a successful apply, read-only EC2/CloudWatch inspection must associate
evidence with the replacement instance IDs and prove:

- FE: `bootstrap-invoked`, `host-prerequisites-ready`, a ready container
  diagnostics summary, and `doris-port-ready` on `9030`;
- BE: `bootstrap-invoked`, `fe-registration-port-waiting`,
  `fe-registration-port-ready` on `9030`, a ready container diagnostics
  summary, and `doris-port-ready` on `9050`.

Any terminal unavailable/failed marker stops execution before an ECS verifier
task is considered.
