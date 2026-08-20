# Goal 6 RBAC empty-partition pruning image — local build and scan

Date: `2026-08-19`

Status: **PASS — LOCAL IMAGE BUILT/SCANNED AND SUBSEQUENTLY PUSHED; NOT DEPLOYED**

## Approved boundary

This checkpoint was approved only to build and vulnerability-scan one local
Goal 6 verifier image from the reviewed source aggregate. It did not authorize
or perform an ECR push, Terraform operation, ECS task-definition change, ECS
task, Doris connected SQL, Databricks operation, or AWS project operation.

## Reproducible source

The established sorted per-file SHA-256 manifest covers
`docker/Dockerfile.doris-verifier`, every regular file under
`docker/doris-verifier/`, and every regular file under `doris/`:

```text
3195354def2b35b9d2ca828594ae455e593906689a46145e2ba7b05bcf19a7f5
```

The aggregate was reverified before build and after final inspection. The RBAC
runner SHA-256 was:

```text
1cfd355469a54a7014a97bbf27b6c084b1d2180fecf11b386f6d8e379cda9ec7
```

Local tag:

```text
ask-david-doris-verifier:goal6-empty-prune-3195354d
```

## Built artifact

| Attribute | Observed value |
| --- | --- |
| Local OCI image ID | `sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9` |
| Platform | `linux/amd64` |
| Size | `17,894,148` bytes |
| Base distribution | Alpine `3.21.7` |
| Effective user/group | `65532:65532` |
| Entrypoint | `/bin/sh` |
| MariaDB client | `11.4.12` |

The build used `--pull=false`. Docker read public base-manifest metadata from
`public.ecr.aws`, resolved digest
`sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d`,
and reused the cached package-install layer. This was an unauthenticated public
base-image metadata read, not a project ECR push or project-account AWS API
operation; no unreviewed application source was substituted.

## Runtime-content inspection

A short-lived container ran with network disabled, a read-only root filesystem,
and a temporary `/tmp`. It confirmed:

- runtime UID/GID is exactly `65532:65532`;
- all six fixed runners exist, are executable, and pass POSIX shell parsing;
- `/app/doris-rbac-verify` matches the reviewed repository hash;
- `SET disable_empty_partition_prune = true` and the reserved-key DELETE occur
  in the same runner command;
- the invalid DELETE `WHERE FALSE` statement is absent; and
- MariaDB client `11.4.12` is installed.

The inspection emitted `content-inspection-pass`. The container used `--rm`,
and final inspection found no running container from the image.

## Vulnerability scan

Trivy `0.69.3` refreshed its public vulnerability database and scanned the
exact local image through a read-only Docker socket with:

```text
image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
```

Result: **PASS — 0 HIGH/CRITICAL findings** across 34 Alpine `3.21.7`
packages. No language-specific package file was detected.

Host networking was used only by the temporary Trivy container to download
the public vulnerability database. It published no service port and accessed
no AWS project endpoint, ECR, Databricks, Doris, Unity Catalog, or project data
endpoint.

## Next approval boundary

The exact scanned local image was subsequently pushed under a separate
approval to immutable ECR tag `goal6-empty-prune-3195354d`; evidence is
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-IMAGE-ECR-PUSH-2026-08-19.md`.
It has not been deployed. Terraform task-definition planning, apply, and
runtime execution remain later independent approval boundaries. Phase 6-11
remains partially verified.
