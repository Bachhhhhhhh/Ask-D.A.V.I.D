# Goal 6 Phase 6-13 audit contract — offline source/design review

Date: `2026-08-19`

Status: `OFFLINE REVIEW COMPLETE — NO SOURCE OR CLOUD MUTATION`

## Durable connected evidence reviewed

Two separately approved, no-retry audit executions failed with the same
sanitized marker:

- prior ID `5f3d5b10fd5b4a08-a24906b966376c6b` — task
  `732ef6a88ea046388810c15f8f77244e`, exit `1`;
- fresh ID `2259b82920f9455a-a1845feae8876892` — task
  `ff6cdedf3a7c43038568c5c03544d5e3`, exit `1`.

Both CloudWatch streams reported:

```json
{"goal":"goal-06","operation":"audit-verify","status":"audit-row-not-found"}
```

The fresh-ID attempt rules out the narrow stale-query/timing-only hypothesis.
The evidence still does not prove a privilege, query-ID-format, or Doris
version defect.

## Repository source review

The current admin refresh migration executes
`SET GLOBAL enable_audit_plugin = true` in
`doris/schemas/02_readonly_workload_and_audit.sql`. The admin runner then emits
only `admin-refresh,status=completed`; it does not read back the setting or
assert that `__internal_schema.audit_log` contains rows.

The audit runner currently:

1. accepts an exact `EXPECTED_QUERY_ID`;
2. polls `internal.__internal_schema.audit_log` for that ID;
3. checks identity, target statement, `EOF`, numeric `query_time`, and
   `goal6_readonly` workload evidence.

Therefore `audit-row-not-found` conflates at least two conditions: an audit
plugin/table with no visible rows and an exact-ID lookup miss. The current
offline tests mock a row and cannot distinguish those live states.

Official Doris documentation confirms that `LAST_QUERY_ID()` returns the
current user's last query ID and that `audit_log` is the `__internal_schema`
system table containing `query_id`, `time`, `user`, `state`, `query_time`, and
`workload_group`:

- <https://doris.apache.org/docs/4.x/sql-manual/sql-functions/scalar-functions/system-functions/last-query-id/>
- <https://doris.apache.org/docs/dev/admin-manual/system-tables/internal_schema/audit_log/>

These contracts support the existing exact-ID design but do not prove that the
live plugin is enabled or producing rows.

## Minimal source remediation proposal

This review proposes, but does not implement, the following bounded change:

1. After enabling the audit plugin in the version-controlled admin migration,
   read back `SHOW VARIABLES LIKE 'enable_audit_plugin'` and fail closed unless
   it reports enabled.
2. Extend the audit runner with read-only preconditions that distinguish
   `audit-plugin-disabled`, `audit-log-unreadable`, and `audit-log-empty` from
   `audit-row-not-found`; never weaken exact query-ID correlation.
3. Keep the existing identity/target/`EOF`/duration/workload assertions and
   keep the admin secret read-only for this operation.
4. Add static and mocked regression tests for every new failure class, update
   the runbook/report, then rebuild and scan a new immutable image through
   separate approvals.
5. Only after the new image is registered should a new approved admin refresh,
   fresh result-contract task, and audit task be considered.

No privilege broadening, public exposure, Doris write-back, arbitrary SQL, or
fallback “latest row” matching is acceptable. A latest-row fallback would not
prove correlation to the representative result and is explicitly rejected.

## Acceptance state

Phase 6-13 remains **UNVERIFIED**. This document is an offline design review,
not implementation or connected evidence. The next approval boundary is
offline implementation of the bounded diagnostic/guard changes above; no
connected task should run before that review is accepted.
