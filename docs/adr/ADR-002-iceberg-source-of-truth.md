# ADR-002: Amazon S3 and Apache Iceberg as the System of Record

- **Status:** Accepted
- **Decision date:** Initial architecture baseline
- **Owners:** Platform Architecture and Data Platform teams

## Context

The platform requires:

- Large-scale analytical storage.
- Open table interoperability.
- Historical snapshots.
- Schema evolution.
- Rebuildable serving systems.
- Multi-engine access.
- Separation between authoritative storage and query acceleration.

Databricks performs primary data engineering and analytics.

Apache Doris provides low-latency serving.

The platform must ensure that serving systems do not become the only copy of business data.

## Decision

Amazon S3 and Apache Iceberg form the structured-data system of record.

Amazon S3 stores the physical data and metadata files.

Apache Iceberg defines the authoritative table abstraction, including:

- Schema.
- Partitions.
- Snapshots.
- Manifests.
- Atomic table updates.
- Schema evolution.
- Historical versions.
- Time travel.

Authoritative structured data must be represented in governed Iceberg tables.

The standard lifecycle is:

```text
Source
  ↓
Raw / Bronze Iceberg
  ↓
Curated / Silver Iceberg
  ↓
Business / Gold Iceberg
  ↓
Serving and analytical consumers
```

## Consequences

### Positive

- Open table format.
- Multi-engine interoperability.
- Historical snapshots.
- Clear source of truth.
- Rebuildable downstream systems.
- Reduced serving-layer lock-in.
- Separation of storage and compute.
- Better support for audit, replay, and backfill.

### Negative

- Iceberg metadata maintenance is required.
- Small-file management must be operated.
- Table optimization must be automated.
- External-engine compatibility must be tested.
- S3 query latency may be slower than dedicated serving systems.

## Implementation constraints

- Unity Catalog is the primary catalog.
- Doris must be rebuildable from Iceberg.
- Agents should query Gold tables or approved semantic views.
- Direct agent access to Raw and Curated layers is prohibited by default.
- Every pipeline must preserve source and run provenance.
- Table-maintenance procedures must be documented.
- Snapshot-retention and recovery policies must be defined.
- No serving system may be the only copy of authoritative data.

## Alternatives considered

### Delta Lake as the system of record

Rejected for this architecture baseline because Apache Iceberg was selected as the open table format for broader engine interoperability.

### Doris as the system of record

Rejected because Doris is selected for low-latency serving, not authoritative historical storage.

### Plain Parquet without a table format

Rejected because it lacks the required transactional metadata, snapshots, schema evolution, and managed-table semantics.

## Validation

This decision is validated when:

- Synthetic data flows from Raw to Curated to Business Iceberg tables.
- Snapshot history can be inspected.
- A previous snapshot can be queried or restored in a controlled test.
- Doris serving data can be removed and rebuilt from Iceberg.
- No authoritative dataset exists only in Doris.
