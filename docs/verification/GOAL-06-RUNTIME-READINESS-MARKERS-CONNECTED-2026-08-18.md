# Goal 6 runtime readiness markers — connected verification

Date: `2026-08-18`

Result: `PASS`

## Approved execution

The owner approved exactly one private readiness-marker diagnostic using:

- AWS account: `736956442295`
- Region: `ap-southeast-1`
- ECS cluster: `ask-david-development-cluster`
- Task definition: `ask-david-development-doris-admin-refresh:8`
- Immutable image digest:
  `sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad`
- Approved private application subnets:
  `subnet-034f5f1c9bca753f1`, `subnet-0a1aad220d82ef879`
- Admin security group: `sg-07a0dd2e8af8aa178`
- Public IP assignment: `DISABLED`
- FE target: `10.42.64.238:9030`
- BE target: `10.42.71.97:9050`

The repository Bash wrapper performed account and immutable task-definition
inspection before launching. Its only command override was the reviewed,
bounded, read-only `SHOW BACKENDS;` diagnostic. No retry was permitted.

## Task result

| Field | Evidence |
| --- | --- |
| Task ID | `221d070dc24b40b0a1144b573e137fac` |
| Task definition | `ask-david-development-doris-admin-refresh:8` |
| Started | `2026-08-18T16:14:29.852000+07:00` |
| Stopped | `2026-08-18T16:14:52.850000+07:00` |
| Task state | `STOPPED` |
| Container | `doris-admin` |
| Container exit code | `0` |
| ECS stop code | `EssentialContainerExited` — expected for a completed one-off essential container |
| Subnet | `subnet-0a1aad220d82ef879` |
| Private task IP | `10.42.44.26` |
| Network interface | `eni-043fbd0ee4ad551ce` |
| CloudWatch stream | `admin/doris-admin/221d070dc24b40b0a1144b573e137fac` |
| Retry count | `0` |

ECS attachment metadata proves the task used an approved private application
subnet and a private RFC1918 address. The reviewed launch configuration bound
only admin SG `sg-07a0dd2e8af8aa178` and set
`assignPublicIp=DISABLED`. The immediate post-stop EC2 lookup returned
`InvalidNetworkInterfaceID.NotFound` because Fargate had already deleted the
ephemeral ENI; this is expected cleanup and not contradictory network evidence.

## Exact marker evidence

The task's dedicated CloudWatch stream contains:

```json
{"goal":"goal-06","operation":"readiness-markers","role":"fe","listener_state":"ready"}
{"goal":"goal-06","operation":"readiness-markers","role":"fe","marker":"doris-port-ready","port":9030}
{"goal":"goal-06","operation":"readiness-markers","role":"be","listener_state":"ready"}
{"goal":"goal-06","operation":"readiness-markers","role":"be","marker":"doris-port-ready","port":9050}
{"goal":"goal-06","operation":"readiness-markers","role":"be","marker":"be-storage-capacity-ready","alive":true,"decommissioned":false,"non_zero_total_capacity":true}
```

The first two records were emitted only after an authenticated connection to
FE and successful `SHOW BACKENDS;`. The final three records were emitted only
after the matching BE row reported alive true, decommissioned false, and
non-zero total capacity. No `doris-port-unavailable` or
`be-storage-capacity-unavailable` record exists in the stream.

## Scope and conclusion

| Acceptance item | Result |
| --- | --- |
| FE `listener_state` | PASS — `ready` |
| FE `doris-port-ready` | PASS — TCP/SQL listener `9030` |
| BE `listener_state` | PASS — `ready` from FE live backend state |
| BE `doris-port-ready` | PASS — heartbeat service `9050` represented by the live BE row |
| BE `be-storage-capacity-ready` | PASS — alive, not decommissioned, non-zero capacity |
| Private one-off task | PASS |
| Implicit retry | PASS — none |
| Admin refresh or serving mutation | PASS — none performed |
| Terraform/ECR/Databricks operation | PASS — none performed |

This connected checkpoint proves the currently deployed FE/BE listeners and BE
usable storage are ready. It does not claim that old bootstrap logs were
reconstructed, and it does not complete Goal 6. Phase 6-7 admin refresh and all
later acceptance and zero-drift checkpoints remain separately gated.
