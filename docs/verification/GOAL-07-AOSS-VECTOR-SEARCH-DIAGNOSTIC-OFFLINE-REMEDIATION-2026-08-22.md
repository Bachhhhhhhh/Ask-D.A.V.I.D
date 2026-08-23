# Goal 7 AOSS vector-search diagnostic offline remediation — 2026-08-22

## Scope

This remediation addresses the latest private indexer failure, which reached
the AOSS vector-search request but emitted only a generic
`AOSS vector search failed` message. The approved scope is source, regression
tests, and documentation only.

No AWS, AOSS, Databricks, ECS, ECR, Terraform, bundle, SQL, or task operation
was performed for this remediation.

## Implemented contract

`AossClient` now:

- converts URL/transport failures into a bounded internal transport diagnostic;
- preserves bounded HTTP status and AOSS error type/reason details;
- reports only JSON container types for malformed search responses;
- records expected-chunk versus returned-hit counts when the indexer acceptance
  assertion fails.

Diagnostics never include endpoint URLs, request bodies, embedding vectors,
credentials, tokens, or arbitrary response content. The indexer remains
private, role-filtered, synthetic-only, and write-capable only through its
existing controlled outbox flow.

## Verification status

| Check | Status | Evidence |
| --- | --- | --- |
| Source change is offline-only | PASS | `packages/goal7-runtime/.../indexer.py` |
| Transport diagnostic is bounded | PASS | `transport_error=<exception type>` only |
| HTTP error detail remains bounded | PASS | existing `_error_detail` contract and regression test |
| Malformed response shape is diagnosable | PASS | `_response_shape` and regression test |
| Empty/mismatched acceptance is diagnosable | PASS | expected/returned count log contract |
| Connected AOSS behavior | UNVERIFIED | requires a separately approved replacement image and one-shot task |
| Goal 7 verified | NO | integrated acceptance remains incomplete |

## Next approval boundary

The next steps require separate approval: build and scan the replacement
indexer image, push it to immutable ECR, update the ignored development digest,
create/review a saved Terraform task-definition plan, apply only that plan,
then run exactly one private indexer task. No retry is implicit.
