# Goal 7 integrated-demo per-agent diagnostics — offline remediation — 2026-08-22

## Approved boundary

This remediation is source/tests/static-validation/documentation-only. It does
not build or push an image, change ignored Terraform inputs, run Terraform,
call AWS or Databricks, deploy a bundle, or run an ECS task.

## Blocker addressed

The connected integrated-demo task after FE/BE startup reached the aggregate
check but exited with only:

`connected Goal 7 integrated demo did not complete all agents`

The entry point had already collected the three `AgentResult` objects, but it
discarded their individual status and error before raising. That evidence was
insufficient to distinguish a structured, RAG, or analytics failure.

## Offline change

`connected_demo.py` now emits one bounded JSON marker,
`integrated-demo-agent-diagnostics`, immediately before an aggregate failure.
For exactly `structured`, `unstructured`, and `analytics`, the marker contains
only:

- `status`;
- `error_present`;
- a fixed `error_category` label.

Raw error text, summaries, data, provenance, SQL, endpoints, credentials,
document content, vectors, and response bodies are excluded. Known
repository-owned messages map to stable categories; unknown messages become
`unclassified_error`; a missing result becomes `missing_result`.

Regression coverage verifies both agent identification and secret-safe
fail-closed behavior. The static validator requires the diagnostic helper and
marker contract.

## Verification status

Offline validation completed:

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal7.py` | PASS — Goal 7 static validation passed |
| `pytest -p no:cacheprovider -o addopts='' -q tests/unit/test_goal7_static.py` | PASS — 34 tests passed |
| `python3 -m compileall -q packages/goal7-runtime/src/ask_david_goal7 scripts/validate_goal7.py tests/unit/test_goal7_static.py` | PASS |
| `git diff --check` | PASS |
| Ruff | UNVERIFIED — executable not installed |
| mypy | UNVERIFIED — executable not installed |

No AWS, Databricks, Terraform, ECS, ECR, SQL, AOSS, or bundle operation was
run. This remediation does not prove the connected demo itself; Goal 7 remains
**UNVERIFIED** pending a separately approved replacement image, task-definition
update, and exactly one connected retry.
