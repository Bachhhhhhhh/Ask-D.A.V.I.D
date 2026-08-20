# Goal 6 RBAC non-empty DELETE-probe image — local build and scan

Date: `2026-08-19`

Status: **PASS — LOCAL IMAGE BUILT/SCANNED AND SUBSEQUENTLY PUSHED; NOT DEPLOYED**

## Approved boundary

This checkpoint was approved only to build and vulnerability-scan one local
Goal 6 verifier image. It did not authorize or perform an ECR push, Terraform
operation, ECS task-definition change, ECS task, Doris SQL, Databricks
operation, or AWS project operation.

## Reproducible source

The established sorted per-file SHA-256 manifest covers
`docker/Dockerfile.doris-verifier`, every regular file under
`docker/doris-verifier/`, and every regular file under `doris/`:

```text
181100d9a1cad8b8285369616a32f0f3a9c848ed15f5b198ff11f85f8f79d673
```

The aggregate was reverified immediately before build. The remediated RBAC
runner SHA-256 was:

```text
2f0a37088a8bd24b88c4cb60eb5723275842326cc2cfb1ee40077f6289f11d9c
```

## Local image

| Attribute | Value |
| --- | --- |
| Local tag | `ask-david-doris-verifier:goal6-nonempty-delete-181100d9` |
| Local OCI image ID | `sha256:b2a4629e1e207fa9b2d06cdca5956472f6e4f94e4f40723a5bc45f1a18b17a73` |
| Platform | `linux/amd64` |
| Size | `17,894,798` bytes |
| Base distribution | Alpine `3.21.7` |
| Effective user/group | `65532:65532` |
| Entrypoint | `/bin/sh` |
| MariaDB client | `11.4.12` |

Docker `29.7.1` built with `--pull=false`. It read only public base-manifest
metadata from `public.ecr.aws` and used the already-pinned Alpine digest
`sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d`.
This was not an authenticated project ECR operation.

## Runtime-content inspection

A network-disabled, read-only, non-root container inspection passed:

- all six fixed runners exist, are executable, and pass POSIX shell parsing;
- `/app/doris-rbac-verify` matches the reviewed runner SHA-256;
- the image contains exactly the lower/upper neutral sentinel schema values;
- the runner emits the sanitized `delete-probe-guard` marker;
- the ineffective `disable_empty_partition_prune` setting is absent; and
- no temporary container remains after inspection.

## Vulnerability scan

Trivy `0.69.3` scanned the exact local image with
`--ignore-unfixed --severity HIGH,CRITICAL --exit-code 1`. It fetched only the
public vulnerability database from `mirror.gcr.io/aquasec/trivy-db:2`; scan
output identified Alpine `3.21.7`, 34 packages, and **0** HIGH/CRITICAL
findings. Exit code was `0`.

## Next approval boundary

The exact image was subsequently pushed under separately approved immutable tag
`goal6-nonempty-delete-181100d9`; see
`docs/verification/GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-IMAGE-ECR-PUSH-2026-08-19.md`.
Terraform planning/apply, task registration, admin seed refresh, and RBAC
verification remain later independent boundaries.
