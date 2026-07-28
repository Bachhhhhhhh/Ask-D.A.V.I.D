# ADR-004: Amazon OpenSearch Serverless as the Vector Retrieval Layer

- **Status:** Accepted
- **Decision date:** Initial architecture baseline
- **Owners:** Platform Architecture and AI Platform teams

## Context

The platform requires semantic and hybrid retrieval over:

- Documents.
- Reports.
- Meeting notes.
- Policies.
- Operational text.
- Synthetic evidence during the infrastructure phase.

The retrieval layer must support:

- Vector search.
- Keyword search.
- Hybrid retrieval.
- Metadata filtering.
- Access-control filtering.
- Citation metadata.
- Document versioning.
- Managed scalable infrastructure.

Original documents must remain independently stored and recoverable.

## Decision

Amazon OpenSearch Serverless is the approved vector and document retrieval platform.

Original documents are stored on Amazon S3.

OpenSearch Serverless stores derived retrieval assets:

- Document chunks.
- Embeddings.
- Searchable text.
- Metadata.
- ACL fields.
- Citation fields.
- Document-version fields.

The Unstructured Data Agent accesses OpenSearch only through the controlled Retrieval Service.

## Required chunk metadata

Every indexed chunk must include:

- Chunk ID.
- Document ID.
- Document version.
- Title.
- Content.
- Page or section.
- Source URI or document reference.
- Source system.
- Effective date.
- Classification.
- Allowed roles or groups.
- Embedding.
- Processing version.

## Consequences

### Positive

- Managed AWS-native retrieval service.
- Vector and keyword search.
- Scalable retrieval infrastructure.
- Network and data-access policies.
- Metadata filtering.
- Separation between original documents and indexes.
- Rebuildable derived index.

### Negative

- OpenSearch-specific mapping knowledge is required.
- Search relevance requires evaluation and tuning.
- Index cost must be monitored.
- ACL filtering must be carefully tested.
- Document-version replacement must be implemented.
- Retrieval quality is not guaranteed solely by infrastructure selection.

## Implementation constraints

- Original documents remain on S3.
- OpenSearch indexes are derived and rebuildable.
- Retrieval Service must enforce ACL filters.
- Authorization must occur before chunks are returned to an agent.
- Citation-metadata completeness is mandatory.
- Deleted documents must disappear from active retrieval.
- Re-indexing must support document versions.
- Query and retrieval metrics must be observable.
- Agents must not hold OpenSearch credentials.

## Alternatives considered

### Databricks AI Search

Considered but not selected because the architecture baseline requires OpenSearch Serverless as the retrieval platform.

### Self-hosted vector database

Rejected for the MVP because of increased operational burden.

### Database-native vector extensions

Rejected as the primary knowledge layer because the platform requires a dedicated scalable retrieval service with hybrid search and document metadata.

## Validation

This decision is validated when:

- Synthetic documents are stored on S3.
- Derived chunks are indexed in OpenSearch Serverless.
- Authorized users retrieve expected chunks.
- Unauthorized users retrieve zero restricted chunks.
- Citations contain document and page metadata.
- Updated documents replace stale active chunks.
- The index can be rebuilt from S3 documents and processing metadata.
