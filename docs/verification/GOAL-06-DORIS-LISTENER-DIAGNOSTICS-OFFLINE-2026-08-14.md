# Goal 6 listener diagnostics/startup remediation — offline evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: source, tests, and documentation only

## Trigger

The stable-private-IP apply completed successfully, but both hosts emitted
`doris-port-unavailable` after the bounded listener guard. The approved
read-only path could not retrieve the encrypted-volume container diagnostics:
no FE/BE CloudWatch host streams appeared. The current failure evidence is
recorded in
`docs/verification/GOAL-06-DORIS-LISTENER-POST-STABLE-IP-DIAGNOSIS-2026-08-14.md`.

## Source-only remediation

The Terraform-owned host bootstrap now:

1. preserves the Apache Doris image's default `fe.conf` and `be.conf`, and
   mounts only `fe_custom.conf`/`be_custom.conf` overrides for
   `priority_networks`, `enable_ssl`, and `storage_root_path`;
2. bounds `docker run` with `timeout --foreground --kill-after=10s 120s`;
3. records Docker launch output in the encrypted-volume `docker-run.log`;
4. distinguishes a launch failure (`container-launch-failed`) from a stopped
   container and from a listener timeout;
5. records redacted `docker inspect` and `docker logs --tail 200` output even
   when no container ID can be established;
6. configures explicit CloudWatch file paths for bootstrap status, private-IP
   diagnostics, container diagnostics, and Docker launch output, with a
   five-second flush interval.

Stable private IPs, existing FE/BE data volumes, private security groups,
IMDSv2, no-public-IP settings, IAM/KMS scope, and the no-task-before-readiness
guard are unchanged. No metadata or serving-data volume is reset.

## Offline validation

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| Goal 6 pytest subset | PASS — 18 passed |
| Python compilation of validator/tests | PASS |
| Rendered FE/BE bootstrap `bash -n` | PASS |
| Terraform `fmt -check` on tracked Goal 6 Terraform sources | PASS |
| Terraform `validate` with backend disabled | PASS |
| Terraform mock-provider tests | PASS — 7 passed |
| `git diff --check` | PASS |

The repository-wide platform-foundation suite and all checks that require
`pydantic` are explicitly excluded from the Goal 6 acceptance gate. They are a
separate Goal 2 development concern, so their installation or verification is
not required for a Goal 6 status.
No connected Terraform plan/apply/destroy, AWS/Databricks mutation, ECS task,
SQL run, bundle operation, or ECR operation occurred for this remediation.

## Next approval boundary

After review, create one saved connected development Terraform plan. The
expected managed actions are only the FE/BE bootstrap/user-data replacements;
the plan must contain zero volume reset/deletion, IAM/KMS, network,
security-group, S3, ECR, Databricks, public-exposure, production, task, or
unrelated replacement actions. Apply and any task launch require separate
hash-bound approvals. `doris-port-ready` for both hosts remains mandatory
before a verifier task.
