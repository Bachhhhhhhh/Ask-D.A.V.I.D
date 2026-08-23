# Goal 7 AOSS search content-type offline remediation — 2026-08-21

## Status

**OFFLINE REMEDIATION IMPLEMENTED AND VALIDATED — NO CONNECTED RETRY**

The one approved private Goal 7 indexer task reached the AOSS data plane and
stopped with exit code `1`. Its bounded CloudWatch log reported:

```text
AOSS vector search failed: HTTP 406; error=Content-Type header application/x-www-form-urlencoded is not supported
```

Connected evidence for that task:

- account/region: `736956442295` / `ap-southeast-1`;
- task definition: `ask-david-development-goal7-indexer:6`;
- task ARN suffix: `3318bbe49a094b818b38cffe957a09f9`;
- image digest: `sha256:da06c4e719e001edc74f837ae65e1a9b91737f7503c615058595a3b5f30e46c0`;
- private subnet/IP: `subnet-034f5f1c9bca753f1` / `10.42.19.124`;
- task security group: `sg-0ff2bcb1d5175c931`;
- final ECS result: `STOPPED`, `EssentialContainerExited`, exit `1`;
- no retry was launched.

## Root cause

`AossClient.search()` encoded a JSON request body but called `_request()` without
an explicit media type. Python `urllib` therefore supplied its default
`application/x-www-form-urlencoded` content type when sending the body. AOSS
rejected the request at HTTP content negotiation with `406`; this was not an
ENI, SG, IAM, SigV4, embedding, or index-mapping failure.

## Remediation

- The vector-search call now explicitly sends `application/json`.
- `_request()` fails closed when a non-empty body has no explicit content type,
  preventing future silent `urllib` form-encoding defaults.
- The search regression test captures the request media type and validates the
  role-filter body.
- A regression test proves body-bearing requests without a media type fail
  before credentials/network access.
- Existing JSON and NDJSON call-site media types remain unchanged.

No AOSS collection/index/document mutation, image build/push, Terraform,
Databricks, bundle/SQL operation, or ECS retry occurred in this checkpoint.

## Offline verification

| Check | Result |
| --- | --- |
| Goal 7 static validator | PASS — `python3 scripts/validate_goal7.py` |
| Focused Goal 7 tests | PASS — 30 passed |
| Python compilation | PASS — `python3 -m compileall -q packages/goal7-runtime/src scripts tests/unit/test_goal7_static.py` |
| `git diff --check` | PASS |
| Ruff lint/format | UNVERIFIED — `ruff` is not installed |
| Full repository unit suite | UNVERIFIED — optional `pydantic` is unavailable |
| Connected AWS/Databricks/AOSS operation | NOT RUN |

## Next checkpoint

Goal 7 remains **UNVERIFIED**. The next separately approved boundaries are:
image build/push and digest update, a task-definition-only saved Terraform
plan/apply, and exactly one private no-retry indexer task.
