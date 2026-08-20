# Goal 6 Phase 6-12 query-limit image — ECR promotion

Date: `2026-08-19`

Status: `PASS — IMMUTABLE IMAGE PUSHED; NOT DEPLOYED OR EXECUTED`

## Approved boundary

The approved operation was limited to AWS identity revalidation, Docker ECR
authentication, pushing one exact scanned local image, logging out, and
read-only registry inspection. No Terraform, ECS task-definition change, ECS
task, Doris SQL, Databricks operation, or unrelated AWS mutation was performed.

## Exact artifact

| Attribute | Result |
| --- | --- |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| Repository | `ask-david-development/doris-verifier` |
| Source aggregate | `a4a0f4fd3a003fadd1a9e7ce48c9d3a75dfdf183768dc593df2fbc40847d4b84` |
| Local image digest | `sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36` |
| Immutable tag | `goal6-query-limit-a4a0f4fd` |
| Remote digest | `sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36` |
| Local/remote digest match | `PASS` |
| Remote media type | `application/vnd.oci.image.index.v1+json` |
| Remote compressed size | `17,892,963` bytes |
| Tag policy | Existing repository is immutable; no overwrite was attempted |

The ECR push output reported the exact expected digest. Docker logout completed
after the push, and no credential value was displayed or persisted in the
repository.

## Registry scan inspection

Read-only `describe-images` returned the exact tag/digest, but the scan status
was null. Read-only `describe-image-scan-findings` returned
`ScanNotFoundException`; therefore ECR registry findings are **UNVERIFIED**.
The local Trivy result remains the authoritative security evidence for this
checkpoint: zero HIGH/CRITICAL findings.

## Next approval boundary

The exact ECR image is now eligible for a separate Terraform-only checkpoint:
update ignored development verifier-image input, run offline preflight, and
create/review a saved connected plan that changes only the admin-refresh and
read-only verifier ECS task definitions to this digest. No apply or task run is
authorized by this promotion.
