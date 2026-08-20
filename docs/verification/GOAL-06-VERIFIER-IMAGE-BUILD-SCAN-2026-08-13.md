# Goal 6 verifier image — local build and scan checkpoint

Date: 2026-08-13
Environment: local build only; no ECR push or cloud mutation

## Source and build

Aggregate SHA-256 of `docker/Dockerfile.doris-verifier`,
`docker/doris-verifier/**`, and `doris/**`:

```text
ac041bb3aaea7266adf4006f73544c4f1e48abb7ca88c7c71931eaae973838e7
```

`docker build --pull --no-cache` completed successfully. Its Alpine base
resolved to `public.ecr.aws/docker/library/alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d`.

| Property | Value |
| --- | --- |
| Local tag | `ask-david-doris-verifier:goal6-ac041bb3a` |
| Local immutable manifest digest | `sha256:167912392ef3276123ec32b021083bd1b7dec02e12af12730cd702ad7143bea6` |
| Size | `17,888,059` bytes |
| Runtime user | non-root `65532:65532` |
| Entrypoint | `/bin/sh` |

## Vulnerability scan

**PASS.** Initial Docker-bridge Trivy runs could not download their DB because
DNS resolution of `ghcr.io` through `192.168.2.253:53` timed out. A temporary
diagnostic container captured that exit-`1` local-network failure and was then
removed. Repeating the DB download with `--network host` succeeded; this uses
the host resolver only for the short-lived scanner and exposes no service.

Trivy `0.69.3` then scanned the exact local image with:

```text
--scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
--skip-db-update
```

It detected Alpine `3.21.7`, 34 packages, no language-specific files, and
**0 vulnerabilities**. The command exited `0`.

## Approved ECR push and inspection

The project owner then approved only the exact scanned source/digest above for
the immutable tag `goal6-ac041bb3a` in:

```text
736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier
```

Pre-push checks reconfirmed account `736956442295`, region
`ap-southeast-1`, the exact source/digest, and an empty immutable-tag ECR
repository. The push completed successfully. Immediate read-only ECR inspection
returned the same OCI index digest
`sha256:167912392ef3276123ec32b021083bd1b7dec02e12af12730cd702ad7143bea6`,
the expected tag, image size `17,885,962` bytes, and media type
`application/vnd.oci.image.index.v1+json`.

The short-lived ECR Docker login was passed only through stdin and was logged
out immediately after inspection, removing its local Docker credential.

## Scope confirmation

No Terraform plan/apply, ECS task launch, SQL execution, Databricks operation,
or source-data mutation occurred. A separately approved update of ignored
development tfvars and saved Terraform plan remains required before task
definitions can be created.
