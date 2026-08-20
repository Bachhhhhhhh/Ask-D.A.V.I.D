# Goal 6 Apache Doris serving layer

This directory holds versioned, synthetic-only Apache Doris artifacts for the
development serving checkpoint. Doris is a rebuildable, internal serving copy;
it never owns the source-of-truth data path.

- `catalogs/`: secret-free Unity Catalog Iceberg REST template, rendered only
  by the private one-off refresh task.
- `schemas/`, `materialized_views/`, and `migrations/`: internal Doris-only
  DDL, read-only workload/audit controls, controlled refresh, and separately
  approved rebuild definitions.
- `tests/`: static contract material; no direct host-to-Doris access exists.

The selected development topology is a private one-FE/one-BE cluster using
`m7i.xlarge` for each node. No resource is enabled until a reviewed connected
Terraform plan is separately approved.
