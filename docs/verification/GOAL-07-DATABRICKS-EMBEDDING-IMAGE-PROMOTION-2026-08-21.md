# Goal 7 Databricks embedding-response image promotion — 2026-08-21

## Approved boundary

This checkpoint was approved for local image build, ECR promotion, and
immediate read-only digest/scan inspection. It did not update ignored
Terraform inputs, create or apply a Terraform plan, deploy a bundle, mutate
Databricks/AOSS, or run/retry an ECS task.

## Source and local image

The corrected indexer image was built from `docker/Dockerfile.goal7-indexer`.
The source aggregate is the SHA-256 of sorted, newline-delimited `sha256sum`
output for the Dockerfile, index mapping, and all regular files under
`packages/goal7-runtime/src/ask_david_goal7/`:

`03e29f63f11dd8c35cb158076b9db3a026ad548365eff1c646427fd36a73c39f`

| Check | Result |
| --- | --- |
| Docker build | PASS — `--pull=false`, `linux/amd64` |
| Local image digest | `sha256:c48ee41c63f36a6d42b4494ceba363e37754f08da60fb50e0a2e0906facc47b0` |
| Image user | PASS — `65532:65532` |
| Entrypoint | PASS — `python -m ask_david_goal7.indexer` |
| Network-disabled import | PASS — `indexer-import-ok` |

## ECR promotion and inspection

| Attribute | Value |
| --- | --- |
| Account / region | `736956442295` / `ap-southeast-1` |
| Repository | `ask-david-development/langgraph-runtime` |
| Repository controls | `IMMUTABLE`, scan-on-push enabled |
| Immutable tag | `goal7-indexer-03e29f63` |
| Remote digest | `sha256:c48ee41c63f36a6d42b4494ceba363e37754f08da60fb50e0a2e0906facc47b0` |
| Remote manifest | `application/vnd.oci.image.index.v1+json` |
| Remote image size | `43,259,046` bytes |
| Local/remote digest match | PASS |
| ECR scan findings | UNVERIFIED — one inspection returned `ScanNotFoundException`; no retry |

The ECR login command emitted Docker's standard warning that credentials are
stored unencrypted in the local Docker config. No credential value was read,
printed, committed, or transmitted in project artifacts.

## Current checkpoint

Promotion is complete, but Goal 7 remains **UNVERIFIED**. The ignored
development indexer digest is unchanged. The next separately approved
checkpoint is to update only that ignored image input and create a saved
connected Terraform plan whose expected action is the Goal 7 indexer
task-definition replacement only. No ECS task is authorized by this report.
