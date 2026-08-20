# Goal 6 Doris intra-cluster connectivity — apply and host-readiness evidence

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Approved saved-plan SHA-256:
`9697f83adeced4944cc9011d7b8b39a8c675d42cfffd7859430e3ba4ecafbb7e`

## Authorization and apply result

Immediately before apply, the saved-plan hash matched, AWS identity resolved to
account `736956442295` and principal
`arn:aws:iam::736956442295:user/bach_dev_admin_david`, the configured region was
`ap-southeast-1`, and the approved Databricks development principal remained
active.

Terraform applied only the reviewed binary saved plan and reported:

```text
Apply complete! Resources: 9 added, 0 changed, 4 destroyed.
```

The five private SG-to-SG rules were created. The four destroy actions were the
delete halves of the reviewed FE/BE EC2 and attachment replacements. No
implicit plan, retry, ECS task, SQL, Databricks mutation, or action outside the
saved plan occurred.

## Replacement host inventory

| Role | Instance | Private IP | Subnet | Type | Public IP | EC2 checks |
| --- | --- | --- | --- | --- | --- | --- |
| FE | `i-0d7b971ba56dc2395` | `10.42.64.238` | `subnet-09bc95f43115dca3e` | `m7i.xlarge` | none | `ok/ok` |
| BE | `i-0dd28df1b1b2c7923` | `10.42.71.97` | `subnet-09bc95f43115dca3e` | `m7i.xlarge` | none | `ok/ok` |

Both use instance profile
`arn:aws:iam::736956442295:instance-profile/ask-david-development-doris-instance`.

The replacement root devices are encrypted 30 GiB gp3 volumes, attached as
`/dev/xvda` with `DeleteOnTermination=true`:

- FE: `vol-0b97a049f281044f7`;
- BE: `vol-0e90cb63371ab8de7`.

The dedicated fresh serving-state volumes were not recreated, resized, or
deleted. Read-only inspection proves they were reattached unchanged as
`/dev/sdf`, encrypted, and `DeleteOnTermination=false`:

- FE: `vol-0e8c9175fe79619be`, 20 GiB, attached to the replacement FE;
- BE: `vol-0b4799bdf2215d397`, 50 GiB, attached to the replacement BE.

No preserved old detached volume was reattached.

## Private network result

Read-only security-group inspection confirmed all five new rules use FE/BE
security-group references and no CIDR:

- BE `sg-0a21b2270f7fcd689` egress to FE
  `sg-019b900ee5601c208` on TCP `9030`;
- FE ingress from BE on TCP `9030`;
- FE egress to BE on TCP `9050`, `9060`, and `8060`.

The existing matching BE ingress rules remain in place. Neither replacement
host has a public IP.

## Deterministic listener evidence

Evidence was retrieved read-only through EC2 serial-console output and bound to
the replacement instance IDs. No interactive host session or SSM access was
used.

FE `i-0d7b971ba56dc2395` emitted, in order:

```text
bootstrap-invoked
host-prerequisites-ready
private-ip-configured (9030)
bootstrap-started
container-diagnostics-summary listener_state=starting container_state=running running=true exit_code=0
container-diagnostics-summary listener_state=ready container_state=running running=true exit_code=0
doris-port-ready (9030)
cloud-init finished
```

The FE ready marker occurred at boot time `108.031256` seconds. Deterministic
counts were `FE_READY=1`, `FE_TERMINAL_FAILURES=0`, and
`FE_CLOUD_INIT_FINISHED=1`.

BE `i-0dd28df1b1b2c7923` emitted, in order:

```text
bootstrap-invoked
host-prerequisites-ready
private-ip-configured (9050)
fe-registration-port-waiting (9030)
fe-registration-port-ready (9030)
bootstrap-started
container-diagnostics-summary listener_state=starting container_state=running running=true exit_code=0
container-diagnostics-summary listener_state=ready container_state=running running=true exit_code=0
doris-port-ready (9050)
cloud-init finished
```

The BE registration-ready marker occurred at boot time `90.385430` seconds and
the BE ready marker at `157.491280` seconds. Deterministic counts were
`BE_REGISTRATION_READY=1`, `BE_READY=1`, `BE_TERMINAL_FAILURES=0`, and
`BE_CLOUD_INIT_FINISHED=1`.

The redacted `log_signal` classifier still matches ordinary words such as
`configuration` or `bind` in the bounded log tail. It is not a terminal health
signal. The explicit `listener_state=ready`, running container state, exit code
zero, local socket marker, and absence of every terminal failure marker are the
authoritative bootstrap result.

## Logging observation

The CloudWatch agent installed, accepted its generated configuration, and was
enabled on both hosts according to serial-console output. No host-specific
CloudWatch stream for either new instance ID was visible during the immediate
post-apply inspection. Therefore this report does **not** claim that dedicated
host file-stream delivery passed. The instance-bound serial-console output is
the durable host-readiness evidence for this checkpoint.

The existing `/ask-david-development/doris` log group and earlier ECS admin
task streams remain present. Phase 6-6 must still retrieve verifier evidence
through its approved CloudWatch task log path; it must not depend on direct
Codex connectivity or SSM.

## Checkpoint

| Check | Result |
| --- | --- |
| Exact saved-plan apply | PASS |
| Expected private SG rules | PASS |
| No public host exposure | PASS |
| Same dedicated data volumes reattached | PASS |
| EC2 system/instance health | PASS |
| FE process/listener `9030` | PASS |
| BE-to-FE registration path `9030` | PASS |
| BE process/listener `9050` | PASS |
| Terminal bootstrap failure markers absent | PASS |
| Dedicated host CloudWatch file streams | UNVERIFIED — not observed immediately after apply |
| Private ECS verifier task | NOT RUN — requires separate approval |

Phase 6-5 host readiness is verified. Goal 6 as a whole remains in progress;
Phase 6-6 private verification-path validation is the next approval boundary.
