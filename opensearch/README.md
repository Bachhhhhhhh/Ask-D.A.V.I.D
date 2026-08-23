# Goal 7 OpenSearch Serverless retrieval layer

Goal 3 provides the reusable private AOSS VPC endpoint plus encryption and
network policies. Goal 7 adds an explicitly gated, Terraform-managed
`VECTORSEARCH` collection and least-privilege data policy; the default gate is
off and no collection exists merely because this source is present.

`index-mapping.json` is the single 1024-dimensional vector-index contract.
The controlled indexing service owns deterministic upserts from the governed
Databricks outbox. OpenSearch stores only derived chunks, vectors, metadata,
and role filters; original documents remain in approved S3/Unity Catalog
storage. No agent imports an OpenSearch SDK or receives its credentials.

The collection/index and data-plane indexing are not connected-verified yet.
They require a saved Terraform plan and explicit approval before any cloud
mutation.
