# Goal 6 Phase 6-13 audit-guard image — ECR promotion

Date: `2026-08-19`

Status: **PASS — EXACT SCANNED IMAGE PUSHED; NOT DEPLOYED OR EXECUTED**

## Approved boundary

This checkpoint promoted exactly one previously scanned local image to the
private development ECR repository and performed immediate read-only digest
inspection. No Terraform, ECS task-definition, ECS task, Doris SQL,
Databricks, or unrelated AWS resource operation occurred.

## Approved artifact and destination

| Attribute | Value |
| --- | --- |
| Source aggregate | `25b48aea6cbedb2f901b7e959d788fed2f4bc79ece65f49b43efc33f7634907c` |
| Scanned local OCI image/index digest | `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| Repository | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier` |
| Immutable tag | `goal6-audit-guards-25b48aea` |

## Fail-closed preflight

Before authentication and push, read-only checks confirmed:

- AWS account was `736956442295`;
- region was `ap-southeast-1`;
- repository URI matched the approved private development repository;
- tag mutability was `IMMUTABLE`;
- scan-on-push was enabled; and
- the destination tag was absent (`ImageNotFoundException`), so no immutable
  tag overwrite was possible.

The local image digest was reverified against the approved scanned digest.
Docker received the short-lived ECR login password only through stdin and
logged out immediately after the push.

## Registry result

| Attribute | Result |
| --- | --- |
| Remote digest | `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |
| Local/remote digest equality | **PASS** |
| Manifest media type | `application/vnd.oci.image.index.v1+json` |
| ECR compressed image size | `17,893,335` bytes |

The registry image-scan status was not returned (`None`) immediately after the
push. It is therefore **UNVERIFIED/NOT RUN**, not a vulnerability-scan PASS;
the exact local Trivy scan remains the authoritative available scan evidence
with zero HIGH/CRITICAL findings.

## Next approval boundary

The active revision-15 admin-refresh and verifier task definitions remain on
the prior image. A separate approval is required to update only the ignored
development image input, run offline preflight, and create/review one saved
connected Terraform plan whose only actions are the two Goal 6 task-definition
replacements. No apply or task execution is authorized by this report.
