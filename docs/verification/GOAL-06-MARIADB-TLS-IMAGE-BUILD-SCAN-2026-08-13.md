# Goal 6 MariaDB TLS remediation image — local build and scan

Date: 2026-08-13
Scope: local image build, runtime option check, and vulnerability scan
ECR push/cloud mutation: not run

## Immutable source and image

Source aggregate (13 sorted repository-relative files, per-file SHA-256 lines
hashed as documented in the offline remediation report):

`ab6bc4dceabf86134ac526707b592d1e95137076ecbf55343b12eabfcee5b142`

Local tag:

`ask-david-doris-verifier:goal6-mariadb-ssl-ab6bc4d`

Local image ID/manifest:

`sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6`

Image size: `17,888,458` bytes
Runtime user: `65532:65532`
Base image: Alpine `3.21` pinned to
`sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d`

## Runtime checks

The image's MariaDB 11.4.12 client accepted `--ssl --protocol=TCP`; all three
runner files inside the image contained the corrected option and no
`--ssl-mode` option. The image remained non-root.

## Vulnerability scan

Trivy `0.69.3` scanned the exact local image with:

```text
--scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
```

The first container-network DB download timed out at the local DNS resolver.
The same scan was rerun with `--network host` for the short-lived scanner;
the database download completed and the scan exited `0` with Alpine `3.21.7`,
34 packages, and `0` HIGH/CRITICAL vulnerabilities detected.

No ECR login, ECR push, Terraform, AWS control-plane operation, Databricks
operation, ECS task, or source-data mutation occurred.

## Approved ECR push and inspection

The exact scanned local image was pushed after explicit approval to:

`736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier:goal6-mariadb-ssl-ab6bc4d`

Read-only ECR inspection returned:

- image digest: `sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6`;
- immutable tag: `goal6-mariadb-ssl-ab6bc4d`;
- media type: `application/vnd.oci.image.index.v1+json`;
- ECR size: `17,886,361` bytes.

The Docker ECR session was logged out immediately after inspection. The shell
wrapper that performed the push exited non-zero after the successful registry
digest output because of a reporting-command quoting error; no retry or second
push was performed. Task-definition configuration and apply require subsequent
separate approvals.
