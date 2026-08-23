# Goal 7 workload endpoint egress offline remediation — 2026-08-21

## Scope and status

The first approved private Goal 7 indexer task failed before container
startup. Read-only AWS evidence in
`GOAL-07-INDEXER-TASK-FAILURE-2026-08-21.md` showed an available,
private-DNS-enabled Secrets Manager interface endpoint and endpoint-side
TCP/443 ingress from the workload security group, while the workload security
group had no egress permissions. The deterministic blocker is therefore the
missing workload-to-endpoint path.

This remediation is **OFFLINE IMPLEMENTED / NOT CONNECTED**. It changed only
repository source, tests, and documentation. No AWS or Databricks operation,
Terraform connected plan/apply/destroy, ECS retry, bundle operation, or SQL run
was performed.

## Declarative change

`infrastructure/modules/network/main.tf` now declares exactly one standalone
`aws_vpc_security_group_egress_rule.workload_aws_endpoints`:

- source: existing `aws_security_group.workload`;
- destination: existing `aws_security_group.aws_endpoints`;
- protocol/port: TCP/443;
- scope: security-group reference only;
- public CIDR egress: prohibited.

The existing endpoint-side ingress rule is unchanged. No NAT/public fallback
was added for the Goal 7 workload.

## Offline evidence

| Check | Result |
| --- | --- |
| Goal 7 static validator requires the rule | PASS — `python3 scripts/validate_goal7.py` |
| Validator rejects CIDR/public workload egress | PASS — SG-only rule assertion and no-CIDR guard |
| Network module Terraform syntax/format | PASS — `/snap/terraform/912/terraform fmt -check -recursive ...` |
| Goal 7 focused regression test covers the rule | PASS — `python3 -m pytest -p no:cacheprovider -o addopts='' -q tests/unit/test_goal7_static.py` (14 passed) |
| Python compilation and diff integrity | PASS — `compileall` and `git diff --check` |
| Ruff static check | PASS — `.venv/bin/ruff` with temporary cache |
| Network module `terraform test` | UNAVAILABLE — offline module test could not resolve the AWS mock provider without a provider installation; no network initialization was attempted |
| Connected Terraform plan | NOT RUN — separate approval required |
| Terraform apply/destroy or AWS mutation | NOT RUN |
| ECS task retry | NOT RUN |

## Next approval boundary

Create a new saved connected development Terraform plan only after explicit
approval. Expected managed action is exactly one egress-rule create for the
existing workload-to-AWS-endpoints SG path, with zero replacement, destroy,
public exposure, production, Goal 6, Databricks, AOSS, task-definition, or
other resource actions. Apply and any ECS retry require separate approvals.
