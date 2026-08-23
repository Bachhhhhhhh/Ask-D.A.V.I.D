# Goal 7 AOSS vector upsert image promotion — 2026-08-21

## Boundary

This checkpoint was separately approved for local image build, ECR promotion,
and immediate read-only digest/scan inspection. It did not update ignored
Terraform variables, create or apply Terraform plans, deploy a bundle, mutate
Databricks/AOSS, or run/retry an ECS task.

## Source and local image

The image was built from `docker/Dockerfile.goal7-indexer` with the corrected
`AossClient` implementation. The source aggregate is the SHA-256 of sorted,
newline-delimited `sha256sum` output for the Dockerfile, index mapping, and
all regular files under `packages/goal7-runtime/src/ask_david_goal7/`:

`2d2abf39b875df78b1e4b3ff37c355ba5d0992596d652afdb8900ddb9c61e9aa`

| Check | Result |
| --- | --- |
| Docker build | PASS — `--pull=false`, `linux/amd64` |
| Local image digest | `sha256:bd3b9f2afd102cf165ee6b303fd973b228233d72406967d81c3b616e2f350b5e` |
| Image user | PASS — `65532:65532` |
| Entrypoint | PASS — `python -m ask_david_goal7.indexer` |
| Network-disabled import | PASS — `indexer-import-ok` |
| Local Trivy scan | UNVERIFIED — `trivy` is not installed |

## ECR promotion

| Attribute | Value |
| --- | --- |
| Account / region | `736956442295` / `ap-southeast-1` |
| Repository | `ask-david-development/langgraph-runtime` |
| Repository controls | `IMMUTABLE`, scan-on-push enabled |
| Immutable tag | `goal7-indexer-2d2abf39` |
| Remote digest | `sha256:bd3b9f2afd102cf165ee6b303fd973b228233d72406967d81c3b616e2f350b5e` |
| Remote manifest | `application/vnd.oci.image.index.v1+json` |
| Remote size | `43,255,193` bytes |
| Digest match | PASS — local and remote match |
| ECR scan findings | UNVERIFIED — `ScanNotFoundException`; no retry performed |

## Current checkpoint

Promotion is complete, but Goal 7 remains **UNVERIFIED**. The ignored
development indexer digest has not been changed. The next separately approved
checkpoint is to update only the ignored development image input and create a
saved connected Terraform plan whose expected action is the Goal 7 indexer
task-definition replacement only. No ECS task is authorized by this report.
