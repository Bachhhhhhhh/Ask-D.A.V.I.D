# Goal 7 private indexer boundary — offline implementation — 2026-08-20

## Status

**IMPLEMENTED OFFLINE — CONNECTED INDEXING NOT STARTED**

This checkpoint adds the minimal controlled deployment boundary required to
move the governed synthetic outbox into the one approved private AOSS vector
index. No Terraform connected plan/apply, image push, AWS mutation,
Databricks mutation, bundle deployment, or ECS task execution occurred here.

## Implemented boundary

- `packages/goal7-runtime/src/ask_david_goal7/indexer.py` is a
  standard-library-only ECS entry point. It reads the fixed UC outbox through
  Databricks SQL Statements API, validates `databricks-gte-large-en` and 1024
  dimensions, signs AOSS requests with the ECS task role, upserts bounded
  synthetic documents, and performs one `business-reader` role-filtered
  vector search.
- `docker/Dockerfile.goal7-indexer` builds the non-root, digest-pinned task
  image source. No credentials or state are copied into the image.
- `infrastructure/modules/goal7-indexer/` defines one gated Fargate task
  definition using existing private subnets, workload role, execution role,
  and runtime log group.
- `goal7/workflow-oauth` is a Terraform-managed, KMS-encrypted secret
  populated from the Goal 4 workflow service-principal secret. The task
  execution role receives only exact secret read and KMS decrypt permissions
  when the gate is enabled. The Doris external-read secret is explicitly not
  used.
- `goal7.tf` adds only the gated workload-security-group to AOSS-endpoint-
  security-group TCP/443 rule.
- The indexer gate now fails closed unless the Goal 7 foundation is enabled,
  and the Databricks workspace host is required to be HTTPS before an OAuth
  request is attempted.

## Offline validation evidence

| Check | Result |
| --- | --- |
| Goal 7 static validator | PASS — `python3 scripts/validate_goal7.py` |
| Focused unit/regression tests | PASS — 10 tests via `pytest -o addopts='' -q tests/unit/test_goal7_static.py` |
| Python compile check | PASS — `python3 -m compileall -q packages/goal7-runtime/src/ask_david_goal7` |
| Ruff check | PASS — indexer, validator, and Goal 7 tests |
| Ruff format check | PASS — indexer and Goal 7 tests |
| Terraform formatting | PASS — modified root and Goal 7/IAM/runtime/identity modules |
| Terraform validation | Previously PASS before this wiring-only correction; current rerun is UNVERIFIED because the offline sandbox could not query the provider registry to recreate a disposable plugin cache |
| Credentials/state/plans tracked | PASS — no repository source contains credentials; no saved plan or state was added |

The current Terraform change is limited to selecting the already-declared
workflow secret ARN and adding an explicit dependency on its secret version;
the existing provider-backed validation result remains applicable to the HCL
shape, while a fresh provider-cache validation is required before a connected
plan.

## Next approval boundary

Before any connected action, separately approve: (1) local image build/scan and
push of one immutable digest to the existing private runtime repository; (2)
setting the ignored development image digest and enabling the task gate; and
(3) creation and review of a saved connected Terraform plan. No task run is
authorized by this report.
