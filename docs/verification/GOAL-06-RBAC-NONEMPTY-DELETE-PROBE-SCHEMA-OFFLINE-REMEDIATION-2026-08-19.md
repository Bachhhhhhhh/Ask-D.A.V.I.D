# Goal 6 non-empty DELETE probe schema remediation — offline — 2026-08-19

## Trigger

The one-shot revision-13 admin refresh failed before completion because the
disposable authorization probe declared `probe_id TINYINT` but attempted to
seed upper sentinel `128`. Signed Doris `TINYINT` cannot represent that value;
the connected failure report records error code `1105` and the `TINYINT` marker.

## Remediation contract

The probe must keep its fixed lower/target/upper safety contract:

- lower sentinel `126` exists;
- reserved DELETE target `127` is absent;
- upper sentinel `128` exists.

The probe key is therefore widened to `SMALLINT`. The admin runner now executes
the versioned `04_recreate_authorization_probe.sql` migration after the base
schema. The migration drops and recreates only the disposable internal probe,
then seeds the two neutral sentinels. It never touches the authoritative
Unity Catalog/S3 source, serving metrics, or any AWS resource.

Recreation is intentional and deterministic: it avoids relying on an
asynchronous in-place key-column schema change and guarantees that repeated
controlled admin refreshes converge to the exact disposable probe state.
Apache Doris documents `MODIFY COLUMN` as an asynchronous schema-change path
for existing key columns; this remediation uses a controlled disposable-table
recreation instead. Reference:
<https://doris.apache.org/docs/4.x/table-design/schema-change/>.

## Offline implementation

Changed only repository-managed Goal 6 schema, runner contract, static
validation, regression tests, plan/runbook text, and durable reports:

- `doris/schemas/01_serving_database.sql` declares `SMALLINT` and no longer
  seeds an out-of-range value during base schema creation;
- `doris/migrations/04_recreate_authorization_probe.sql` performs the scoped
  disposable recreation and seeds `126`/`128`;
- `docker/doris-verifier/doris-admin-refresh` executes that migration before
  grants and refresh;
- `scripts/validate_goal6.py` and Goal 6 tests enforce the migration/order and
  SMALLINT contract;
- the Goal 6 plan/runbook and PROJECT_STATUS describe the new contract.

## Offline validation

All applicable focused gates passed:

```text
sh -n docker/doris-verifier/doris-admin-refresh                  PASS
python3 scripts/validate_goal6.py                                 PASS
python3 -m pytest -o addopts='' tests/unit/test_goal6_static.py \
  tests/unit/test_goal5_static_goal6_regression.py -q              45 passed
git diff --check                                                   PASS
```

Pytest emitted only two cache-permission warnings because the environment
cannot write `.pytest_cache`; no test failed.

No image was built or pushed. No Terraform plan/apply/destroy, ECS task,
Doris SQL, Databricks operation, AWS mutation, bundle deployment, or source
table operation was performed for this remediation.

## Current state

This remediation is implemented and offline-validated only. A new image
build/promotion, task-definition plan, admin refresh, and RBAC verifier run
each require their own explicit approval.
