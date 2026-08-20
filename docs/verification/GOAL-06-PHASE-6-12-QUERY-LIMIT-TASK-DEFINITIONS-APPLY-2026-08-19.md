# Goal 6 Phase 6-12 query-limit task definitions — apply

Date: `2026-08-19`

Status: `PASS — APPLIED; QUERY-LIMIT TASK NOT RUN`

## Approved boundary

The apply was explicitly approved for saved plan SHA-256
`c24205563e73adcda4345a1d3707c27807c21a3c701eac3b8469e93f2b982ae1` in AWS
account `736956442295`, region `ap-southeast-1`. The approved scope was only
the two reviewed ECS task-definition replacements. No ECS task, Doris SQL,
ECR push, Databricks operation, or unrelated AWS mutation was performed.

## Apply result

Terraform reported:

```text
Apply complete! Resources: 2 added, 0 changed, 2 destroyed.
```

The replacement was driven only by `container_definitions`, updating the
container image to the immutable query-limit remediation digest
`sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36`.

## Immediate read-only ECS inspection

| Task definition | Revision | Status | Image digest | Running tasks |
| --- | ---: | --- | --- | --- |
| `ask-david-development-doris-admin-refresh` | `15` | `ACTIVE` | exact expected digest | `0` |
| `ask-david-development-doris-verifier` | `15` | `ACTIVE` | exact expected digest | `0` |

Both definitions remain Fargate/`awsvpc` task definitions. The admin command
is `/app/doris-admin-refresh`; the verifier command is
`/app/doris-readonly-verify`. No task was started by this checkpoint.

## Checkpoint

The query-limit remediation image is now registered in revision 15, but Phase
6-12 is still **UNVERIFIED** until one separately approved, private,
no-retry query-limit verifier task runs and produces its expected result
contract. A task approval must be bound to the revision/image and must not
implicitly redeploy or retry.
