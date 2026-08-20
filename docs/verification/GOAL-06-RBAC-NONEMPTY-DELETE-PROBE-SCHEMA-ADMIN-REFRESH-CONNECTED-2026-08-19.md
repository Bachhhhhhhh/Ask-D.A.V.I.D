# Goal 6 SMALLINT probe remediation admin refresh — 2026-08-19

## Scope and approval boundary

One separately approved private admin-refresh ECS task was launched from the
Terraform-created revision-14 task definition. The wrapper performed its
fail-closed preflight, launched exactly one task, waited for STOPPED, inspected
the task and CloudWatch completion marker, and did not retry. No verifier task,
additional ECS task, Terraform operation, ECR push, Databricks mutation, or
unrelated AWS operation occurred.

## Launch contract

| Check | Result |
| --- | --- |
| AWS account / region | PASS — `736956442295` / `ap-southeast-1` |
| Cluster | PASS — `ask-david-development-cluster` |
| Task definition | PASS — `ask-david-development-doris-admin-refresh:14` |
| Image | PASS — digest `sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88` |
| Command | PASS — `/app/doris-admin-refresh` |
| Subnets | PASS — `subnet-034f5f1c9bca753f1`, `subnet-0a1aad220d82ef879` |
| Security group | PASS — `sg-07a0dd2e8af8aa178` |
| Public addressing | PASS — `assignPublicIp=DISABLED` |
| FE / BE hosts | PASS — `10.42.64.238` / `10.42.71.97` |

## Task result

| Attribute | Value |
| --- | --- |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/394d846105324da08cc8883fe97f63f6` |
| Status | `STOPPED` |
| Exit code | `0` |
| Stop code | `EssentialContainerExited` |
| Stop reason | `Essential container in task exited` |
| Private subnet | `subnet-034f5f1c9bca753f1` |
| Private IPv4 | `10.42.25.53` |
| ENI | `eni-01e54bf77f8bcecfc` |
| CloudWatch stream | `admin/doris-admin/394d846105324da08cc8883fe97f63f6` |
| Completion marker | PASS — `operation=admin-refresh`, `status=completed` |
| Running tasks after completion | PASS — `[]` |

The completed admin refresh ran the version-controlled migrations, including
the disposable `SMALLINT` authorization-probe recreation and neutral sentinels
`126` and `128`. The wrapper exposes only non-sensitive task/attachment and
completion metadata; raw log contents are not recorded here.

## Current checkpoint

The disposable schema prerequisite for the non-empty DELETE authorization probe
is now applied successfully. A separate approval is required before launching
one private revision-14 read-only verifier task; no verifier has run yet.
