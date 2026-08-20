# Goal 6 admin global-grant remediation — local image build and scan

Date: 2026-08-17
Scope: local build and vulnerability scan only
Cloud mutation: none

## Immutable source and image

The sorted `sha256sum` aggregate of `docker/Dockerfile.doris-verifier`,
`docker/doris-verifier/**`, and `doris/**` is:

```text
ad0056f26ac2901410075224e57ae1406c5cfe2405e6374280bf44dbb1dd423b
```

The standard Docker build was unable to complete its Alpine package download
and produced no image. After the project owner explicitly approved one
host-networked local build/scan attempt, the following local image was built:

| Property | Value |
| --- | --- |
| Local tag | `ask-david-doris-verifier:goal6-admin-priv-ad0056f2` |
| Local image ID | `sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad` |
| Size | `17,888,460` bytes |
| Runtime user | `65532:65532` (non-root) |
| Entrypoint | `/bin/sh` |
| MariaDB client | `11.4.12` |

The short-lived local runtime check verified the runner contains
`GRANT ADMIN_PRIV ON *.*.*` and does not contain the invalid
`GRANT ADMIN_PRIV ON *.*` form. It did not connect to Doris, Databricks, AWS,
or any external data source.

## Vulnerability scan

The pre-existing local `aquasec/trivy:0.69.3` image scanned the exact local tag
in one short-lived container with host networking, Docker socket access only,
and these policy options:

```text
image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
```

It downloaded the current Trivy vulnerability database, identified Alpine
`3.21.7` with 34 packages, and exited `0` with **0 HIGH/CRITICAL
vulnerabilities**. The container was removed automatically. Host networking
was used only to download public Alpine/Trivy dependencies; no service port was
published and no AWS, ECR, Terraform, ECS, Databricks, Unity Catalog, or source
data operation occurred.

## Next approval boundary

The separately approved ECR push completed for immutable tag
`goal6-admin-priv-ad0056f2`; immediate read-only inspection returned the exact
local image ID as remote OCI digest. Evidence:
`docs/verification/GOAL-06-ADMIN-PRIV-GRANT-ECR-PUSH-2026-08-17.md`. The
active task definitions remain unchanged. A separately approved Terraform
task-definition update and a later one-shot admin-refresh execution are still
required.
