# Goal 6 Phase 6-12 query-limit image — local build and scan

Date: `2026-08-19`

Status: `PASS — LOCAL IMAGE BUILT/SCANNED; NOT PUSHED OR DEPLOYED`

## Approved boundary

This checkpoint was approved only for a local Docker build, network-disabled
runtime inspection, and HIGH/CRITICAL vulnerability scan of the offline-
remediated Goal 6 verifier source. It did not authorize ECR push, Terraform,
ECS task-definition changes, ECS task execution, Doris SQL, Databricks, or AWS
project operations.

## Exact source and artifact

The established source aggregate covers `docker/Dockerfile.doris-verifier`,
every regular file below `docker/doris-verifier/`, and every regular file below
`doris/`, using the sorted per-file SHA-256 manifest method (newline-delimited
`sha256sum` output):

```text
a4a0f4fd3a003fadd1a9e7ce48c9d3a75dfdf183768dc593df2fbc40847d4b84
```

| Attribute | Value |
| --- | --- |
| Local tag | `ask-david-doris-verifier:goal6-query-limit-20260819` |
| Local OCI image/index digest | `sha256:ff56b545a6850047035e619d01833f57c2646517b761fd70ec8a0767b393cb36` |
| Platform | `linux/amd64` |
| Size | `17,895,060` bytes |
| Runtime UID/GID | `65532:65532` |
| Entrypoint | `/bin/sh` |
| Base | `public.ecr.aws/docker/library/alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d` |
| MariaDB client | `11.4.12` |

The build used `docker build --pull=false`. It reused the reviewed public
Alpine base and package layer; no private registry login or project AWS API
operation occurred.

## Runtime inspection

A short-lived `--network none --read-only` container with temporary `/tmp`
confirmed the non-root UID/GID, all six fixed Goal 6 runner entrypoints and
POSIX shell parsing, MariaDB client availability, and the remediation contract:

- `SHOW PROPERTY LIKE 'query_timeout'` is present;
- `SHOW PROPERTY FOR` is absent from the query-limit runner; and
- no network or mutable project endpoint was reachable.

The container exited with `content-inspection-pass` and was removed.

## Vulnerability scan

Trivy `0.69.3` scanned the exact local image through a read-only Docker socket
with:

```text
image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
```

Result: `PASS` — zero HIGH/CRITICAL findings across 34 Alpine 3.21.7 packages;
no language-specific files were detected. The temporary scanner used host
networking only to download the public vulnerability database and did not
contact project AWS, ECR, Databricks, or Doris endpoints.

## Current boundary

The deployed ECS revision-14 task definitions remain unchanged on their prior
image digest. The exact local artifact is not yet an ECR image and cannot be
used for a connected task. A separate approval is required to push it under a
new immutable ECR tag, followed by separate Terraform task-definition planning
and apply approval, then one no-retry query-limit verifier task.
