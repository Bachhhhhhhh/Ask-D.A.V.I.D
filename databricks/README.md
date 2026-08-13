# Governed Databricks lakehouse assets

This directory contains declarative development assets for the verified Goal 4
foundation and the synthetic-only Goal 5 MVP. Unity Catalog is the governance
authority and S3 remains the durable storage layer. Goal 4's existing tables
are managed Delta UniForm with Iceberg-compatible metadata according to the
authoritative Tables API; they are not described as native Iceberg. Goal 5
accepts either native managed `ICEBERG` or managed `DELTA_UNIFORM_ICEBERG` and
records the actual observed format.

## Layout

- `databricks.yml` is the single Declarative Automation Bundle root.
- `bundles/goal_04_lakehouse/resources.yml` declares one authorized synthetic
  workflow, read-only history/lineage verification jobs, and two expected-
  failure authorization jobs.
- `sql/goal_04/` contains deterministic neutral synthetic SQL. The seven
  physical-table declarations use `USING ICEBERG` and deliberately omit
  `LOCATION`. A pre-write task now fails unless SQL metadata reports exactly
  seven managed Iceberg tables. Final acceptance additionally requires the raw
  Tables API inventory verifier because Delta UniForm can expose compatible
  Iceberg metadata while remaining `data_source_format = DELTA`.
- `sql/goal_04/remediation/` contains only a non-executable exclusion marker.
  Executable remediation SQL is forbidden there; the explicit bundle exclude
  must remain so future approval-only remediation cannot be synchronized.
- `bundles/goal_05_ingestion/resources.yml` declares the reduced synthetic
  structured/document/CDC ingestion workflow. It reuses the existing
  Serverless SQL Warehouse and does not create compute.
- `sql/goal_05/` contains only neutral fixture ingestion, governed managed
  tables, quality/provenance assertions, and read-only idempotency checks.

The bundle always references the existing approved Serverless SQL Warehouse.
It contains no cluster or warehouse resource. Terraform supplies the
warehouse, catalog, service-principal, and S3-probe inputs before a future
approved deployment. The Databricks CLI selects the approved workspace and
OAuth authentication exclusively through the named development profile; the
bundle does not declare or interpolate a workspace host. No OAuth token or
cloud credential is a bundle variable.

The production-mode development target explicitly places synchronized bundle
files under the governance administrator's user-scoped workspace path:

```text
/Workspace/Users/${var.governance_admin_user_name}/.bundle/${bundle.name}/${bundle.target}
```

The bundle must not deploy from `/Workspace/Shared`, where top-level bundle
permissions can conflict with shared-folder permissions. Its top-level bundle
ACL explicitly declares the same governance administrator as `CAN_MANAGE`, so
strict validation matches the permission inherited from that user's folder.

## Offline validation

Run the credential-free static contract:

```powershell
.\scripts\dev.ps1 databricks-static
```

or:

```bash
make databricks-static
```

This check performs no authentication, deployment, or SQL execution. A future
connected `databricks bundle validate`, bundle deployment, authorized SQL run,
and each negative run require their own approval boundaries documented in
`docs/runbooks/GOAL-04-DATABRICKS-LAKEHOUSE.md`.

Validate a sanitized Goal 4 native-Iceberg inventory offline with:

```bash
python scripts/verify_goal4_table_inventory.py /path/to/sanitized-table-inventory.json
```

This verifier performs no cloud call. It fails closed unless the exact seven
project tables are Unity Catalog `MANAGED` native `ICEBERG` tables with no
Delta properties.

Validate a sanitized Goal 5 inventory against the accepted format policy with:

```bash
python scripts/verify_goal5_table_inventory.py /path/to/sanitized-goal5-inventory.json
```

This verifier accepts native `ICEBERG` or managed `DELTA` with explicit
UniForm Iceberg properties and an Iceberg metadata path. Plain `DELTA` fails.
