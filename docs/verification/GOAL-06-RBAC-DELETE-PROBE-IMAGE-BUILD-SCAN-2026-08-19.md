# Goal 6 RBAC DELETE-probe remediation image — local build and scan

Date: `2026-08-19`

Status: **LOCAL IMAGE BUILT/SCANNED AND SUBSEQUENTLY PUSHED — NOT DEPLOYED**

## Approved boundary

This checkpoint was approved only to build and vulnerability-scan one local
Goal 6 verifier image from the reviewed source aggregate. It did not authorize
or perform an ECR push, Terraform operation, ECS task-definition change, ECS
task, Doris SQL, Databricks operation, or AWS operation.

## Reproducible source

The established sorted per-file SHA-256 manifest covers
`docker/Dockerfile.doris-verifier`, every regular file under
`docker/doris-verifier/`, and every regular file under `doris/`:

```text
c468b8fde5b00aacb208d460099b408b9893912a845a5d48b8f1b59b6647dc64
```

Local tag:

```text
ask-david-doris-verifier:goal6-delete-probe-c468b8fd
```

## Built artifact

| Attribute | Observed value |
| --- | --- |
| Local OCI image ID | `sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e` |
| Platform | `linux/amd64` |
| Size | `17,894,013` bytes |
| Base distribution | Alpine `3.21.7` |
| Effective user/group | `65532:65532` |
| Entrypoint | `/bin/sh` |
| MariaDB client | `11.4.12` |
| RBAC runner SHA-256 | `5271111b7ac07e1c96dfb807e07e52defc15fd42a0a37dd53fa128fb75357fc5` |

The build used `--pull=false`; the pinned Alpine base was already locally
resolved and the package-install layer was cached. No unreviewed source was
substituted.

## Runtime-content inspection

A short-lived container ran with network disabled, a read-only root filesystem,
and a temporary `/tmp`. It confirmed:

- runtime UID/GID is exactly `65532:65532`;
- all six fixed runners exist, are executable, and pass POSIX shell parsing;
- `/app/doris-rbac-verify` matches the reviewed repository hash;
- the reserved-key precondition and non-constant DELETE predicate are present;
- the invalid DELETE `WHERE FALSE` statement is absent; and
- the expected MariaDB client version is installed.

The first inspection harness invocation stopped before these assertions because
its own double-quoted grep literal expanded an unset shell variable under
`set -u`. The command was corrected by escaping that literal and rerun against
the same image; no rebuild occurred. The corrected inspection passed. Both
short-lived containers used `--rm`, and final inspection found no container
from this image running.

## Vulnerability scan

Trivy `0.69.3` refreshed its public vulnerability database and scanned the
exact local image through a read-only Docker socket with:

```text
image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
```

Result: **PASS — 0 HIGH/CRITICAL findings** across 34 Alpine packages. No
language-specific package file was detected.

Host networking was used only by the temporary Trivy container to download the
public vulnerability database. It published no service port and accessed no
AWS, Databricks, Doris, Unity Catalog, or project data endpoint.

## Next approval boundary

The exact local artifact was subsequently pushed under a separately approved
immutable ECR tag. That operation is recorded in
`docs/verification/GOAL-06-RBAC-DELETE-PROBE-IMAGE-ECR-PUSH-2026-08-19.md`.
The deployed revision-10 task definitions still use the previous digest.
Terraform task-definition revision and a later one-shot RBAC retry remain
separate subsequent approvals.
