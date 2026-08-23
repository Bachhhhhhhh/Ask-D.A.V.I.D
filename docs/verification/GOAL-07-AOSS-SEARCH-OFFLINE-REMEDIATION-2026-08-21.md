# Goal 7 AOSS vector-search offline remediation — 2026-08-21

## Approved boundary

This checkpoint was approved for source, regression-test, and documentation
changes plus offline validation only. No AOSS/AWS/Databricks call, image
build/push, ignored Terraform-input update, Terraform plan/apply/destroy,
bundle operation, SQL/job execution, or ECS task retry was performed.

## Failure evidence addressed

The one approved private revision-5 indexer task stopped with exit code `1`
after the corrected Databricks embedding parser succeeded. CloudWatch reported:

`RuntimeError: AOSS vector search failed`

The deployed search path did not include the AOSS HTTP status or bounded error
body in its exception/log, so the exact live rejection remains unverified.

## Remediation implemented

`AossClient.search()` now:

1. converts non-2xx/non-object responses into the existing bounded `_failure`
   contract with HTTP status and whitelisted AOSS error fields;
2. logs only bounded non-secret diagnostics (operation/status/error detail);
3. validates the nested `hits.hits` response shape without unsafe chained
   access; and
4. fails closed with a bounded shape error for malformed successful responses.

No raw response body, vector, credential, or SQL result is logged.

Regression tests cover an HTTP error with type/reason details, a valid hits
response, and malformed hits shape. The static validator requires the search
diagnostic markers.

## Offline verification

| Check | Result |
| --- | --- |
| Goal 7 static validator | PASS — `python3 scripts/validate_goal7.py` |
| Focused Goal 7 tests | PASS — 29 passed |
| Python compilation | PASS — `python3 -m compileall -q ...` |
| `git diff --check` | PASS |
| Ruff lint/format | UNVERIFIED — `ruff` is not installed in this environment |
| Full repository unit suite | UNVERIFIED — optional `pydantic` is not installed |
| AOSS/AWS/Databricks connected operation | NOT RUN — prohibited at this boundary |

## Current checkpoint

Goal 7 remains **UNVERIFIED**. The next step requires a separately approved
image build/push from this remediation, digest-only task-definition plan/apply,
and one no-retry private task to capture the real AOSS search error or pass the
index-and-search contract.
