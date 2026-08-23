# Goal 7 dedicated indexer image — ECR promotion — 2026-08-21

## Status

**PUSH PASS — TASK NOT RUN**

The separately approved dedicated Goal 7 indexer image was promoted to the
existing private ECR repository. No Terraform, ignored-variable update,
Databricks operation, AOSS mutation, or ECS task run occurred.

## Preflight

| Check | Result |
| --- | --- |
| AWS account | PASS — `736956442295` |
| AWS region | PASS — `ap-southeast-1` |
| Principal | PASS — `arn:aws:iam::736956442295:user/bach_dev_admin_david` |
| Repository | PASS — `ask-david-development/langgraph-runtime` |
| Repository URI | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/langgraph-runtime` |
| Tag mutability | PASS — `IMMUTABLE` |
| Scan-on-push configuration | PASS — enabled |
| Local image entry point | PASS — `python -m ask_david_goal7.indexer` |
| Local image user | PASS — `65532:65532` |

## Promoted artifact

| Attribute | Value |
| --- | --- |
| Source aggregate | `6fc7ce13b4a5a53c51124529ca483f72eb921e02d5dbf01e51ae8a72afef4207` |
| Local image ID | `sha256:08ef16bfbd3e4dbd6a940227a6fd7afab14385644eec617d02da7c8f46714669` |
| Immutable tag | `goal7-indexer-6fc7ce13` |
| Remote image digest | `sha256:08ef16bfbd3e4dbd6a940227a6fd7afab14385644eec617d02da7c8f46714669` |
| Remote manifest | `application/vnd.oci.image.index.v1+json` |
| Remote image size | `43,252,113` bytes |
| Push time | `2026-08-21T01:28:25+07:00` |

## Verification boundary

- `aws ecr describe-images` confirmed the immutable tag resolves to the exact
  local digest.
- `describe-image-scan-findings` returned `ScanNotFoundException`; therefore
  vulnerability scan findings are **UNVERIFIED**, not silently treated as a
  pass and not retried in this checkpoint.
- The ignored development image variables still point to the previously
  reviewed digest and were not changed.
- A new saved Terraform plan and any ECS task require separate approvals.

## Next checkpoint

Separately approve updating ignored development variables with the dedicated
indexer digest (and a distinct demo image digest), then create and review a
saved connected Terraform plan. Do not run an indexer task until that plan is
approved and applied.
