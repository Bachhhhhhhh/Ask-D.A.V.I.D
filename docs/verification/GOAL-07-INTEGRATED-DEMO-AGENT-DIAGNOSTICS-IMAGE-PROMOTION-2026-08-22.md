# Goal 7 integrated-demo diagnostics image promotion — 2026-08-22

## Approved boundary

The approved operation covered local image build, private ECR promotion, and
immediate read-only digest/scan inspection. It did not update ignored
Terraform variables, create/apply a Terraform plan, register a task
definition, run an ECS task, or mutate Databricks, SQL, AOSS data, or other
AWS resources.

## Source and image evidence

The deterministic source aggregate is the SHA-256 of the sorted,
newline-delimited `sha256sum` manifest covering:

- `docker/Dockerfile.goal7-runtime`;
- `docker/requirements.goal7-runtime.txt`;
- `opensearch/index-mapping.json`;
- all regular files under `packages/goal7-runtime/src/ask_david_goal7/`,
  excluding `__pycache__`.

| Field | Result |
| --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| Source aggregate SHA-256 | `2e251338af4e50c40796e089c8c9c82ecb6ca3b89d272d3d25bbb65d0c317abf` |
| Local image tag | `ask-david-goal7-runtime:agent-diagnostics-2e251338` |
| Local image digest | `sha256:1c9b63827b30bff0783a321e95ebecb296f490d42473c81d14fed7e31747502b` |
| Image user | `65532:65532` |
| Entrypoint | `python -m ask_david_goal7.connected_demo` |
| Network-disabled import | PASS — `connected-demo-import-ok` |
| ECR repository | `ask-david-development/langgraph-runtime` |
| Immutable tag | `goal7-integrated-agent-diagnostics-2e251338` |
| ECR digest | `sha256:1c9b63827b30bff0783a321e95ebecb296f490d42473c81d14fed7e31747502b` |
| Digest equality | PASS |
| ECR manifest | `application/vnd.oci.image.index.v1+json` |
| ECR repository controls | PASS — `IMMUTABLE`, scan-on-push enabled |

The pre-push account check returned `736956442295`, and the destination tag
was absent. Docker registry credentials were removed with `docker logout`
after the push.

## Scan status and next boundary

The immediate `describe-image-scan-findings` call returned
`ScanNotFoundException`; the scan result is therefore **UNVERIFIED**, not a
clean scan. No retry or alternate scanner was run.

The next approval boundary is to update only the ignored development demo
image digest, run offline preflight, and create/review a saved connected
development Terraform plan. No ECS task may run until that plan is separately
approved and applied.

Goal 7 remains **UNVERIFIED**.
