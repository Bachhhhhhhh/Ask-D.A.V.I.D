# Goal 7 runtime image — local build checkpoint — 2026-08-20

## Status

**LOCAL IMAGE BUILT AND PUSHED — NOT DEPLOYED**

This checkpoint records the digest-pinned runtime image for the gated Goal 7
indexer and integrated-demo tasks. The separately approved ECR promotion is
recorded in `GOAL-07-RUNTIME-IMAGE-ECR-PUSH-2026-08-20.md`. It does not edit
ignored Terraform variables, create a Terraform plan, mutate Databricks, or
run an ECS task.

## Reproducible source aggregate

The source aggregate covers these files, sorted by path, with each file's
SHA-256 followed by its path and the resulting manifest hashed once more:

- `docker/Dockerfile.goal7-runtime`;
- `docker/requirements.goal7-runtime.txt`;
- `opensearch/index-mapping.json`;
- all regular files under `packages/goal7-runtime/src/ask_david_goal7/`.

Source aggregate:

```text
17a425d0ddbcd5c3d4056eabf370357cdc6a43ef5e11f1504823176372df1633
```

## Built artifact

| Attribute | Observed value |
| --- | --- |
| Local tag | `ask-david-goal7-runtime:offline` |
| Local OCI image/manifest digest | `sha256:c854fe57c92ad16be5cdb9935cfa16736164749a9812c9183157ad9417fae84f` |
| Platform | `linux/amd64` |
| Effective user/group | `65532:65532` |
| Entrypoint | `python -m ask_david_goal7.connected_demo` |
| Image size | `65,122,456` bytes |
| Base image | `python:3.12-slim` (resolved during build to `sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`) |

The same image is designed to run the indexer task through its Terraform
command override `python -m ask_david_goal7.indexer`.

## Local checks

| Check | Result |
| --- | --- |
| Docker build | PASS — `docker build --pull=false -f docker/Dockerfile.goal7-runtime -t ask-david-goal7-runtime:offline .` |
| Non-root image metadata | PASS — UID/GID `65532:65532` |
| Network-disabled import check | PASS — `langgraph`, `pymysql`, and `ask_david_goal7` import successfully with `--network none` |
| Entrypoint metadata | PASS — connected demo entrypoint; indexer command is an explicit task-definition override |
| Vulnerability scan | UNVERIFIED — `trivy`/`grype` is not installed in this environment; no scan result is claimed |

## Promotion boundary

The exact local digest now matches the ECR digest under immutable tag
`goal7-runtime-17a425d0`. The immediate ECR scan inspection returned
`ScanNotFoundException`, so vulnerability scanning remains UNVERIFIED. Only
after a separate approval may the ignored development variables be updated
and a new saved connected Terraform plan be created.

No image push, Terraform operation, AWS/Databricks mutation, or ECS task run
occurred for this checkpoint.
