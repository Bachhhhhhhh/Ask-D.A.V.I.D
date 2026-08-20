# Goal 6 later-phase verifier image — ECR push

Date: `2026-08-18`

Status: `PASS — EXACT REVIEWED IMAGE PUSHED; ECR BASIC SCAN NOT STARTED`

## Approved artifact

| Property | Value |
| --- | --- |
| Source aggregate SHA-256 | `ecbd7e31c590bc279da57eec328d907517eb95de91a20c9da65eb7352df1b052` |
| Local image ID | `sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510` |
| Repository | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier` |
| Immutable tag | `goal6-later-ecbd7e31` |
| AWS account / region | `736956442295` / `ap-southeast-1` |

Before mutation, the source aggregate, local image ID, AWS identity, region,
repository, immutable tag policy, and tag absence were revalidated. Docker
received its short-lived ECR login password through standard input; no
credential value was printed. Docker logged out immediately after the push.

## Registry result

| Field | Observed value |
| --- | --- |
| Registry digest | `sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510` |
| Digest equality | PASS — registry equals approved local image ID |
| Tag | `goal6-later-ecbd7e31` |
| Media type | `application/vnd.oci.image.index.v1+json` |
| Registry size | `17,890,949` bytes |
| Pushed at | `2026-08-18T17:14:02.937+07:00` |
| Linux/amd64 child manifest | `sha256:41a33747c1bc237f6901b0dac5b52fe2c55ea0781ea48460c696a18f2fc37060` |
| Attestation manifest | `sha256:df77dd45321bf3719c0fd575ab1af5b5fe542476e03f457a4f0c720df956334b` |

Only ECR image/blob upload occurred. No Terraform, ECS task, Doris SQL,
Databricks, Unity Catalog, S3 source-data, IAM, KMS, network, EC2, EBS, public,
or production operation occurred.

## Vulnerability scan evidence

The exact local image was already scanned with Trivy `0.69.3` for fixed
HIGH/CRITICAL vulnerabilities and returned zero findings, as recorded in
`GOAL-06-LATER-PHASE-IMAGE-BUILD-SCAN-2026-08-18.md`.

Immediate ECR inspection returned no scan status/findings for the OCI index or
either child manifest. The registry reports Basic scanning with an empty rule
set. Current AWS documentation states that repositories not matching a Basic
scan-on-push filter use manual scan frequency. Therefore:

- ECR vulnerability scan: `NOT RUN`;
- local exact-image Trivy scan: `PASS`;
- no manual ECR scan was started because the approval allowed only read-only
  scan inspection after the push.

Official references:

- <https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning-basic-enabling.html>
- <https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning-filters.html>

This distinction prevents a false registry-scan PASS claim. The missing ECR
scan does not change the pushed digest and is not a Goal 6 final-acceptance
criterion; the exact artifact still has the durable local security scan.

## Next boundary

The ignored development tfvars and active revision-8 task definitions still
reference the prior image digest. The next separately approved operation is:

1. update only ignored `goal_6_verifier_image` to the registry digest above;
2. run offline preflight;
3. create and review one saved connected development Terraform plan.

The expected managed actions are replacements/registrations of only the two
ECS task definitions `doris-admin-refresh` and `doris-verifier`. No apply or
task execution is authorized by this report.
