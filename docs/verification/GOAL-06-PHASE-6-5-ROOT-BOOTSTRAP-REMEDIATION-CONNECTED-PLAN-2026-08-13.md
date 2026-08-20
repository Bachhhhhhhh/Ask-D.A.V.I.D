# Goal 6 Phase 6-5 root-bootstrap remediation — connected saved plan

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Phase: saved-plan review; no apply

## Read-only revalidation

| Prerequisite | Result |
| --- | --- |
| AWS identity | PASS — `arn:aws:iam::736956442295:user/bach_dev_admin_david` |
| AWS region | PASS — `ap-southeast-1` |
| Databricks development identity | PASS — active principal `bachvxuan@gmail.com` |
| Unity Catalog metastore | PASS — `3a7f7e7a-680b-4bd6-907a-6d5e77b43178` |
| Foundation gates | PASS — Goal 5 source retention and Goal 6 foundation enabled; verifier task definitions disabled |

## Saved plan

Ignored local artifact:

```text
infrastructure/environments/development/goal-06-root-bootstrap-remediation-20260813.tfplan
```

SHA-256:

```text
81943eb2c58097e074b87f96d57b736767e9ab105c9b8997d3eb7576a28bfe30
```

The exact plan has 242 no-op resources and three non-no-op resource changes:

| Terraform address | Action | Reviewed effect |
| --- | --- | --- |
| `module.doris_serving.aws_instance.fe[0]` | update in place | encrypted root volume size `8 → 30 GiB`; same subnet, SG, instance profile, and `associate_public_ip_address=false` |
| `module.doris_serving.aws_instance.be[0]` | replace | root volume `8 → 30 GiB`; replacement is caused only by `user_data` generation `2`; same subnet, SG, instance profile, and no public IP |
| `module.doris_serving.aws_volume_attachment.be[0]` | replace | detach/reattach the **same** existing BE serving-data volume `vol-01e9b0ed05f7b92b9` at the same `/dev/sdf` device to the replacement BE |

The replacement actions are the paired delete/create actions for the BE
instance and its attachment; they are not an unreviewed deletion of the BE
serving-data volume. There are zero Databricks, IAM, KMS, security-group,
network, S3/source-data, ECS, ECR, metastore, warehouse, production, or public
exposure actions.

No saved plan was applied. No ECR image push, ECS task launch, bundle deployment,
SQL/job run, or source-data mutation occurred.

## Required next approval

Apply only the hash-bound artifact above after re-verifying the approved AWS
account and region. The apply will deliberately replace the failed BE and
temporarily detach then reattach its existing disposable serving-data volume.
If the apply fails, stop and perform only the required read-only inventory;
do not retry, destroy, or repair out of band.
