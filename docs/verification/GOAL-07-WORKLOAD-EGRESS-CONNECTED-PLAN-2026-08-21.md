# Goal 7 workload endpoint egress connected plan — 2026-08-21

## Status

**SAVED PLAN CREATED AND REVIEWED — NO APPLY**

The explicitly approved connected development plan refreshed the existing
Terraform state and produced one local saved plan. No apply, destroy, ECS task
retry, AOSS index mutation, Databricks SQL/bundle operation, or other resource
mutation occurred.

## Identity and environment

- AWS account: `736956442295`
- AWS region: `ap-southeast-1`
- AWS principal: `arn:aws:iam::736956442295:user/bach_dev_admin_david`
- Databricks development profile: `ask-david-development` (`Valid: YES`)
- Terraform state: existing development remote state, read-only refresh

## Saved artifact

- plan: `/tmp/goal7-workload-egress.tfplan`
- plan SHA-256:
  `80fa254bb6a62f8c23f257651c92ad935a8fba008e33697427198fc670c018e6`
- plan JSON inspection: `/tmp/goal7-workload-egress.json`
- artifacts are local temporary files and must not be committed.

## Exact action review

Terraform human-readable output: `1 to add, 0 to change, 0 to destroy`.
Independent `terraform show -json` filtering returned exactly one non-no-op:

| Address | Action | Effective values |
| --- | --- | --- |
| `module.network.aws_vpc_security_group_egress_rule.workload_aws_endpoints` | create | workload SG `sg-0a22126b47d3a5aea` → existing AWS endpoints SG `sg-09df4c29eba7991fa`, TCP/443 |

The filtered plan contained `272` no-op resources and no other action. The
planned rule has `cidr_ipv4 = null` and `cidr_ipv6 = null`; it is strictly
security-group referenced.

| Guard | Result |
| --- | --- |
| replacement | 0 |
| destroy | 0 |
| Goal 6 EC2/EBS/attachment action | 0 |
| Goal 7 task-definition action | 0 |
| AOSS, Databricks, production, or public action | 0 |
| AWS account/region | PASS |
| saved-plan hash | PASS |

## Next approval boundary

Applying this exact saved plan requires a separate explicit approval bound to
SHA-256
`80fa254bb6a62f8c23f257651c92ad935a8fba008e33697427198fc670c018e6`.
Do not retry the indexer task before that apply and its read-only SG/endpoint
inspection succeed. Any unexpected plan hash or action set must stop the
checkpoint.
