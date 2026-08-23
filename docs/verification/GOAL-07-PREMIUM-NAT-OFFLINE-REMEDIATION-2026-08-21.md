# Goal 7 Premium + NAT HTTPS egress offline remediation — 2026-08-21

## Status

**OFFLINE IMPLEMENTED — NOT CONNECTED**

The user approved continuing with the existing Databricks Premium workspace and
the existing private-subnet NAT path instead of Enterprise PrivateLink. This
checkpoint changes only repository Terraform source, static validation, tests,
and documentation. It does not create a Terraform plan, apply or destroy AWS
resources, run an ECS task, run Databricks SQL, push ECR, or mutate Databricks,
AWS, or OpenSearch.

## Declarative boundary

The implementation adds a dedicated `aws_security_group.goal7_tasks`, gated by
`goal_7_indexer_task_enabled || goal_7_demo_task_enabled`. Its implicit egress
is disabled (`egress = []`) and it receives exactly these explicit paths:

1. TCP/443 to `0.0.0.0/0`, which is usable only through the existing private
   subnet route table and NAT gateway for the Premium Databricks workspace
   endpoint;
2. TCP/443 to the existing AWS interface-endpoints SG;
3. TCP/443 to the existing S3 gateway prefix list.

The AWS endpoint SG receives matching TCP/443 ingress from the dedicated Goal 7
SG. Existing AOSS and Doris-FE ingress rules now reference the dedicated SG,
and both Goal 7 task modules receive its ID. The shared workload SG remains
unchanged and does not receive public/CIDR egress. The task placement remains
private subnets with `assignPublicIp=DISABLED` at run time.

The `0.0.0.0/0` rule is intentionally confined to this dedicated Goal 7 SG;
it is not a hostname-level allowlist because AWS security groups cannot express
managed SaaS hostnames. This is the explicit Premium/NAT security trade-off
approved for the development checkpoint. No static Databricks IPs or
credentials were added.

## Expected connected plan scope

Before any connected plan is created, the exact saved plan must be reviewed.
Expected Goal 7-only changes are:

- one gated dedicated Goal 7 task security group;
- one TCP/443 NAT egress rule;
- one AWS-interface-endpoint egress rule;
- one S3-prefix-list egress rule;
- one AWS-interface-endpoint ingress rule;
- replacement/update of the existing Goal 7 AOSS and Doris-FE ingress rules
  solely to reference the dedicated SG; and
- no Goal 6 EC2/EBS, IAM/KMS, Databricks resource, AOSS collection, ECR,
  production, public-IP, or unrelated resource action.

Any additional create, replacement, destroy, public exposure, or production
change stops the checkpoint for review. The next action is a separately
approved saved connected development Terraform plan; apply and ECS retry remain
separate approvals.

## Offline validation

| Check | Result |
| --- | --- |
| Goal 7 static validator | PASS — `python3 scripts/validate_goal7.py` |
| Goal 7 focused regression tests | PASS — `17 passed` |
| Terraform formatting | PASS — direct Terraform binary on modified files |
| Diff integrity | PASS — `git diff --check` |
| Connected Terraform plan/apply/destroy | NOT RUN |
| ECS retry, Databricks SQL, ECR, AOSS, AWS mutation | NOT RUN |
