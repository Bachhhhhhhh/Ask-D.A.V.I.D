# Goal 6 FE listener remediation — connected apply

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: exact hash-bound Terraform apply and immediate read-only inspection

## Approved artifact and execution

The exact saved plan was re-hashed immediately before apply:

```text
goal-06-fe-listener-remediation-20260813.tfplan
SHA-256: 90c504a9e54529d3d4d82e61088455573ab0d02d9ff287df47bc0b6ca7bf83a0
```

AWS identity revalidation passed for account `736956442295` and region
`ap-southeast-1`. Terraform applied only that saved artifact; it did not create
an implicit plan. Result:

```text
Apply complete! Resources: 6 added, 0 changed, 6 destroyed.
```

The first local invocation used an invalid path after `-chdir`, failed before
loading the plan, and performed no AWS operation. The corrected invocation
used the same hash-verified artifact and completed successfully.

## Applied resources

| Area | Result |
| --- | --- |
| FE | Replacement created `i-01415e2378d0e2ca8`, private IP `10.42.78.72`, subnet `subnet-09bc95f43115dca3e`, type `m7i.xlarge`, no public IP |
| BE | Replacement created `i-0e17d80269bc0f208`, private IP `10.42.73.187`, subnet `subnet-09bc95f43115dca3e`, type `m7i.xlarge`, no public IP |
| FE metadata volume | Existing encrypted 20 GiB volume `vol-012bc3410278ed85e` reattached at `/dev/sdf` |
| BE serving volume | Existing encrypted 50 GiB volume `vol-01e9b0ed05f7b92b9` reattached at `/dev/sdf` |
| Admin task definition | `ask-david-development-doris-admin-refresh:4`, `ACTIVE` |
| Read-only verifier task definition | `ask-david-development-doris-verifier:4`, `ACTIVE` |

Both task definitions remain private Fargate `awsvpc` definitions with
`512` CPU / `1024` MiB and use the Terraform-derived replacement FE/BE private
addresses. No task was launched.

## Immediate read-only inspection

| Check | Result |
| --- | --- |
| FE/BE instance state | PASS — both `running` |
| Public exposure | PASS — both `PublicIp=null`; private subnet only |
| EBS encryption/attachments | PASS — both expected volumes `in-use`, encrypted, attached at `/dev/sdf` |
| Task-definition revisions | PASS — revision 4 active with expected commands and digest-pinned image |
| Running Goal 6 ECS tasks | PASS — none |
| Doris security-group ingress | PASS — only documented security-group peers; no public CIDR ingress |
| EC2 platform health | UNVERIFIED at inspection time — both system and instance checks were still `initializing` |
| Doris listener/application health | UNVERIFIED — no task or SQL validation was run |

No IAM, KMS, route, NACL, S3/source-data, Databricks, ECR, production, or
public-exposure change occurred outside the reviewed six replacements.

## Next boundary

This apply does not prove Doris application health or Goal 6 acceptance. The
next step is read-only health inspection followed by a separately approved
private verification-path check and one-off task contract. No ECS task, SQL,
bundle, or retry is authorized by this apply alone.
