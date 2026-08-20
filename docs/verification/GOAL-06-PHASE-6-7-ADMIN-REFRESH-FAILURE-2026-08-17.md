# Goal 6 Phase 6-7 admin-refresh attempt — stopped without retry

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **FAILED — DECLARATIVE SQL REMEDIATION REQUIRED; NO RETRY**

## Scope and approval

The project owner approved exactly one private Fargate execution of the
already-reviewed admin-refresh task. Its purpose was limited to the first
governed Unity Catalog Iceberg REST read and creation/refresh of disposable
internal Doris serving state. It was not approval for a retry, a Terraform
operation, a Databricks control-plane operation, or any change to AWS
infrastructure.

## Pre-run contract

Read-only inspection immediately before launch recorded:

| Control | Observed value | Result |
| --- | --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` | PASS |
| Task definition | `ask-david-development-doris-admin-refresh:7` | PASS |
| Runtime | Fargate, `awsvpc`, CPU `512`, memory `1024` | PASS |
| Image | digest-pinned `doris-verifier@sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6` | PASS |
| Default command | `/app/doris-admin-refresh` | PASS |
| Existing running admin tasks | none | PASS |
| Network | approved private application subnets; `assignPublicIp=DISABLED` | PASS |
| Admin task SG | `sg-07a0dd2e8af8aa178`; TCP/9030 only to FE SG and TCP/443 egress for approved HTTPS endpoints | PASS |
| Hosts | FE `10.42.64.238`, BE `10.42.71.97`; private and EC2 `ok/ok` | PASS |

No command override was used. The task therefore executed only the
task-definition's reviewed default runner.

## One-task result

ECS launched exactly one task:

```text
arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/8179ca7fd66343d597a283ba02877e7e
```

It received private ENI `eni-0625edeb22112eef0` in approved subnet
`subnet-0a1aad220d82ef879`, private address `10.42.38.44`, and no public
address. It started at `2026-08-17T15:05:12+07:00` and stopped at
`2026-08-17T15:05:36+07:00` with:

| ECS field | Value |
| --- | --- |
| Last status | `STOPPED` |
| Stop code | `EssentialContainerExited` |
| Container exit code | `1` |
| Image digest | `sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6` |
| Task ENI after stop | deleted |

The task did **not** emit the approved non-sensitive
`{"goal":"goal-06","operation":"admin-refresh","status":"completed"}`
marker. No retry was launched.

## Exact failure classification

The CloudWatch stream is
`admin/doris-admin/8179ca7fd66343d597a283ba02877e7e`. Initial inspection was
restricted to counts for fixed signatures to avoid retrieving confidential
source or credential-adjacent details. It found one generic `ERROR` event and
zero events containing each of:

- `invalid-workspace-origin`;
- `source-not-allowlisted`;
- `Access denied`;
- `curl:`;
- `completed`.

After explicit owner approval, inspection retrieved only that one `ERROR`
event. Its complete message was a non-secret Doris SQL diagnostic:

```text
ERROR 1105 (HY000) at line 2: errCode = 2, detailMessage = ADMIN_PRIV and NODE_PRIV can only be granted/revoke on/from *.*.*
```

The runner currently creates its restricted admin user with:

```sql
GRANT ADMIN_PRIV ON *.* TO '<admin-user>'@'%';
```

That is a deterministic syntax/scope mismatch for the deployed Doris 4.0.1
authorization model. The official Doris 4.x `GRANT` reference defines global
privileges at `*.*.*`, and explicitly identifies `ADMIN_PRIV` and `NODE_PRIV`
as global-only privileges. The runner failed before it could use the named
admin identity, add the BE, construct the temporary Unity Catalog catalog,
request OAuth, read the lakehouse, or create/refresh serving objects.

This proves neither a governed external read nor any Phase 6-7 acceptance
criterion. It proves only that this observed task failure occurred before the
runner reached the later network, S3, KMS, Databricks OAuth, Unity Catalog, or
source-data stages; those stages remain unverified rather than ruled out.

## Required next boundary

The smallest declarative remediation was implemented offline: the admin grant
in `docker/doris-verifier/doris-admin-refresh` now uses `ON *.*.*`; a focused
regression assertion and a fail-closed static-validator rule reject the prior
two-level form; the plan and runbook record the global-scope contract. It does
not change IAM, KMS, network, secret references, task definitions,
source-table permissions, or execution behavior.

Offline validation passed:

| Check | Result |
| --- | --- |
| `sh -n docker/doris-verifier/doris-admin-refresh` | PASS |
| `python3 scripts/validate_goal6.py` | PASS |
| `pytest -q -p no:cacheprovider -o addopts='' tests/unit/test_goal6_static.py` | PASS — 21 tests |
| `python3 -m compileall -q scripts/validate_goal6.py` | PASS |
| `git diff --check` | PASS |

`ruff` is not installed in the current local environment, so its check and
format gates are **UNVERIFIED** rather than inferred. No formatter was used to
change source.

## Local image build checkpoint

The deterministic image source aggregate is
`ad0056f26ac2901410075224e57ae1406c5cfe2405e6374280bf44dbb1dd423b`, over
`docker/Dockerfile.doris-verifier`, `docker/doris-verifier/**`, and `doris/**`.
Two local `docker build --pull --no-cache` attempts for tag
`ask-david-doris-verifier:goal6-admin-priv-ad0056f2` did not produce a local
image. Both outputs stopped while the Alpine build step fetched the community
APK index; read-only Docker inspection found no resulting image and no running
build container. The captured evidence does not establish a root cause, so it
is recorded as **BUILD/SCAN UNVERIFIED**, not as a source or cloud failure.

The one explicitly approved host-networked local build/scan attempt succeeded:
source aggregate `ad0056f26ac2901410075224e57ae1406c5cfe2405e6374280bf44dbb1dd423b`
produced local image ID
`sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad`.
It has the non-root and corrected-grant contracts, and Trivy 0.69.3 found zero
HIGH/CRITICAL vulnerabilities. No ECR login/push, Terraform, AWS
control-plane action, Databricks action, task-definition update, or task retry
was performed. Evidence:
`docs/verification/GOAL-06-ADMIN-PRIV-GRANT-IMAGE-BUILD-SCAN-2026-08-17.md`.

A separately approved ECR push, task-definition revision, and task-run remain
required before any Phase 6-7 result may be claimed.
