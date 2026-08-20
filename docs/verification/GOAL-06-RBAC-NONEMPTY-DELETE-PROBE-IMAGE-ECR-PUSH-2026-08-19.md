# Goal 6 RBAC non-empty DELETE-probe image — ECR promotion

Date: `2026-08-19`

Status: **PASS — EXACT SCANNED IMAGE PUSHED; NOT DEPLOYED**

## Approved artifact

| Attribute | Value |
| --- | --- |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| AWS principal | `arn:aws:iam::736956442295:user/bach_dev_admin_david` |
| Source aggregate | `181100d9a1cad8b8285369616a32f0f3a9c848ed15f5b198ff11f85f8f79d673` |
| Local OCI digest | `sha256:b2a4629e1e207fa9b2d06cdca5956472f6e4f94e4f40723a5bc45f1a18b17a73` |
| Repository | `ask-david-development/doris-verifier` |
| Immutable tag | `goal6-nonempty-delete-181100d9` |

Immediately before authentication, the source aggregate and local OCI digest
matched the approved values. Read-only ECR preflight confirmed repository tag
immutability `IMMUTABLE`, scan-on-push enabled, AES256 encryption, and that the
approved tag did not exist. No immutable tag was overwritten.

## Promotion result

Docker authenticated only to the approved ECR registry using password stdin,
pushed the exact local image under the approved tag, then logged out in cleanup.
No credential value was printed or persisted in the repository.

Read-only ECR inspection returned the exact remote digest:

```text
sha256:b2a4629e1e207fa9b2d06cdca5956472f6e4f94e4f40723a5bc45f1a18b17a73
```

It exactly matches the scanned local OCI image.

## Scan evidence

The ECR repository has scan-on-push enabled, but immediate
`describe-image-scan-findings` returned `ScanNotFoundException`. Registry scan
findings are therefore **NOT RUN / NOT AVAILABLE**; this report does not infer
a pass from repository configuration. The exact local Trivy `0.69.3` scan
remains PASS with zero HIGH/CRITICAL findings; see
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-IMAGE-BUILD-SCAN-2026-08-19.md`.

## Scope and next boundary

This operation created only ECR image/blob/tag content. It did not run
Terraform, create/update an ECS task definition, run an ECS task, execute Doris
SQL, access Databricks, or change any other AWS resource.

The image is not in the active revision-12 task definitions. A separate
approval is required to update ignored development tfvars, run offline
preflight, and create a saved connected Terraform plan limited to the two
admin/verifier task-definition revisions.
