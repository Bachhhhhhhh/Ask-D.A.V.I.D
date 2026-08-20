# Goal 6 Doris listener diagnostics — apply evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Authorization: explicit approval to apply the exact saved plan and perform
immediate read-only post-apply inspection

## Applied artifact

```text
infrastructure/environments/development/goal-06-doris-listener-diagnostics-remediation-20260814.tfplan
SHA-256: 8f8c674cbe1fe23141c7aedf376c93e484c0fc3d1a2f3a2d571c584c72285cd6
```

Terraform reported:

```text
Apply complete! Resources: 4 added, 0 changed, 4 destroyed.
```

The apply matched the reviewed plan: FE and BE instances were replaced for
the listener-diagnostics bootstrap, and their existing `/dev/sdf` volume
attachments were re-created for the replacement instance IDs. No task was
run and no SQL, bundle, Databricks, or unrelated AWS operation was performed.

## Read-only post-apply inspection

| Component | Result |
| --- | --- |
| New FE instance | `i-0ce389278aecaf8a6`, `running`, private IPv4 `10.42.69.177` |
| New BE instance | `i-07c6ec23f7cb40476`, `running`, private IPv4 `10.42.77.49` |
| Network placement | Both in `subnet-09bc95f43115dca3e`, VPC `vpc-007ba758b98a9ab9e`, AZ `ap-southeast-1a` |
| Public exposure | Both `PublicIp: null` |
| EC2 system checks | Both `SystemStatus: ok`, `InstanceStatus: ok` |
| FE data volume | `vol-012bc3410278ed85e`, encrypted, 20 GiB, `in-use`, attached to new FE at `/dev/sdf`, `DeleteOnTermination: false` |
| BE data volume | `vol-01e9b0ed05f7b92b9`, encrypted, 50 GiB, `in-use`, attached to new BE at `/dev/sdf`, `DeleteOnTermination: false` |
| Old FE/BE instances | `i-07092c079553a0e63` and `i-0747c1f2e6dd51c1d` are `terminated` and have no private IP |
| Old root volumes | `vol-0054f85536eeb639f` and `vol-00a50e38ba3e3a769` are absent, consistent with the reviewed `delete_on_termination = true` root-device behavior |

The Terraform-managed Goal 6 tags remain present, including `Environment =
development`, `Goal = goal-06`, `ManagedBy = terraform`, and
`DataClassification = synthetic-only`.

## Listener readiness

- FE console output contains `doris-port-ready` for port `9030`.
- BE console output currently contains `host-prerequisites-ready`,
  `private-ip-configured`, and `bootstrap-started` for port `9050`, but no
  `doris-port-ready` or `doris-port-unavailable` marker yet.
- Therefore FE listener readiness is **PASS** and BE listener readiness is
  **UNVERIFIED/PENDING**. This is not evidence of a failure and no retry or
  additional mutation was initiated.
- CloudWatch host streams were not yet present during this immediate check;
  the console output is the current evidence source.

## Checkpoint

The approved instance replacement and private-IP/volume reattachment are
complete and verified. Goal 6 remains blocked at BE application-listener
readiness. A later, separately approved read-only inspection may confirm the
BE marker; no Goal 6 verifier task should run until both FE and BE emit
`doris-port-ready`.
