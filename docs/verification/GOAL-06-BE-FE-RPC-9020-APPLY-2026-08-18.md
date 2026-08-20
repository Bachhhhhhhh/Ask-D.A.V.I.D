# Goal 6 BE-to-FE RPC 9020 remediation — apply evidence

Date: 2026-08-18

Environment: development (`736956442295`, `ap-southeast-1`)

Status: exact saved plan applied successfully; network remediation PASS.
Direct Doris BE capacity evidence remains UNVERIFIED. No ECS task, SQL
operation, EC2 replacement, volume operation, Databricks mutation, public
exposure, or production action occurred.

## Approved artifact

- saved plan:
  `/tmp/ask-david-goal6-rpc-9020-plan.DGzllw/goal-06-be-fe-rpc-9020-20260818.tfplan`;
- SHA-256:
  `2e5d7aaa4889fd90865f312c3659f6ce1f41cc6a82dde8d8a3faecb56fb9ae4b`;
- AWS account: `736956442295`;
- region: `ap-southeast-1`.

Immediately before apply, fail-closed checks reconfirmed the exact account,
region, artifact hash, temporary Terraform data directory, two-resource
address allowlist, create-only action set, and exact TCP `9020` bounds. No
implicit replacement plan was generated.

## Apply result

Terraform completed:

```text
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```

Created resources:

| Rule ID | Direction | Source | Destination | Protocol/port |
| --- | --- | --- | --- | --- |
| `sgr-092a7ed0c879d5bea` | egress | BE SG `sg-0a21b2270f7fcd689` | FE SG `sg-019b900ee5601c208` | TCP `9020` |
| `sgr-09b2940215ba4691b` | ingress | BE SG `sg-0a21b2270f7fcd689` | FE SG `sg-019b900ee5601c208` | TCP `9020` |

Read-only CloudTrail inspection places both authorization events at
`2026-08-18T08:24:18Z` (`15:24:18+07:00`).

## Immediate post-apply inspection

AWS SG inspection confirms both exact rule IDs, directions, referenced groups,
TCP protocol, and `9020`-only bounds.

EC2 platform status:

- FE `i-0959fcc02513accb6`: `running`, system `ok`, instance `ok`, no event;
- BE `i-00ee935abe7df116f`: `running`, system `ok`, instance `ok`, no event.

No host was replaced or restarted by this apply.

Immediate ECS inspection returned empty `RUNNING` task lists for both
`ask-david-development-doris-admin-refresh` and
`ask-david-development-doris-verifier`.

## Deterministic flow evidence

VPC Flow Logs provide a before/after distinction:

- historical BE `10.42.71.97` to FE `10.42.64.238:9020` records ending at
  `08:00:23Z` are `REJECT OK`;
- the first post-apply record starts at `08:24:25Z`, seven seconds after both
  rule creates, and is `ACCEPT OK`;
- subsequent records contain BE-to-FE requests and FE-to-BE responses with
  non-zero packet/byte counts on multiple source connections.

This proves the exact private RPC network path is now authorized and actively
used. No CIDR or public path is involved.

## Remaining verification boundary

The dedicated Doris CloudWatch log group currently contains ECS task streams
only; it has no FE/BE host stream. EC2 serial console output contains no
post-apply Doris callback or capacity record. Therefore the following must not
be inferred from SG/flow evidence alone:

- all four BE callback error families have ceased at the application layer;
- the FE now reports the BE alive, non-decommissioned, and with non-zero total
  capacity;
- `be-storage-capacity-ready` acceptance is satisfied.

Those items remain UNVERIFIED. A separately approved, bounded, private,
non-mutating diagnostic may query FE state and emit sanitized evidence through
CloudWatch. No admin refresh, serving mutation, or automatic retry is
authorized by this apply.

## Negative-action result

- update/replacement/destroy: zero;
- EC2/user-data/EBS/attachment action: zero;
- IAM/KMS/ECS/task-definition/Databricks action: zero;
- public/production/unrelated action: zero;
- ECS task or SQL run: zero.
