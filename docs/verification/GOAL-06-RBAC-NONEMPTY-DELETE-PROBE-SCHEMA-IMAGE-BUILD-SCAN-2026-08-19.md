# Goal 6 SMALLINT probe remediation image build and scan — 2026-08-19

## Scope

Local-only build and security scan for the offline-validated disposable-probe
schema remediation. No Docker login, ECR push, Terraform, ECS task, Doris SQL,
Databricks, or AWS operation was performed.

## Source and image identity

| Attribute | Value |
| --- | --- |
| Source aggregate | `6fa3d0c9b55e8fe22916c7448ea44d12de3f750ee047ff6b8cfed34f44458f78` |
| Local tag | `ask-david-doris-verifier:goal6-smallint-probe-6fa3d0c9` |
| Local OCI image ID | `sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88` |
| Platform | `linux/amd64` |
| Size | `17,895,046` bytes |
| Runtime user | `65532:65532` |
| Entrypoint | `/bin/sh` |
| Base | `public.ecr.aws/docker/library/alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d` |

The image was built with `--pull=false`. The public base-image manifest was
resolved because the local daemon did not have that base tag; no registry login
or private registry operation occurred.

## Network-disabled image inspection

A `--network none --read-only` container check passed:

- all six controlled runner scripts parse with `sh -n`;
- `04_recreate_authorization_probe.sql` is included;
- base schema and probe migration both declare `probe_id SMALLINT NOT NULL`;
- migration contains only the fixed internal probe drop/recreate and sentinel
  contract;
- `probe_id TINYINT NOT NULL` is absent;
- MariaDB client is `11.4.12`.

## Security scan

Trivy `0.70.0` scanned the exact local image with:

```text
image --ignore-unfixed --severity HIGH,CRITICAL --exit-code 1
```

It downloaded the public vulnerability database from `mirror.gcr.io`, detected
Alpine `3.21.7` with 34 packages, and returned exit `0` with zero HIGH/CRITICAL
vulnerabilities. Secret scan was enabled by Trivy; no secret findings were
reported in the summary.

## Current checkpoint

The image is local only. It must be pushed under a new immutable development
ECR tag through a separately approved promotion before a new task-definition
plan can be created. The currently deployed revision-13 task definitions remain
unchanged.
