# Goal 6 RBAC remediation — task-definition apply

Date: 2026-08-19
Status: **PASS — REVISION 10 ACTIVE; NO TASK RUN**

## Approved artifact

| Item | Value |
| --- | --- |
| AWS account | `736956442295` |
| Region | `ap-southeast-1` |
| Saved-plan SHA-256 | `09a97fcdc9cacdbd82e69ea8157a7f74753fc8578d5280be8ce62433179ac7db` |
| Immutable image digest | `sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6` |

Immediately before apply, connected identity inspection confirmed account
`736956442295`, region `ap-southeast-1`, the unchanged saved-plan SHA-256, and
exactly two `delete,create` actions caused only by `container_definitions`.

## Apply result

Terraform completed successfully with `2 added, 0 changed, 2 destroyed`.
For ECS task definitions, this represents deregistration/replacement in state
and registration of new immutable revisions; no ECS task was launched.

| Task definition | Result | Default command |
| --- | --- | --- |
| `ask-david-development-doris-admin-refresh:10` | ACTIVE | `/app/doris-admin-refresh` |
| `ask-david-development-doris-verifier:10` | ACTIVE | `/app/doris-readonly-verify` |

Read-only ECS inspection confirms both revisions use Fargate, `awsvpc`, `512`
CPU, `1024` MiB memory, and the exact reviewed image digest. Neither family had
a RUNNING task after the apply.

## Scope controls

- No task execution, retry, Doris SQL, ECR push, or Databricks operation ran.
- No IAM, KMS, network, security-group, EC2/EBS, S3, public-exposure, or
  production change occurred.
- No credential or secret value was retrieved or printed.

## Next boundary

The image is deployed but its remediated RBAC classifier has not yet produced
connected evidence. One revision-10 RBAC verifier run requires a separate
explicit no-retry approval and must stop for review on any nonzero exit or
wrong rejection layer.
