# Goal 6 workspace-origin remediation — offline validation

Date: 2026-08-13
Scope: source, regression tests, and documentation only; no cloud operation

## Defect and correction

The revision-1 admin task definition injects the approved Databricks workspace
as an HTTPS origin. The prior runner prepended `https://` again when composing
its OAuth and Unity Catalog Iceberg REST URLs, producing an invalid
double-scheme URL.

The runner now:

1. normalizes one optional trailing slash into `workspace_origin`;
2. accepts only one `https://*.cloud.databricks.com` origin;
3. exits `1` with a non-sensitive `invalid-workspace-origin` JSON result before
   secret parsing or network access when the origin is malformed; and
4. composes both OAuth and Iceberg REST paths only from the normalized origin.

This remains a URL-construction correction only. It does not relax TLS,
privileges, source allowlisting, credential vending, networking, or data-write
boundaries.

## Offline evidence

| Check | Result |
| --- | --- |
| Shell syntax, admin runner | PASS |
| Invalid-origin execution with all dummy inputs | PASS — emitted only `invalid-workspace-origin` and exited `1` before network access. |
| `scripts/validate_goal6.py` | PASS — static contract rejects the old double-scheme construction and requires the strict normalized-origin controls. |
| `python3 -m py_compile` on updated validator and regression test | PASS |
| Local verifier image build | PASS — source aggregate `ef83572cc9ee0a05c2fabc95e69b566656af537e9f671f23a8f954576bc03c40`, local OCI digest `sha256:41095093cb0cc820eb8b15afedacf97333ba443de8216de9dc40b950becee57d`. |
| Trivy `0.69.3` image vulnerability scan | PASS — HIGH/CRITICAL, ignore-unfixed, exit code 1 on finding; Alpine `3.21.7`, 34 packages, 0 findings. |
| `git diff --check` | PASS |
| Focused pytest | UNVERIFIED — the checked-in `.venv` entrypoint targets a missing `/workspace/.venv/bin/python3`; neither `uv` nor the prior temporary validation environment is present. No dependency installation or lock bypass was performed. |

## Required next checkpoint

## Approved ECR push and inspection

After explicit hash-bound approval, the scanned image was pushed with immutable
tag `goal6-workspace-origin-ef83572c` to the Terraform-created private ECR
repository. Immediate read-only ECR inspection returned the same OCI digest
`sha256:41095093cb0cc820eb8b15afedacf97333ba443de8216de9dc40b950becee57d`,
the expected tag, size `17,886,395` bytes, and OCI image-index media type. The
temporary Docker ECR login was removed immediately after inspection.

Do not plan Terraform, replace task definitions, or launch an ECS task without
the separate approvals required by the Goal 6 runbook.
