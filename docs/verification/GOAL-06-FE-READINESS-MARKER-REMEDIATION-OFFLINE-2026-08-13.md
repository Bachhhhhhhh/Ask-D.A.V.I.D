# Goal 6 FE readiness-marker remediation — offline evidence

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: source, tests, runbook, and offline validation only

## Trigger

After the FE/BE discovery-variable remediation was applied, EC2 platform
checks passed but one approved revision-4 private admin-refresh task still
failed with:

```text
ERROR 2002 (HY000): Can't connect to server on '10.42.78.72' (115)
```

The task was not retried. The evidence did not distinguish an FE process that
was still bootstrapping from a process that had exited, because the previous
bootstrap guard emitted its status only to cloud-init stdout/stderr. EC2
`running` and platform checks are not Doris application readiness.

## Minimal declarative remediation

The host template now persists non-sensitive JSON lifecycle markers to the
encrypted role-volume log directory:

```text
<role>-log/bootstrap-status.log
```

The dedicated CloudWatch agent already collects `*.log` from that directory.
The marker states are:

- `bootstrap-started`;
- `container-exited`;
- `doris-port-ready`;
- `doris-port-unavailable`;
- `invalid-private-ip` / `missing-fe-private-ip`.

The runbook now requires `doris-port-ready` evidence for both FE and BE before
launching a private verifier task. No public ingress, IAM/KMS permission,
network rule, image, secret, task definition, or cloud resource was changed by
this offline remediation.

## Offline validation

| Check | Result |
| --- | --- |
| Goal 6 static validator | PASS |
| 17 Goal 6 static tests (manual invocation) | PASS |
| Python compile | PASS |
| Rendered FE/BE bootstrap `bash -n` | PASS |
| Terraform formatting on `.tf`/`.tftest.hcl` source set | PASS |
| Terraform `init -backend=false` | PASS |
| Terraform `validate` | PASS |
| `git diff --check` | PASS |
| Default pytest command | UNVERIFIED — host Python has no `pytest` module |

No connected Terraform plan/apply/destroy, AWS/Databricks operation, ECR push,
ECS task, SQL/job run, or bundle operation occurred in this remediation.

## Next boundary

Create and review a new saved connected Terraform plan only after separate
approval. The plan must expose any user-data/task-definition replacement and
must stop on unexpected IAM/KMS/network/public-exposure/production/source-data
actions. After a reviewed apply, read the FE and BE readiness markers before
requesting another one-off private task.
