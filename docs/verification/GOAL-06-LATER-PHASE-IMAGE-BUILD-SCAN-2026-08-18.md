# Goal 6 later-phase verifier image — local build and scan

Date: `2026-08-18`

Status: `LOCAL IMAGE BUILT/SCANNED AND SUBSEQUENTLY PUSHED — NOT DEPLOYED`

## Scope

This checkpoint packages the already reviewed Goal 6 result-contract, RBAC,
query-limit, and audit verifier remediations into one local immutable image.
It does not push an ECR artifact, register an ECS task-definition revision,
launch a task, execute Doris SQL, or perform an AWS, Databricks, or Terraform
operation.

## Reproducible inputs

The source aggregate covers `docker/Dockerfile.doris-verifier`, every regular
file below `docker/doris-verifier/`, and every regular file below `doris/`.
It is computed by sorting the null-delimited path set, hashing each file, and
hashing that manifest:

```text
ecbd7e31c590bc279da57eec328d907517eb95de91a20c9da65eb7352df1b052
```

Local tag:

```text
ask-david-doris-verifier:goal6-later-ecbd7e31
```

## Built artifact

| Attribute | Observed value |
| --- | --- |
| Local OCI image ID/digest | `sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510` |
| Platform | `linux/amd64` |
| Size | `17,893,046` bytes |
| Base distribution | Alpine `3.21.7` |
| Effective user/group | `65532:65532` |
| Entrypoint | `/bin/sh` |
| MariaDB client | `11.4.12` |

## Local validation

| Check | Result |
| --- | --- |
| Image build from the reviewed source aggregate | PASS |
| Non-root effective UID/GID | PASS — `65532:65532` |
| Network-disabled container inspection | PASS |
| Six fixed runners present, executable, and POSIX-shell parseable | PASS |
| Repository/image hash equality for result, RBAC, query-limit, audit, serving schema, and rebuild migration inputs | PASS |
| Trivy `0.69.3` HIGH/CRITICAL vulnerability scan with `--ignore-unfixed` | PASS — zero findings |

The six executable image entrypoints checked were:

- `/app/doris-admin-refresh`;
- `/app/doris-readonly-verify`;
- `/app/doris-rebuild-serving`;
- `/app/doris-rbac-verify`;
- `/app/doris-query-limit-verify`;
- `/app/doris-audit-verify`.

The later local attempt to repeat the Trivy scan with `--skip-db-update` used a
fresh empty cache volume and correctly stopped before scanning because no local
database was present. That non-scan does not replace the completed scan above
and made no source, image, or cloud change.

## Deployment boundary

The local digest is not an ECR digest and must not be used as an ECS image
reference. The active revision-8 admin and verifier task definitions still use
the previously approved immutable ECR image and do not contain these later
verifier runners/remediations.

After the separately approved Phase 6-7 admin refresh succeeds, promotion
requires two additional independent boundaries:

1. approval to push this exact reviewed source/image under an immutable ECR
   tag and verify the resulting registry digest;
2. a saved connected Terraform plan and separate apply approval to register
   task-definition revisions that use that exact ECR digest.

No later verifier task is authorized by this report. The exact image was
subsequently pushed under the immutable registry digest recorded in
`GOAL-06-LATER-PHASE-IMAGE-ECR-PUSH-2026-08-18.md`; it is still absent from
the active task definitions.

## Read-only promotion preflight

After Phase 6-7 completed, promotion was rechecked without mutation:

| Check | Result |
| --- | --- |
| AWS identity | PASS — account `736956442295` |
| CLI region | PASS — `ap-southeast-1` |
| ECR repository | PASS — `ask-david-development/doris-verifier` |
| Tag policy | PASS — `IMMUTABLE` |
| Registry scan-on-push | PASS — enabled |
| Intended tag | PASS — `goal6-later-ecbd7e31` is absent |
| Current ignored verifier-image input | Unchanged — still the approved revision-8 digest `sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad` |

The tag lookup returned `ImageNotFoundException`, which is the expected
fail-closed proof that the immutable destination name is unused. No ECR login,
tagging, push, tfvars edit, Terraform operation, or task execution occurred.
