# Goal 6 Phase 6-5 root-bootstrap remediation — connected apply

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Saved-plan SHA-256: `81943eb2c58097e074b87f96d57b736767e9ab105c9b8997d3eb7576a28bfe30`

## Authorization and immutable input

The project owner explicitly approved applying the exact saved plan above for
the approved account and region, including replacement of the Backend EC2
instance and a temporary detach/reattach of its existing 50 GiB serving-data
volume at `/dev/sdf`.

Immediately before apply, the artifact hash matched. Read-only AWS identity
verification returned account `736956442295`, principal
`arn:aws:iam::736956442295:user/bach_dev_admin_david`, and region
`ap-southeast-1`.

The host-local Terraform executable and provider cache used to make the saved
plan were absent. Terraform `1.15.8` was restored into `/tmp`; its archive
matched the HashiCorp-published SHA-256. An isolated temporary `TF_DATA_DIR`
was initialized with the existing backend and lockfile, without an upgrade or
new plan. This restored the locked provider versions: AWS `6.56.0`, Databricks
`1.122.0`, and Random `3.9.0`.

## Applied change set

Terraform applied only the approved saved plan:

| Address | Result |
| --- | --- |
| `module.doris_serving.aws_instance.fe[0]` | In-place encrypted root-volume expansion from 8 GiB to 30 GiB; FE identity and private address unchanged. |
| `module.doris_serving.aws_instance.be[0]` | Replaced solely to rerun BE bootstrap generation 2 with a 30 GiB encrypted root volume. |
| `module.doris_serving.aws_volume_attachment.be[0]` | Existing `vol-01e9b0ed05f7b92b9` detached from the terminated BE and reattached at `/dev/sdf` to the replacement BE. |

No new plan was created. No Databricks, IAM, KMS, security-group, network,
S3/source-data, ECS, ECR, metastore, warehouse, production, SQL, bundle, or
task action was performed.

## Read-only post-apply inventory

| Check | Result |
| --- | --- |
| FE | PASS — `i-074e456efa350b444`, running, private `10.42.76.67`, FE SG `sg-019b900ee5601c208`, no public IP; root `vol-010e0af7fe686c7a9` is encrypted 30 GiB. |
| Replacement BE | PASS — `i-0118ff6e619268859`, running, private `10.42.78.119`, BE SG `sg-0a21b2270f7fcd689`, no public IP; encrypted 30 GiB root `vol-0336f432597a6659c`. |
| Previous BE | EXPECTED — `i-05b409f7992294844` is terminated. |
| BE serving-data volume | PASS — encrypted 50 GiB `vol-01e9b0ed05f7b92b9` is `in-use` and attached to the replacement BE at `/dev/sdf`. |
| FE metadata volume | PASS — encrypted 20 GiB `vol-012bc3410278ed85e` remains attached to FE at `/dev/sdf`. |
| Terraform ownership | PASS — FE, replacement BE, and both volume-attachment addresses are present in remote state. |
| EC2 platform checks | PASS — FE and replacement BE system and instance checks are `ok`; no scheduled events. |
| Private exposure | PASS — both instances have no public IP and retain their reviewed private subnet and security groups. |
| BE bootstrap | PASS at bootstrap layer — console output records data-volume recovery/mount, Docker and CloudWatch-agent installation, successful digest-pinned BE image pull, a Docker container ID, and `cloud-init ... finished`. |
| Doris application health | UNVERIFIED — no Doris CloudWatch stream/event is present yet, and no private verifier task or SQL operation was approved or run. |

The original 8 GiB root-volume failure (`no space left on device` while
unpacking the BE image) is not present in the replacement BE console output.

## Current checkpoint and limits

Phase 6-5 infrastructure/bootstrap remediation is applied and partially
verified. The persistent, cost-bearing resources are the two `m7i.xlarge` EC2
instances, their encrypted EBS volumes, NAT egress, CloudWatch log group,
Secrets Manager containers, and KMS usage. No ECS verifier/admin task
definition or ECR verifier image exists because those gates remain disabled.

Do not infer application readiness, FE/BE membership, governed Unity Catalog
integration, or serving correctness from this checkpoint. The next action is a
separately approved connected plan for the intentionally gated verifier-image
and task-definition foundation, followed by separately approved private task
runs. It must not broaden ingress or use an interactive/public path.
