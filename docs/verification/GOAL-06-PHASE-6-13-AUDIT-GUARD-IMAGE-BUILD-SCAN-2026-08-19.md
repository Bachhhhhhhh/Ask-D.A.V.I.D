# Goal 6 Phase 6-13 audit-guard image — local build and scan

Date: `2026-08-19`

Status: **PASS — LOCAL IMAGE BUILT/SCANNED; NOT PUSHED OR DEPLOYED**

## Approved boundary

This checkpoint built and scanned one local image from the offline-validated
Phase 6-13 audit-guard source. It did not authenticate to or push ECR, modify
Terraform, register a task-definition revision, run an ECS task, execute Doris
SQL, call Databricks, or mutate AWS resources.

## Reproducible source and artifact

The source aggregate covers `docker/Dockerfile.doris-verifier`, every regular
file below `docker/doris-verifier/`, and every regular file below `doris/`.
The sorted per-file SHA-256 manifest contains 17 files and hashes to:

```text
25b48aea6cbedb2f901b7e959d788fed2f4bc79ece65f49b43efc33f7634907c
```

The two newly remediated runner hashes were reverified before and after the
build:

| File | SHA-256 |
| --- | --- |
| `docker/doris-verifier/doris-admin-refresh` | `ca2aa999675ed47b8236344e966933c93d207d16bfa527474a62fe96b0cebcae` |
| `docker/doris-verifier/doris-audit-verify` | `2b2c9316c0dffcf3aebac0611769e553e6fe43964ed3aa5cff7f79cc74b21da4` |

| Attribute | Observed value |
| --- | --- |
| Local tag | `ask-david-doris-verifier:goal6-audit-guards-25b48aea` |
| Local OCI image/index digest | `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |
| Platform | `linux/amd64` |
| Size | `17,895,432` bytes |
| Runtime UID/GID | `65532:65532` |
| Entrypoint | `/bin/sh` |
| MariaDB client | `11.4.12` |

The build used `docker build --pull=false`; the already reviewed public Alpine
base/package layers were reused. No private registry login was performed.

## Local runtime inspection

A short-lived `--network none --read-only` container with a temporary `/tmp`
filesystem passed all checks:

- effective UID/GID is `65532:65532`;
- all six fixed Goal 6 runners exist, are executable, and pass `sh -n`;
- the image copies the exact reviewed admin and audit runner hashes; and
- the MariaDB client is available.

The first inspection invocation supplied an extra `sh` argument to the image's
`/bin/sh` entrypoint and stopped with a local command-usage error. The corrected
entrypoint invocation passed; this was not an image or runtime failure.

## Vulnerability scan

Trivy `0.69.3` scanned the exact local tag with:

```text
image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
```

Result: **PASS** — Alpine `3.21.7`, 34 packages, zero HIGH/CRITICAL findings,
and no language-specific files detected. The scanner downloaded only the public
Trivy vulnerability database and did not contact project AWS, ECR, Databricks,
or Doris endpoints.

## Next approval boundary

The image is local only. The active revision-15 ECS task definitions remain on
the previously approved ECR digest. A separate approval is required to push
this exact image under a new immutable ECR tag, followed by independent
Terraform task-definition planning/apply and one-shot admin-refresh/audit
verification approvals. Phase 6-13 remains **UNVERIFIED**.
