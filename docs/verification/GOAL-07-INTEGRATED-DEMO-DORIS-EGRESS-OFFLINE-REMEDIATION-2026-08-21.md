# Goal 7 Integrated Demo Doris Egress Offline Remediation — 2026-08-21

## Scope

This remediation addresses one failed integrated-demo task. It changes only
repository Terraform, static validation, regression tests, and documentation.
No connected Terraform plan/apply, AWS mutation, ECS retry, or task execution
is included.

## Failure evidence

- Task: `2ae16132e1574f9c978c666d081f006d`
- Task definition: `ask-david-development-goal7-integrated-demo:1`
- Private ENI: `eni-0bd57007968358c54` (`10.42.40.208`)
- Exit code: `1`
- Error: `Can't connect to MySQL server on '10.42.64.238' (timed out)`

The checked-in network contract had FE ingress TCP/9030 for the Goal 7 task
security group, but the same dedicated task security group had no TCP/9030
egress rule. Its explicit egress allowlist contained only HTTPS and S3 paths.

## Offline correction

Added exactly one gated `aws_vpc_security_group_egress_rule.goal7_demo_to_doris`
with:

- source: the dedicated Goal 7 task security group;
- destination: the existing Doris FE security group;
- protocol/port: TCP/9030;
- gate: `goal_7_demo_task_enabled`;
- no CIDR or public exposure.

## Offline validation

- `terraform fmt -check infrastructure/environments/development/goal7.tf` — PASS;
- `terraform validate -no-color` — PASS;
- `python3 scripts/validate_goal7.py` — PASS;
- `python3 -m pytest -p no:cacheprovider -o addopts='' -q tests/unit/test_goal7_static.py` — 31 passed;
- `python3 -m compileall -q packages/goal7-runtime/src scripts tests/unit/test_goal7_static.py` — PASS;
- trailing-whitespace scan — PASS;
- `git diff --check` — PASS for tracked changes.

Connected planning, apply, and task retry require separate approvals.
