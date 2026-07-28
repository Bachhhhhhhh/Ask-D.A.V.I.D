# ADR-003: Apache Doris as the Low-Latency OLAP Serving Layer

- **Status:** Accepted
- **Decision date:** Initial architecture baseline
- **Owners:** Platform Architecture and Data Platform teams

## Context

Iceberg on S3 provides the system of record but may not meet every low-latency, high-concurrency, interactive analytical requirement.

The AI platform requires fast access to:

- Frequently used metrics.
- Semantic marts.
- Filtered aggregates.
- Interactive comparisons.
- Dashboard-style queries.
- Repeated agent queries.

A serving engine is required without changing the source-of-truth decision.

## Decision

Apache Doris is the approved low-latency OLAP serving layer.

Doris serves:

- Frequently queried metrics.
- Approved semantic marts.
- Precomputed aggregates.
- High-concurrency analytical queries.
- Agent-oriented low-latency datasets.

Doris is not a source of truth.

Every Doris dataset must have:

- An Iceberg source.
- A documented refresh strategy.
- A freshness SLA.
- A rebuild procedure.
- Validation against Iceberg.
- An owner.
- Auditability.

## Query routing

The Structured Data Agent should use Doris when:

- An approved serving mart exists.
- The required data is fresh enough.
- The query matches supported semantic structures.
- Low latency is required.

It should use Databricks SQL and Iceberg when:

- Full historical detail is required.
- The dataset is not materialized in Doris.
- The query is ad hoc.
- Large-scale processing is required.
- Iceberg snapshot history is required.

## Consequences

### Positive

- Low-latency OLAP.
- Higher interactive concurrency.
- Reduced repeated scans over S3.
- Clear serving-layer responsibility.
- Faster agent responses.
- Semantic-mart support.
- Rebuildability from the system of record.

### Negative

- Additional infrastructure to operate.
- Data duplication between Iceberg and Doris.
- Refresh-lag management.
- Consistency validation is required.
- Schema changes must be coordinated.
- Query routing becomes more complex.

## Implementation constraints

- Doris agent users must be read-only.
- DDL and DML from agents are prohibited.
- Query Service is the only approved agent-facing Doris interface.
- Resource groups and timeouts must be configured.
- Serving-table definitions must be version controlled.
- Refresh lag must be observable.
- Rebuild tests must be automated.
- Doris must never be used to reconstruct Iceberg authoritative history.

## Alternatives considered

### ClickHouse

Considered suitable for low-latency analytics, but Apache Doris was selected for this platform baseline.

### Direct Iceberg queries only

Rejected because the platform requires a dedicated low-latency serving path for frequent and concurrent queries.

### Databricks SQL only

Rejected as the only serving path because the architecture requires a distinct Doris-based OLAP serving layer.

## Validation

This decision is validated when:

- A benchmark dataset is materialized from Iceberg into Doris.
- Doris meets the defined query-latency target.
- The dataset can be deleted from Doris and rebuilt from Iceberg.
- Counts and checksums match expected source results.
- Agent queries are read-only and pass through Query Service.
- Refresh lag is measured.
