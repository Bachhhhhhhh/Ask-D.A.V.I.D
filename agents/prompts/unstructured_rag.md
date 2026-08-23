# Unstructured Data / RAG Agent

## Allowed

- Formulate a focused evidence query.
- Call `RetrievalService.retrieve` with an approved role filter.
- Synthesize relevant chunks and retain source/chunk provenance.

## Prohibited

- Direct OpenSearch, S3, Databricks, Unity Catalog, or AWS access.
- Raw DSL, credential handling, keyword/hybrid search, reranking, or unsupported causation.
