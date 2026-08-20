# Goal 6 post-stable-IP listener diagnosis — read-only evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: read-only AWS inspection and diagnosis; no task launch or mutation

## Trigger

The exact stable-private-IP plan
`goal-06-doris-private-ip-remediation-20260814.tfplan` (SHA-256
`5e1cf1ae3be48d2565635da4cd1d73bbb14e3addd90d4ce71ff93511c55729d1`) was
approved and applied as `4 added, 0 changed, 4 destroyed`. The replacement
FE and BE are now running with the reviewed private addresses and the
existing encrypted `/dev/sdf` volumes reattached.

## Durable connected evidence

Read-only EC2 inspection confirms:

| Role | Instance | Private IP | Subnet | Public IP | Platform checks |
| --- | --- | --- | --- | --- | --- |
| FE | `i-07092c079553a0e63` | `10.42.69.177` | `subnet-09bc95f43115dca3e` | none | `ok/ok` |
| BE | `i-0747c1f2e6dd51c1d` | `10.42.77.49` | `subnet-09bc95f43115dca3e` | none | `ok/ok` |

The existing volumes remain intact and attached:

- FE `vol-012bc3410278ed85e` at `/dev/sdf`;
- BE `vol-01e9b0ed05f7b92b9` at `/dev/sdf`.

Read-only EC2 console output then recorded the complete bounded bootstrap
result:

```text
FE: host-prerequisites-ready
FE: private-ip-configured (9030)
FE: bootstrap-started
FE: doris-port-unavailable (9030)

BE: host-prerequisites-ready
BE: private-ip-configured (9050)
BE: bootstrap-started
BE: doris-port-unavailable (9050)
```

The FE marker was emitted at approximately `03:28:04Z` and the BE marker at
approximately `03:28:58Z`; both cloud-init runs reported `scripts-user`
failure. No `doris-port-ready` marker exists. No Goal 6 ECS task, SQL run,
bundle operation, retry, destroy, or additional AWS mutation was performed.

## What the evidence proves

The stable private-IP contract and EC2/network foundation are working. The
failure occurs after the pinned image pull and inside the Doris container
startup/readiness path. It is not evidence of public exposure, subnet/IP
mismatch, or an EC2 platform failure.

The rendered user-data was inspected read-only and contains the expected
`FE_SERVERS`/`FE_ID` contract for FE and `FE_SERVERS`/`BE_ADDR` contract for
BE, the private `priority_networks` configuration, and the local 450-second
listener guard. The official Apache Doris 4.x entrypoint source confirms
those variables are the election-mode startup contract. Therefore a missing
discovery variable is not proven as the current cause.

The host role policy allows the CloudWatch agent to create streams and put
events in the dedicated log group, but no FE/BE host stream appeared. This
means the encrypted-volume `container-diagnostics.log` could not be
independently read through the current log-delivery path; it does not prove
that the container emitted no diagnostics.

## Current diagnosis

**BLOCKED — Doris application listener unavailable; exact container failure is
not independently observable from the approved read-only path.**

The leading hypotheses are:

1. the pinned 4.0.1 container reaches a startup failure or long-running
   initialization while using the persisted FE metadata/BE serving state;
2. the current file-based CloudWatch collection does not deliver the
   encrypted-volume diagnostics, leaving the failure opaque;
3. the bootstrap launch path has no bounded capture around `docker run`, so a
   launch/start failure cannot be separated from a listener timeout.

These are hypotheses, not verified root causes. No metadata or serving-data
volume may be reset based on them.

## Offline remediation implemented for review

The source-only remediation now:

- preserves the image-provided FE/BE base configuration and mounts only
  `fe_custom.conf`/`be_custom.conf` overrides;
- bounds `docker run` with a 120-second timeout and records its output in
  `docker-run.log`;
- distinguishes `container-launch-failed` from a stopped container and the
  final listener timeout;
- configures deterministic CloudWatch paths for status, private-IP,
  container, and Docker-run diagnostics with a five-second flush interval;
- preserves stable private IPs, existing volumes, private security groups,
  and the no-task-before-readiness guard.

No connected operation has been performed for this remediation.

## Required next boundary

Review the offline-only, declarative remediation above and its validation
evidence. A new saved connected development plan may then be created, but it
must be reviewed before any apply. It should contain only the expected FE/BE
bootstrap replacements and no volume reset, IAM/KMS/network/security-group,
public-exposure, task, or production action.

The remediation requirements were:

1. preserve the stable private IPs and both existing volumes;
2. retain the no-public-ingress and no-task-before-readiness gates;
3. make container launch bounded and persist redacted `docker inspect`/
   `docker logs` output even when launch fails;
4. make the CloudWatch collection use explicit diagnostic paths or an
   equivalent deterministic delivery mechanism;
5. avoid changing IAM/KMS/network/security-group scope unless a new plan
   proves it is strictly required;
6. add offline shell/static regression tests and documentation.

No connected Terraform plan/apply/destroy, AWS/Databricks mutation, ECS task,
SQL run, or volume reset is authorized until that remediation is reviewed and
receives its own saved-plan approval.
