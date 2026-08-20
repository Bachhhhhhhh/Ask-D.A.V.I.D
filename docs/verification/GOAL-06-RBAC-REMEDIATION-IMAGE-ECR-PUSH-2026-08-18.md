# Goal 6 RBAC-remediation verifier image — ECR push

Date: `2026-08-18`

Status: `PUSHED — NOT DEPLOYED OR EXECUTED`

## Approved immutable artifact

| Attribute | Value |
| --- | --- |
| AWS account | `736956442295` |
| Region | `ap-southeast-1` |
| Repository | `ask-david-development/doris-verifier` |
| Immutable tag | `goal6-rbac-25b09566` |
| Source aggregate SHA-256 | `25b0956680a6765fcb5e2f5034208da8e6d3e5b4817ccada3c07030af681bff5` |
| Local image ID before push | `sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6` |
| ECR digest after push | `sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6` |

## Preconditions and result

Read-only preflight verified the intended account and region, repository tag
immutability, scan-on-push setting, exact source/image identity, and that the
destination tag was absent. The approved operation authenticated Docker to ECR,
pushed only the exact immutable tag above, and logged Docker out immediately.
Read-only ECR inspection confirms the matching digest and tag.

No Terraform plan/apply/destroy, ECS task, Doris SQL, Databricks operation, or
AWS resource mutation other than the approved ECR image/blob push occurred.
No task definition references this new image yet.

## Scan evidence

The reviewed local image passed Trivy `0.69.3` with zero HIGH/CRITICAL
findings. ECR repository configuration reports `scanOnPush = true`, but the
immediate `DescribeImageScanFindings` call returned `ScanNotFoundException`.
Therefore, ECR registry scan findings are **NOT RUN**; this report does not
replace the completed local scan with an assumed registry result.

## Next boundary

Promotion to ECS requires a separate approval to update only the ignored
development image input, run offline preflight, and create a saved connected
Terraform plan. That future plan must be reviewed independently; it must not
run a task or apply a change without further approval.
