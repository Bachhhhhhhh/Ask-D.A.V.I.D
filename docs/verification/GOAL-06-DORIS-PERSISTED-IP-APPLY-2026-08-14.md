# Goal 6 persisted Doris IP remediation — apply evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Approval: explicit confirmation for the saved plan below

## Immutable plan and apply result

```text
Plan: infrastructure/environments/development/goal-06-doris-persisted-ip-remediation-20260814.tfplan
SHA-256: c7d1368001470bff744d38eb50e6dfb77e6b1f40a7a1a10a1d70c33112cca83e
Terraform result: Apply complete! Resources: 6 added, 0 changed, 6 destroyed.
```

The first local apply attempt stopped before any AWS mutation because its
temporary dependency lock did not match the saved plan. The approved artifact
was then applied unchanged in an isolated context using the exact plan-time
provider lockfile (`aws 6.56.0`, `databricks 1.122.0`, `random 3.9.0`). No new
plan was created and no implicit retry or alternate action set was used.

## Managed actions observed

The six actions match the reviewed plan exactly:

- replace FE EC2 instance and its existing `/dev/sdf` attachment;
- replace BE EC2 instance and its existing `/dev/sdf` attachment;
- register the admin-refresh task-definition revision with the new FE/BE
  hosts;
- register the read-only verifier task-definition revision with the new FE
  host.

No IAM, KMS, S3, ECR, security-group, route, subnet, RDS, Redis, Databricks,
production, or public-exposure action was performed. No ECS task was run.

## Read-only post-apply inspection

| Component | Result |
| --- | --- |
| FE | `i-0086c691d5d975ba0`, running, private `10.42.64.238`, subnet `subnet-09bc95f43115dca3e`, no public IP |
| BE | `i-029fd9a3bed8fe2e7`, running, private `10.42.71.97`, subnet `subnet-09bc95f43115dca3e`, no public IP |
| VPC/AZ | `vpc-007ba758b98a9ab9e`, `ap-southeast-1a` for both instances |
| FE data volume | `vol-012bc3410278ed85e`, 20 GiB, encrypted, `in-use`, attached `/dev/sdf`, `DeleteOnTermination=false` |
| BE data volume | `vol-01e9b0ed05f7b92b9`, 50 GiB, encrypted, `in-use`, attached `/dev/sdf`, `DeleteOnTermination=false` |
| Old FE/BE | `i-0ce389278aecaf8a6` and `i-07c6ec23f7cb40476` terminated; no data volume was deleted |
| Admin task definition | family `ask-david-development-doris-admin-refresh`, revision 7, ACTIVE; hosts `10.42.64.238`/`10.42.71.97` |
| Verifier task definition | family `ask-david-development-doris-verifier`, revision 7, ACTIVE; FE host `10.42.64.238` |

The first immediate EC2 readiness snapshot reported both platform checks as
`initializing`. A later single read-only snapshot reports `System=ok` and
`Instance=ok` for both hosts, and both console outputs contain
`host-prerequisites-ready`. Neither console output contains
`doris-port-ready`, `doris-port-unavailable`, or `container-launch-failed`.
Console output confirms the expected private addresses and data-volume
mount/recovery. SSM credential warnings are expected because no SSM
instance-management role is part of this reviewed change.

Therefore the persisted-IP hypothesis is deployed and host prerequisites are
ready, but FE/BE Doris listener readiness remains **UNVERIFIED**: a positive
listener marker has not been observed. Do not launch a verifier task, perform
a retry, reset either volume, or create another plan until a separate
read-only readiness review is approved. If a listener still fails, stop and
design the next declarative remediation without erasing persisted metadata.

## Verification commands

The apply used the exact saved artifact with Terraform v1.15.8. Post-apply
inspection used only read-only `sts get-caller-identity`, EC2
`describe-instances`, `describe-instance-status`, `describe-volumes`,
`get-console-output`, and ECS `describe-task-definition` calls. No task run,
AWS CLI mutation, Databricks operation, SQL/job, bundle operation, or destroy
command was issued after the approved apply.

## Checkpoint

Goal 6 remains **NOT VERIFIED** and blocked at Doris application listener
readiness. The infrastructure replacement and stable private-IP portion is
implemented and applied; service readiness and all later Goal 6 acceptance
phases remain outstanding.
