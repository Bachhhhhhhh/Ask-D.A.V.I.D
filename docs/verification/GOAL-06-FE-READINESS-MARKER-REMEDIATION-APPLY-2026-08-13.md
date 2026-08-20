# Goal 6 FE readiness-marker remediation — apply evidence

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: exact approved saved-plan apply and immediate read-only inspection

## Approval and integrity

The exact saved plan
`goal-06-fe-readiness-marker-remediation-20260813.tfplan` was hash-verified
before apply:

```text
07a9efc1f932b2eabc48216aef89cc476f0f6cfbc582a5a3d83b13b69f5349a6
```

The caller was verified in AWS account `736956442295`; the configured region
was `ap-southeast-1`. No replacement plan was generated.

## Apply result

Terraform completed exactly:

```text
Apply complete! Resources: 6 added, 0 changed, 6 destroyed.
```

The approved six replacements were the FE and BE instances, their two volume
attachments, and the two Goal 6 ECS task definitions. No standalone volume was
deleted. No IAM, KMS, security-group, route/NACL, S3, ECR, Secrets Manager,
Databricks, production, or public-exposure action occurred.

## Immediate read-only inspection

| Check | Result |
| --- | --- |
| FE instance | `i-0fe26c51fd499b7de`, private `10.42.64.238`, no public IP, running |
| BE instance | `i-07d1e1eddfec1c9eb`, private `10.42.71.97`, no public IP, running |
| FE role volume | `vol-012bc3410278ed85e`, encrypted, `/dev/sdf`, in-use by new FE |
| BE role volume | `vol-01e9b0ed05f7b92b9`, encrypted, `/dev/sdf`, in-use by new BE |
| Task definitions | Admin and verifier revision `5`, `ACTIVE`, pinned MariaDB-compatible image |
| Running Goal 6 tasks | None |
| EC2 health after bootstrap | FE `ok/ok`; BE `ok/ok` |
| Marker log streams | None visible for the new instance IDs |

The absence of CloudWatch streams is not by itself treated as a readiness
failure because the EC2 console output is authoritative for the bootstrap
markers. No task was launched or retried.

## Final readiness result

The persisted console markers later showed:

```text
FE: {"goal":"goal-06","role":"fe","status":"doris-port-unavailable","port":"9030"}
BE: {"goal":"goal-06","role":"be","status":"doris-port-unavailable","port":"9050"}
```

Both markers were emitted after the 90-iteration local readiness guard and
cloud-init reported `scripts-user` failure. Neither host reached
`doris-port-ready`. No ECS task was launched or retried.

## Current checkpoint

The approved infrastructure apply is complete, but Goal 6 remains blocked:
both persisted readiness markers prove that the FE/BE query ports were
unavailable. A new offline diagnosis/remediation is required before another
connected plan or any one-off private task. No retry was made.
