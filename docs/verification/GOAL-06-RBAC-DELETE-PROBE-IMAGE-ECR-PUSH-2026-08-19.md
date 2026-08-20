# Goal 6 RBAC DELETE-probe remediation image — ECR push

Date: `2026-08-19`

Status: **PASS — IMMUTABLE IMAGE PUSHED; NOT DEPLOYED OR EXECUTED**

## Approved artifact and destination

| Attribute | Value |
| --- | --- |
| Source aggregate | `c468b8fde5b00aacb208d460099b408b9893912a845a5d48b8f1b59b6647dc64` |
| Scanned local OCI image ID | `sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e` |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| ECR repository | `ask-david-development/doris-verifier` |
| Immutable tag | `goal6-delete-probe-c468b8fd` |

## Fail-closed preflight

Read-only checks completed before Docker authentication:

- STS returned the approved account `736956442295`;
- the repository URI matched the approved private development repository;
- tag mutability was `IMMUTABLE`;
- repository scan-on-push configuration was enabled;
- encryption type was `AES256`; and
- `describe-images` returned `ImageNotFoundException` for the destination tag,
  proving that no immutable artifact would be overwritten.

The source aggregate and local OCI image ID were reverified immediately before
the push and matched the approved values.

## Push and remote inspection

Docker authentication used ECR password output only through stdin. Exactly one
tag was pushed:

```text
736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier:goal6-delete-probe-c468b8fd
```

Immediate read-only ECR inspection returned:

| Attribute | Result |
| --- | --- |
| Remote digest | `sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e` |
| Local/remote digest equality | PASS |
| Tag | `goal6-delete-probe-c468b8fd` |
| Manifest media type | `application/vnd.oci.image.index.v1+json` |
| ECR compressed image size | `17,891,916` bytes |

Docker logout completed immediately after push and removed the stored registry
login entry.

## Registry scan status

Although repository scan-on-push configuration is enabled, `describe-images`
returned no scan status and `describe-image-scan-findings` returned
`ScanNotFoundException`. ECR registry findings are therefore **NOT RUN**, not
PASS. This does not replace or weaken the exact local Trivy `0.69.3` result:
zero HIGH/CRITICAL findings with a freshly downloaded public database.

## Scope boundary and next step

No Terraform, task-definition, ECS task, Doris SQL, Databricks, S3, IAM, KMS,
network, EC2/EBS, public, or production change occurred. The active revision-10
admin/verifier task definitions still use the previous image digest.

Next requires separate approval to update only ignored development tfvars to
the new digest, run offline preflight, and create one saved connected
development Terraform plan. The only acceptable managed-resource actions are
new revisions/replacements of the two Goal 6 ECS task definitions due solely to
their image reference. Apply and the one-shot RBAC retry require later,
independent approvals.

That separately approved saved-plan checkpoint subsequently completed and is
recorded in
`docs/verification/GOAL-06-RBAC-DELETE-PROBE-TASK-DEFINITIONS-CONNECTED-PLAN-2026-08-19.md`.
The reviewed plan has exactly the expected two task-definition replacements;
it has not been applied.
