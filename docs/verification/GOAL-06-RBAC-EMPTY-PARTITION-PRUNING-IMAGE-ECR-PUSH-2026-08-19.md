# Goal 6 RBAC empty-partition pruning image — ECR push

Date: `2026-08-19`

Status: **PASS — EXACT SCANNED IMAGE PUSHED; NOT DEPLOYED**

## Approved boundary

The approved operation was limited to authenticating to the existing private
development ECR registry, pushing the exact scanned local Goal 6 verifier
image under one new immutable tag, logging out, and performing immediate
read-only digest/scan inspection. It did not authorize or perform Terraform,
an ECS task or task-definition change, Doris SQL, Databricks, or another AWS
resource mutation.

## Preflight

| Check | Result |
| --- | --- |
| AWS account / Region | PASS — `736956442295` / `ap-southeast-1` |
| Authenticated principal | `arn:aws:iam::736956442295:user/bach_dev_admin_david` |
| Repository | `ask-david-development/doris-verifier` |
| Repository URI | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier` |
| Tag policy | PASS — `IMMUTABLE` |
| Scan-on-push configuration | enabled |
| Repository encryption | `AES256` |
| Proposed tag | PASS — absent before push |
| Source aggregate | PASS — `3195354def2b35b9d2ca828594ae455e593906689a46145e2ba7b05bcf19a7f5` |
| Exact local image ID | PASS — `sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9` |

## Push result

Only this tag was pushed:

```text
goal6-empty-prune-3195354d
```

Immediate ECR inspection returned:

| Attribute | Value |
| --- | --- |
| Remote digest | `sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9` |
| Local/remote digest match | PASS |
| Compressed image size | `17,892,051` bytes |
| Manifest media type | `application/vnd.oci.image.index.v1+json` |
| Tags on digest | only `goal6-empty-prune-3195354d` |

Docker logout completed immediately after push and removed credentials for the
development ECR registry.

## Scan evidence

`describe-images` returned no ECR image-scan status, and
`describe-image-scan-findings` returned `ScanNotFoundException`. Registry scan
findings are therefore **NOT RUN**, despite scan-on-push being configured. This
is not represented as a successful ECR scan.

The exact local image's separately recorded Trivy `0.69.3` scan remains
**PASS — 0 HIGH/CRITICAL findings** across 34 Alpine `3.21.7` packages:
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-IMAGE-BUILD-SCAN-2026-08-19.md`.

## Next approval boundary

The immutable image is present in ECR but revision 11 task definitions still
use the prior digest. Updating the ignored development image input, running
offline preflight, and creating a saved connected development plan limited to
the two Goal 6 ECS task-definition revisions requires separate approval. No
task may run and no plan may be applied under this checkpoint.

That separately approved planning checkpoint was subsequently attempted, but
Databricks account/workspace refresh failures produced an errored,
non-applyable plan artifact. No valid saved plan was created and no apply ran.
Evidence is
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-CONNECTED-PLAN-BLOCKER-2026-08-19.md`.
