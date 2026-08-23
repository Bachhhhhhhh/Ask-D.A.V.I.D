# Goal 7 AOSS search remediation image promotion — 2026-08-21

## Approved boundary

This checkpoint was approved for local image build, ECR promotion, and
immediate read-only digest/scan inspection. It did not update ignored
Terraform inputs, create or apply a Terraform plan, deploy a bundle, mutate
Databricks/AOSS, or run/retry an ECS task.

## Source and local image

The image was built from `docker/Dockerfile.goal7-indexer` after the bounded
AOSS search diagnostics remediation. The source aggregate is the SHA-256 of
sorted, newline-delimited `sha256sum` output for the Dockerfile, index mapping,
and all regular files under `packages/goal7-runtime/src/ask_david_goal7/`:

`7cf2a9bf8df6330ae9365860ee062a14ac9f31c591adfc97cfc82b8ee567e5c1`

| Check | Result |
| --- | --- |
| Docker build | PASS — `--pull=false`, `linux/amd64` |
| Local image digest | `sha256:da06c4e719e001edc74f837ae65e1a9b91737f7503c615058595a3b5f30e46c0` |
| Image user | PASS — `65532:65532` |
| Entrypoint | PASS — `python -m ask_david_goal7.indexer` |
| Network-disabled import | PASS — `indexer-import-ok` |

## ECR promotion and inspection

| Attribute | Value |
| --- | --- |
| Account / region | `736956442295` / `ap-southeast-1` |
| Repository | `ask-david-development/langgraph-runtime` |
| Repository controls | `IMMUTABLE`, scan-on-push enabled |
| Immutable tag | `goal7-indexer-7cf2a9bf` |
| Remote digest | `sha256:da06c4e719e001edc74f837ae65e1a9b91737f7503c615058595a3b5f30e46c0` |
| Remote manifest | `application/vnd.oci.image.index.v1+json` |
| Remote image size | `43,259,346` bytes |
| Local/remote digest match | PASS |
| ECR scan findings | UNVERIFIED — one inspection returned `ScanNotFoundException`; no retry |

## Current checkpoint

Promotion is complete, but Goal 7 remains **UNVERIFIED**. The ignored
development indexer digest still points to the previous image. The next
separately approved checkpoint is to update only that ignored input and create
a saved connected Terraform plan whose expected action is the Goal 7 indexer
task-definition replacement only.
