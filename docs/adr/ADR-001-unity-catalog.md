# ADR-001: Unity Catalog as the Primary Catalog

- **Status:** Accepted
- **Decision date:** Initial architecture baseline
- **Owners:** Platform Architecture and Data Platform teams

## Context

The platform uses:

- Databricks on AWS.
- Apache Iceberg.
- Amazon S3.
- Apache Doris.
- Other AWS services.

Multiple technologies can provide catalog-like functionality, including Unity Catalog and AWS Glue.

Allowing multiple systems to independently own and mutate metadata for the same tables would introduce:

- Split authority.
- Inconsistent permissions.
- Metadata drift.
- Conflicting table versions.
- Unclear lineage.
- Difficult incident recovery.
- Ambiguous ownership.

The platform requires one primary governance and metadata authority.

## Decision

Unity Catalog is the primary catalog for governed platform data.

Unity Catalog is responsible for:

- Catalog and schema hierarchy.
- Table registration.
- View registration.
- Service-principal access.
- User and group permissions.
- Data discovery.
- Sensitivity metadata.
- Ownership.
- Lineage.
- Audit integration.
- Environment isolation.

AWS Glue may be used only for narrowly scoped AWS integrations when required.

AWS Glue must not become a competing primary catalog for the same governed tables.

Each governed table must have one declared metadata authority.

## Consequences

### Positive

- Centralized governance.
- Consistent Databricks authorization.
- Clear ownership.
- Unified lineage.
- Reduced metadata drift.
- Easier auditing.
- Stable metadata boundary for agents.
- Clear integration point for the Metadata Service.

### Negative

- External engines must use supported Unity Catalog or Iceberg interfaces.
- Some AWS-native integrations may need additional configuration.
- Catalog integration must be tested for each external engine.
- Platform availability partly depends on Unity Catalog availability.

## Implementation constraints

- Do not create unmanaged production Iceberg tables.
- Do not register the same table as independently mutable in multiple catalogs.
- Do not allow agents to query Unity Catalog directly.
- Expose metadata through the controlled Metadata Service.
- Separate development, staging, and production namespaces.
- Grants must follow least privilege.
- Catalog changes must be auditable.

## Alternatives considered

### AWS Glue as the primary catalog

Rejected because the selected platform is Databricks-centered and requires Unity Catalog governance, lineage, access control, and asset discovery.

### Multiple primary catalogs

Rejected because split metadata ownership creates ambiguity and drift.

### Custom catalog service

Rejected for the MVP because it would duplicate existing governance capabilities and increase operational complexity.

## Validation

This decision is validated when:

- Governed Iceberg tables are registered in Unity Catalog.
- Unauthorized users cannot query protected tables.
- Lineage is recorded.
- External services access metadata through approved interfaces.
- No competing mutable catalog registration exists for the same table.
