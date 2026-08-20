# Goal 6 Phase 6-13 audit-row-not-found — offline remediation plan

Date: `2026-08-19`

Status: `OFFLINE ANALYSIS COMPLETE — NO SOURCE OR CLOUD MUTATION`

## Observed failure

The first approved Phase 6-13 audit task used the previously recorded result
query ID `5f3d5b10fd5b4a08-a24906b966376c6b`. The task stopped with exit code 1
and emitted only:

```json
{"goal":"goal-06","operation":"audit-verify","status":"audit-row-not-found"}
```

The failure is durable evidence that the exact ID was absent from the audit
runner's bounded lookup. It is not evidence of a privilege bypass, an audit
plugin failure, or a query-ID format mismatch by itself.

## Source analysis

The current result runner emits `executed_query_id` from `LAST_QUERY_ID()` in
the same MariaDB session as the representative serving query. The current
audit runner receives that ID through `EXPECTED_QUERY_ID`, then polls
`internal.__internal_schema.audit_log` for an exact `query_id` match and checks
identity, target table, successful `EOF` state, numeric query duration, and
`goal6_readonly` workload-group evidence. The admin-operation wrapper does not
retry and does not override any credential or network setting.

Offline evidence cannot determine whether the old row was absent because of
retention/timing, a query-ID correlation semantic, or another live Doris audit
condition. No executable source change is justified by the failure alone.

## Minimal fail-closed remediation sequence

1. Keep the current image, task definitions, privileges, network boundary, and
   audit SQL unchanged.
2. Under a separate approval, run exactly one fresh private read-only result
   contract task from verifier revision `15`. Capture only its sanitized
   `executed_query_id`; do not retry or mutate data.
3. Under a separate approval, run exactly one private admin audit task from
   admin revision `15` using that fresh query ID. Require the existing exact
   identity/target/state/duration/workload checks and stop on any failure.
4. If the fresh-ID audit passes, use that connected evidence for Phase 6-13.
5. If the fresh-ID audit still returns `audit-row-not-found`, stop again and
   perform a new offline source/design review before changing the audit query;
   do not broaden privileges or weaken exact correlation to make the test pass.

This sequence tests the smallest evidence-based hypothesis (the prior query
row was stale or outside the audit retention/timing window) without changing
the architecture or adding cloud resources.

## Explicit non-goals

- No source, test, or executable SQL change is included in this checkpoint.
- No connected SQL, ECS task, Terraform, ECR, Databricks, or AWS operation is
  authorized by this plan.
- No audit acceptance claim is made until a fresh query ID is correlated by a
  successful connected run.

## Fresh-ID result

The separately approved fresh verifier task produced query ID
`2259b82920f9455a-a1845feae8876892`, but the separately approved audit task
using that fresh ID also returned `audit-row-not-found` and exited 1. The
retention/timing-only hypothesis is therefore rejected. The failure still does
not justify guessing at a privilege or query-ID-format fix.

## Acceptance state

Phase 6-13 remains **UNVERIFIED**. The next approval boundary is one fresh
offline source/design review for the audit contract. No additional connected
task should run until that review is complete and separately approved.
