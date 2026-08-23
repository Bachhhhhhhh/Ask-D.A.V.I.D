# Goal 7 dedicated indexer image contract — offline remediation — 2026-08-21

## Status

**OFFLINE REMEDIATION PASS — NO CLOUD OPERATION**

This checkpoint addresses the approved post-egress indexer failure. The
private task started and exited with `missing required environment variable:
DORIS_FE_HOST`, while the checked-in indexer contract has no Doris dependency.
The correction is source-level and fail-closed; it does not add Doris access to
the indexer and does not retry the task.

## Contract correction

- `goal_7_indexer_image` is now an independent Terraform input wired only to
  `module.goal7_indexer`.
- `goal_7_demo_image` is a separate Terraform input wired only to
  `module.goal7_demo`.
- When both task gates are enabled, Terraform rejects a shared image digest.
- The dedicated indexer image is built from
  `docker/Dockerfile.goal7-indexer`, whose immutable entry point is
  `python -m ask_david_goal7.indexer`.
- The Doris-aware `python -m ask_david_goal7.connected_demo` entry point remains
  in `docker/Dockerfile.goal7-runtime` for the later integrated demo only.
- Static checks reject `DORIS_FE_HOST` in the indexer Dockerfile/source and
  reject wiring the demo to the indexer image input.

No ignored `terraform.tfvars`, Terraform state, plan, ECR tag/digest, AWS
resource, Databricks object, or ECS task was changed by this remediation.

## Deterministic local image evidence

The dedicated image source aggregate covers the sorted files below. The
aggregate is the SHA-256 of newline-delimited `sha256sum` output:

- `docker/Dockerfile.goal7-indexer`;
- `opensearch/index-mapping.json`;
- all regular files under
  `packages/goal7-runtime/src/ask_david_goal7/` (excluding `__pycache__`).

| Check | Result |
| --- | --- |
| Source aggregate | PASS — `6fc7ce13b4a5a53c51124529ca483f72eb921e02d5dbf01e51ae8a72afef4207` |
| Local Docker build | PASS — `docker build --pull=false -f docker/Dockerfile.goal7-indexer -t ask-david-goal7-indexer:offline .` |
| Local image ID/manifest | PASS — `sha256:08ef16bfbd3e4dbd6a940227a6fd7afab14385644eec617d02da7c8f46714669` |
| Image user | PASS — `65532:65532` |
| Image entry point | PASS — `python -m ask_david_goal7.indexer` |
| Network-disabled import | PASS — `ask_david_goal7.indexer` imports with `--network none` |
| ECR push/scan | NOT RUN — requires separate approval |

## Offline validation

| Check | Result |
| --- | --- |
| Goal 7 static validator | PASS — `python3 scripts/validate_goal7.py` |
| Goal 7 unit/regression tests | PASS — `16 passed` |
| Ruff check | PASS |
| Ruff format check | PASS |
| Python compile check | PASS |
| Terraform formatting | PASS for modified Goal 7/network sources |
| Connected Terraform plan/apply | NOT RUN |
| ECS task retry | NOT RUN |
| Databricks/AOSS mutation | NOT RUN |

## Next approval boundary

The next actions are separate: promote the dedicated image to the existing
private ECR repository, update ignored development image inputs with both
indexer and demo digests, create/review a saved connected development plan,
apply only an approved plan, and then approve exactly one private indexer task.
None of those actions is authorized by this offline checkpoint.
