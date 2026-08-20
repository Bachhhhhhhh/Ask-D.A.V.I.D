# Goal 6 private verifier FE health command failure

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **PARTIALLY VERIFIED — FE LISTENER REACHABILITY PASS; NO RETRY**

## Approved execution and scope

The project owner approved one private Fargate FE health task from
`ask-david-development-doris-verifier:7`, using the two approved application
subnets, verifier security group `sg-04eb1ebf613ceeadc`, and
`assignPublicIp=DISABLED`. Its sole intended action was a bounded, non-mutating
MariaDB TLS health ping to FE `10.42.64.238:9030`.

No serving query, admin refresh, SQL mutation, Terraform operation, ECR
operation, Databricks operation, or retry was approved or performed.

## Pre-run evidence

Read-only inspection reconfirmed the approved account, region, cluster,
active Fargate task-definition revision, private application subnets, verifier
security group, immutable image digest, and FE host health. The preceding
endpoint remediation had already added the least-privilege verifier-SG to
interface-endpoint-SG TCP/443 rule, with no CIDR ingress.

## One-task result

ECS launched exactly one task:

```text
arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/ee65c772bda64d76b74de112c456bedc
```

The task used private ENI `eni-068b6ab6e6a58d117` in approved application
subnet `subnet-034f5f1c9bca753f1`, with private address `10.42.28.94`; no
public association was reported. It stopped with `EssentialContainerExited`
and exit code `2`.

The task's sanitized CloudWatch output was:

```text
/bin/sh: line 3: syntax error: unexpected word (expecting ")")
```

## Deterministic cause

The image/task definition has `ENTRYPOINT ["/bin/sh"]`. The approved task
override also supplied `/bin/sh -c <health command>`. ECS consequently invoked
the equivalent of:

```text
/bin/sh /bin/sh -c <health command>
```

The first shell interpreted the second shell path as an input script and
terminated before `mysqladmin` started. This is a command-vector composition
defect, not a SQL error, FE-listener result, permission expansion, public
network requirement, or renewed Secrets Manager failure.

The container reached execution and emitted a CloudWatch stream, so the prior
secret-injection failure is no longer the observed blocker. This does **not**
prove that FE port `9030` is reachable; the approved health command never ran.

## Approved offline remediation

The project owner approved source/tests/docs remediation only. The repository
adds `infrastructure/scripts/run-goal6-fe-health.ps1`, a fail-closed wrapper
that verifies the exact private Fargate task contract and sends only
`[-c, <bounded mysqladmin TLS ping>]` to the existing `/bin/sh` entrypoint.
It rejects the previous double-shell vector, performs no SQL, and never retries
a failed task. Static validation and regression coverage are required before a
new, separately approved single health task may run.

No new image, ECR push, task-definition revision, Terraform plan/apply, or AWS
mutation is part of this remediation.

## ECS entrypoint inspection correction

The first read-only pre-run inspection after that remediation found that ECS
`DescribeTaskDefinition` correctly reports `entryPoint: null` for revision 7:
the task definition does not override the image entrypoint. This was initially
treated incorrectly as a mismatch, so the wrapper would have stopped before
`RunTask`. No task was launched.

Read-only local Docker metadata for the exact reviewed image ID reports
`ENTRYPOINT ["/bin/sh"]` and no image `CMD`; its pinned ECR digest is already
bound by the wrapper. The approved follow-up offline correction therefore
requires null ECS `entryPoint` (preventing a task-definition override) while
retaining the immutable image binding and the source-validated Docker entrypoint
contract. It still passes exactly `[-c, <bounded mysqladmin TLS ping>]`. The
full offline validation set below was rerun after this correction and passed.

## Offline validation

The approved source/tests/docs change was validated without any cloud call:

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| `pytest -q -p no:cacheprovider -o addopts='' tests/unit/test_goal6_static.py` | PASS — 20 tests |
| `terraform fmt -check -recursive infrastructure` | PASS — run outside the Snap-confined sandbox; formatting check only |
| `python3 -m compileall -q scripts/validate_goal6.py` | PASS |
| `git diff --check` | PASS |

PowerShell is not installed in this offline environment, so an actual
PowerShell parser execution is **UNVERIFIED**. Static regression coverage
inspects the wrapper's exact entrypoint guard, private-network shape, command
vector, non-query client command, no-retry handling, and CloudWatch success
marker.

## Next approval boundary

The corrected health task was separately approved and launched exactly once:

```text
arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/f90b1e0ac7c342bfa4fcb4473f33c7cb
```

It used private ENI `eni-0235da75a9ade9b4b` in approved subnet
`subnet-0a1aad220d82ef879`, private IPv4 `10.42.39.89`, verifier SG
`sg-04eb1ebf613ceeadc`, and no public association. The task stopped normally
with `EssentialContainerExited`, exit code `0`, and the reviewed `[-c,
<bounded ping>]` override.

CloudWatch emitted a MariaDB TLS client warning followed by:

```text
mysqladmin: connect to server at '10.42.64.238' failed
error: 'Access denied for user 'UNKNOWN_USER@10.42.39.89' (using password: YES)'
```

An authentication-denied MariaDB server response can occur only after the
private TCP/TLS connection reaches the FE listener. Together with exit `0`, it
is PASS evidence for Phase 6-6 listener reachability and denied anonymous
access. It does not prove the future query identity or serving SQL; those are
later phases. No retry was launched.

The approved offline evidence-contract update accepts either `mysqld is alive`
or this expected authentication-denied response after exit `0`, while rejecting
timeouts, refusals, missing CloudWatch evidence, non-zero exits, and every
other task failure. The full offline validation set below was rerun after this
evidence-contract update and passed. No task is implicitly authorized.
