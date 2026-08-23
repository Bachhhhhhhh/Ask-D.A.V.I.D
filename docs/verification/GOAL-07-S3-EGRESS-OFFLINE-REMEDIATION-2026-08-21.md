# Goal 7 S3 gateway-prefix-list egress offline remediation — 2026-08-21

## Scope and status

The single approved indexer task after the Secrets Manager egress fix failed
before container startup while pulling the digest-pinned ECR image. The error
timed out at `52.219.124.111:443`; read-only inspection showed a healthy S3
gateway route through managed prefix list `pl-6fa54006`, but no workload-SG
egress rule targeting that prefix list.

This remediation is **OFFLINE IMPLEMENTED / NOT CONNECTED**. It changes only
Terraform source, tests, and documentation. No connected plan/apply/destroy,
AWS/Databricks mutation, ECS retry, bundle/SQL run, or ECR operation occurred.

## Declarative change

`infrastructure/modules/network/main.tf` now declares exactly one additional
rule, `aws_vpc_security_group_egress_rule.workload_s3`:

- source: existing `aws_security_group.workload`;
- destination: existing `aws_vpc_endpoint.s3.prefix_list_id`;
- protocol/port: TCP/443;
- scope: managed S3 gateway prefix list only;
- public CIDR or SG-wide alternative: prohibited.

The previously applied interface-endpoint SG rule is unchanged. No NAT route,
endpoint, ECR repository, or task definition was changed.

## Offline validation

| Check | Result |
| --- | --- |
| Goal 7 static validator | PASS — `python3 scripts/validate_goal7.py` |
| Network Terraform formatting | PASS — `/snap/terraform/912/terraform fmt -check -recursive ...` |
| Goal 7 focused pytest regression suite | PASS — 15 passed |
| Ruff and Python compilation | PASS — `.venv/bin/ruff` and `compileall` |
| `git diff --check` | PASS |
| Network module `terraform test` | UNAVAILABLE — offline provider schema was not installed; no network initialization was attempted |
| Connected Terraform plan | NOT RUN — separate approval required |
| AWS/Databricks mutation or ECS retry | NOT RUN |

## Next approval boundary

Create a new saved connected development plan only after explicit approval.
Expected managed action is exactly one `workload_s3` egress-rule create, with
zero replacement, destroy, public/production, Goal 6, task-definition, AOSS,
Databricks, or unrelated resource actions. A new indexer task attempt requires
another separate approval and must not be an implicit retry.
