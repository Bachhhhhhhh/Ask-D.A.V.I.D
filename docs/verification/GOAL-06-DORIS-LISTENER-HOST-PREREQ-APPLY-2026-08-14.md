# Goal 6 Doris listener host-prerequisite remediation — apply evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: exact approved saved-plan apply and immediate read-only inspection

## Approval and integrity

The exact saved plan was revalidated immediately before apply:

```text
goal-06-doris-listener-host-prereq-remediation-20260814.tfplan
SHA-256: bbe5e504b136fd639995c033d90afecf3a557fb430dbd3a1f194f29e5b7a0bbd
```

AWS identity was revalidated as account `736956442295` and region
`ap-southeast-1`. No replacement plan was generated.

## Apply result

Terraform completed exactly:

```text
Apply complete! Resources: 6 added, 0 changed, 6 destroyed.
```

The six approved replacements were the FE and BE EC2 instances, their two
volume attachments, and the two Goal 6 ECS task definitions. No standalone
serving-data volume was deleted. No IAM, KMS, security-group, route/NACL, S3,
ECR, Secrets Manager, Databricks, production, or public-exposure action
occurred.

## Immediate read-only inspection

| Check | Result |
| --- | --- |
| FE instance | `i-0ad90219f868841f7`, private `10.42.69.177`, no public IP, running |
| BE instance | `i-0dc0e8f4f71d1876e`, private `10.42.77.49`, no public IP, running |
| FE role volume | `vol-012bc3410278ed85e`, encrypted 20 GiB, `/dev/sdf`, attached to new FE |
| BE role volume | `vol-01e9b0ed05f7b92b9`, encrypted 50 GiB, `/dev/sdf`, attached to new BE |
| EC2 platform checks | FE and BE `ok/ok` |
| Admin task definition | revision `6`, `ACTIVE`, private Fargate, pinned verifier image |
| Verifier task definition | revision `6`, `ACTIVE`, private Fargate, pinned verifier image |
| Running Goal 6 tasks | none |
| Terraform state ownership | new FE/BE, attachments, and task definitions present in remote state |

## Doris readiness result

Both hosts emitted the new host-prerequisite marker and completed the pinned
image pull:

```text
FE: host-prerequisites-ready; bootstrap-started
BE: host-prerequisites-ready; bootstrap-started
```

The local readiness guard then failed on both hosts:

```text
FE: {"goal":"goal-06","role":"fe","status":"doris-port-unavailable","port":"9030"}
BE: {"goal":"goal-06","role":"be","status":"doris-port-unavailable","port":"9050"}
```

Cloud-init reported `scripts-user` failure for both instances. No dedicated
FE/BE CloudWatch log stream appeared, so `doris-port-ready` is not verified.
The readiness evidence is application-failure evidence, not a network or EC2
platform failure. No ECS task was launched or retried.

## Current checkpoint

The approved infrastructure remediation applied successfully and the host
prerequisites were reached, but Doris FE/BE query listeners remain unavailable.
Goal 6 is still blocked before any verifier task. The next work must be a new
offline diagnosis/remediation based on the persisted failure evidence; no
connected retry, task launch, destroy, or ad-hoc shell is authorized.
