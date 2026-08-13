# Goal 5 corrected workflow retry

Date: 2026-08-13  
Scope: one approved run of the corrected Goal 5 bundle job, followed by
read-only run/task inspection. No implicit retry, redeploy, second workflow,
Terraform operation, AWS operation, or ad-hoc SQL execution was performed.

## Pre-run

- Profile: `ask-david-development`.
- Existing warehouse: `757e0335c6efb51e`, `Serverless Starter Warehouse`,
  Small/PRO, serverless enabled, STOPPED, auto-stop 10 minutes.
- Active runs for job `382877731318442`: none.
- Deployed corrected CDC SQL had already been byte-verified against the
  approved source hash `9ce80b73ec48bf0a7568fad81faf791f286dbfbae4c66ca0a9af84fe013f66fd`.

## Single run

Exactly one `run-now` was submitted for job `382877731318442`:

```text
run_id: 149148676670509
```

Task results after terminal inspection:

| Task | Result |
| --- | --- |
| `create_goal5_tables` | SUCCESS |
| `ingest_structured_csv` | SUCCESS |
| `ingest_document` | SUCCESS |
| `ingest_cdc` | SUCCESS |
| `verify_goal5_outputs` | FAILED |
| `verify_goal5_idempotency` | SKIPPED — UPSTREAM_FAILED |

The run terminated `FAILED` with:

```text
[USER_RAISED_EXCEPTION] CDC current state must reflect UPDATE and DELETE tombstone semantics SQLSTATE: P0001
```

The failed task run was `457857084612006`; its output was inspected
read-only. No further connected operation was started after the failure.

## Analysis and boundary

The CDC ingestion task itself succeeded, including the corrected shared temp
view. The failure is in the downstream acceptance assertion, not a source
access or CDC SQL-scope failure. Offline source inspection shows the
assertion compares JSON `metric_value` to the exact string `'120'` while the
declared payload field is `DOUBLE`; the live serialized representation may be
`120.0`. This is an offline hypothesis until a reviewed remediation changes
the assertion and its regression contract; no live table query was run after
the failure.

Goal 5 remains unverified. The next step is an offline-only remediation plan
for the deterministic output assertion, followed by static/regression
validation and a fresh strict bundle validation. A new workflow run requires
separate approval after those gates.
