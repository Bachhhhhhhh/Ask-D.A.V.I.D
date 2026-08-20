# Goal 6 Doris listener post-apply diagnosis

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: read-only post-apply inspection; no repair or retry

## Observed failure

The hash-bound listener-diagnostics plan
`8f8c674bce1fe23141c7aedf376c93e484c0fc3d1a2f3a2d571c584c72285cd6` was
applied successfully. The replacement FE reached `doris-port-ready` on 9030.
The replacement BE (`i-07c6ec23f7cb40476`, private IPv4 `10.42.77.49`) later
emitted:

```text
{"goal":"goal-06","role":"be","status":"doris-port-unavailable","port":"9050"}
```

The marker occurred after the bounded local readiness loop. Cloud-init then
reported that `scripts-user` failed. The EC2 instance remains `running` with
both platform checks `ok`; this is an application/bootstrap failure, not
evidence of an EC2 health or public-network failure. No task, SQL/job, bundle,
Terraform, or ad-hoc AWS repair was run after the failure.

## Read-only evidence inventory

- FE: `i-0ce389278aecaf8a6`, private IPv4 `10.42.69.177`, listener marker PASS.
- BE: `i-07c6ec23f7cb40476`, private IPv4 `10.42.77.49`, listener marker FAIL.
- Existing encrypted role volumes remain attached at `/dev/sdf`; no volume was
  deleted or reformatted.
- The prior persisted-state addresses `10.42.64.238` (FE) and `10.42.71.97`
  (BE) have no current ENI assignment. The selected subnet remains
  `10.42.64.0/20` with 4088 available addresses.
- No FE/BE host CloudWatch stream is present, so container diagnostics cannot
  be independently read from the current log-delivery path. SSM is not
  configured for these instances; no ad-hoc shell access was attempted.

## Diagnosis and boundary

The current bootstrap reaches the host-prerequisite and private-IP checks, and
the FE listener starts. The BE failure is inside the persisted Doris startup
state or container process. Existing durable history records that these same
volumes previously belonged to hosts using `10.42.64.238` and `10.42.71.97`,
while the current deployment uses `10.42.69.177` and `10.42.77.49`. This makes
persisted single-node identity/IP state the leading hypothesis, not a proven
fact; no volume reset or metadata migration is authorized implicitly.

The next permitted action is an offline-only declarative remediation design and
validation that can restore the volume-compatible private IP inputs while
preserving the encrypted volumes and private topology. A new connected plan
and a separate hash-bound approval are required before any instance
replacement, attachment change, or other AWS mutation.
