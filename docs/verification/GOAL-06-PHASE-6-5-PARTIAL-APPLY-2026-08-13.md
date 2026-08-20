# Goal 6 Phase 6-5 partial foundation apply

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Result: **STOPPED — bootstrap failure; state reconciliation no longer required**

## Approved action

Terraform applied the reviewed foundation artifact with SHA-256
`71c98b16a8531ac49a64cd789933e174c207cf610d28e74a39cd8347f6ebbddc`.
No replacement, destroy, ECR image push, bundle deployment, SQL execution, or
ECS task run was authorized.

## Read-only post-apply evidence

The first post-apply inspection found a Terraform-state ownership discrepancy
for three serving resources:

| Resource | AWS state | Terraform state ownership | Notes |
| --- | --- | --- | --- |
| BE instance `i-05b409f7992294844` | Running, private `10.42.64.254` | Present | `m7i.xlarge`, backend role |
| FE instance `i-074e456efa350b444` | Running, private `10.42.76.67` | **Absent** | `m7i.xlarge`, frontend role |
| BE data volume `vol-01e9b0ed05f7b92b9` | Encrypted 50 GiB gp3, attached | Volume present; attachment absent | Attached at `/dev/sdf` to BE |
| FE metadata volume `vol-012bc3410278ed85e` | Encrypted 20 GiB gp3, attached | Volume present; attachment absent | Attached at `/dev/sdf` to FE |

The exact final Terraform diagnostic was not durably recoverable from the
execution transport because its output ended after resource creation. The
initial state/AWS discrepancy nevertheless correctly stopped all mutation.

### Subsequent state-reconciliation evidence

A separately approved, saved connected reconciliation plan was created on
`2026-08-13` after the three configuration-driven import blocks had been
implemented and offline validated. Its ignored local artifact SHA-256 is:

```text
318a8b1d8b7693d002e8019c3db82fdca2ee7abe93473112a0e20f056da54481
```

The plan contains 245 `no-op` changes and **zero** import, create, update,
replace, or destroy actions. Read-only remote-state inspection now shows all
three previously missing addresses with the exact expected identities:

| Terraform address | State identity |
| --- | --- |
| `module.doris_serving.aws_instance.fe[0]` | `i-074e456efa350b444` |
| `module.doris_serving.aws_volume_attachment.fe[0]` | `vai-3021515803` → `/dev/sdf:vol-012bc3410278ed85e:i-074e456efa350b444` |
| `module.doris_serving.aws_volume_attachment.be[0]` | `vai-3572161323` → `/dev/sdf:vol-01e9b0ed05f7b92b9:i-05b409f7992294844` |

No reconciliation apply was requested or performed because the reviewed
artifact was a complete no-op, rather than the expected three imports. This
resolves the state-ownership concern but does not prove Doris health.

### Security and lifecycle inspection

- Both EC2 instances are in the approved private data subnet
  `subnet-09bc95f43115dca3e`; both have `PublicIp = null`.
- A later read-only EC2 inspection found both instances `running` with EC2
  instance and system checks `ok`, no scheduled events, and the intended
  instance profile. This is only EC2 health, not Doris application health.
- FE/BE ingress rules reference only dedicated security groups and documented
  ports. No ingress rule uses a public CIDR.
- The only public-CIDR rules are reviewed private-subnet TCP/443 egress through
  existing NAT for AWS/Databricks endpoints; they are not public exposure.
- The verifier ECR repository exists and contains zero images. No Goal 6 ECS
  task definition exists.
- The KMS-encrypted Doris CloudWatch log group exists with a 30-day retention,
  but has no log stream or stored events. No log contents were read.
- The dedicated Databricks Doris external-read service principal exists with
  workspace access. Its OAuth material is stored in the exact Secrets Manager
  container; no secret value was retrieved or recorded.

## Cost-bearing partial resources

Costs are now accruing for the two running `m7i.xlarge` instances, their root
volumes and 20/50 GiB data volumes, CloudWatch Logs, KMS requests, Secrets
Manager containers, ECR storage if an image is later pushed, and private-NAT
data processing. There are no running Fargate tasks.

## Exact bootstrap failure recovered from EC2 console evidence

Read-only filtered EC2 console output recovered the operational failure that
was not present in the Terraform transport output. The FE completed its
bootstrap and started its pinned container. The BE bootstrap failed while
Docker unpacked the pinned Doris BE image:

```text
docker: failed to register layer: write
/opt/apache-doris/be/lib/java_extensions/hadoop-hudi-scanner/
hadoop-hudi-scanner-jar-with-dependencies.jar: no space left on device.
```

Both AMI-created root EBS volumes are encrypted `gp3` volumes of only 8 GiB.
The dedicated 20 GiB FE metadata and 50 GiB BE serving-data volumes are
separate, encrypted, attached, and healthy; they do not provide Docker's root
filesystem space. The BE therefore has no healthy Doris process, and the
two-node Doris deployment is **not healthy/verified**.

## Required stop and next decision

No retry, new plan, replacement, cleanup, task launch, or integration action
was performed. The safe next direction must be approved explicitly:

1. implement and offline-validate a minimal Terraform-managed bootstrap
   remediation: declare an adequate encrypted root-volume size and arrange a
   controlled BE re-bootstrap. Because the failed cloud-init user-data script
   will not re-run merely from an online EBS resize, the follow-up saved plan
   must explicitly disclose any BE replacement and volume-attachment action;
   or
2. design and review Terraform-managed cleanup of the partial serving
   resources, then create a new saved plan.

Until one option is approved, Goal 6 remains partially verified and no Doris,
Unity Catalog, refresh, or verifier execution may proceed.
