# Goal 6 persisted Doris IP compatibility — offline remediation plan

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: offline implementation complete; no connected plan or AWS mutation
authorized by this document

## Trigger

The listener-diagnostics apply replaced the private FE/BE hosts while keeping
the encrypted role volumes. FE reached `doris-port-ready` on 9030, but BE
later emitted `doris-port-unavailable` on 9050 and cloud-init reported a
`scripts-user` failure. EC2 health remained `ok/ok`. No task or retry was run.

## Evidence and hypothesis

The current hosts use `10.42.69.177` (FE) and `10.42.77.49` (BE). Durable
Goal 6 history records that the same persisted FE metadata and BE serving-data
volumes previously belonged to hosts using `10.42.64.238` and `10.42.71.97`.
Those prior addresses are currently unassigned, and the selected subnet
`10.42.64.0/20` has 4088 available addresses. This makes persisted
single-node identity/IP state the leading hypothesis for the BE startup
failure, but it is not proof of the on-volume metadata because SSM and host
CloudWatch streams are unavailable.

## Implemented offline-only change set

The repository-managed Goal 6 development input contract, ignored development
tfvars, tests, runbook, and validation expectations now use:

```text
FE private IP: 10.42.64.238
BE private IP: 10.42.71.97
```

The remediation must preserve all of the following:

- the pinned FE/BE image digests;
- the existing encrypted FE metadata and BE serving-data volumes;
- the existing data-subnet, private-only security groups, IAM, KMS, routes,
  CloudWatch, ECR, and Secrets Manager resources;
- the existing instance types and root/data volume sizes;
- the no-public-IP posture and synthetic-only scope;
- fail-closed private-IP validation and readiness markers.

No volume deletion, reformat, metadata reset, ad-hoc shell repair, public
ingress, task launch, SQL/job run, or Databricks operation is part of this
remediation.

The implementation changes only the input contract and durable documentation;
it does not assign either address in AWS. The ignored local tfvars remains
untracked and no credentials or state were added to Git.

## Offline validation evidence

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| Goal 6 static/regression pytest subset | PASS — 18 passed |
| `git diff --check` | PASS |
| Terraform formatting for Goal 6 sources | PASS |
| Backend-disabled Terraform validation in isolated local provider mirror | PASS |
| Terraform mock-provider tests | PASS — 7 passed, 0 failed |

The isolated Terraform validation used a temporary provider lockfile/cache;
the tracked lockfile was not changed. No connected backend, AWS provider call,
Terraform plan/apply/destroy, task, SQL/job, bundle, or Databricks operation
occurred.

## Expected approval sequence

1. Review this completed offline source/tests/docs and ignored
   development-input update.
2. Separately create and inspect a saved connected development plan.
3. Require the plan to show only the reviewed FE/BE host and necessary volume
   attachment replacements (plus any explicitly reviewed task-definition
   propagation), with zero unrelated IAM/KMS/network/S3/ECR/Databricks,
   production, public-exposure, or volume-destroy actions.
4. Request a separate hash-bound approval before applying that exact plan.
5. Recheck both private IPv4 addresses, volume attachments, EC2 health, and
   `doris-port-ready` markers before any verifier task.

This implementation is not evidence that the IP change will repair Doris
startup. If
the persisted state remains incompatible, stop and design a declarative
metadata migration/rebuild separately; do not erase the authoritative serving
volume implicitly.
