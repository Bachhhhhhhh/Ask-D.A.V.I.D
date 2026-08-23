# Goal 7 bundle deployment — 2026-08-20

## Approved deployment

The reviewed development bundle plan had SHA-256
`69ba965b1b6ed06ed82b5fb6d5aa14a94c3f5999d3f4ed0a3a9f174b128ef729` and was
approved for deployment. Its exact action set was two creates (the Goal 7 job
and its permissions), zero updates, replacements, or destroys; all existing
Goal 4/5/6 resources were no-op.

## Read-only post-deployment evidence

| Check | Result |
| --- | --- |
| Target/profile | PASS — `development` / `ask-david-development` |
| Job | PASS — `ask-david-development-goal7-document-embedding`, ID `306888706947227` |
| Tasks | PASS — `prepare_document_chunks`, `emit_vector_index_outbox`, `verify_vector_payload` |
| Warehouse | PASS — existing Serverless SQL Warehouse `757e0335c6efb51e` |
| Run-as | PASS — Terraform-created workflow service principal `b2bdec62-62db-432d-bc6f-1f92b78053b0` |
| Permissions | PASS — governance owner/admins manage, data engineers run, denied principal `CAN_VIEW` only |
| Run history | PASS — no runs returned; deployment did not execute SQL |
| Compute/AWS mutation | PASS — no new compute, Terraform, or AWS operation |

## Gate decision

Bundle deployment is **PASS**. Goal 7 remains **NOT VERIFIED** until the one
approved synthetic SQL pipeline produces governed chunks/embeddings and the
controlled OpenSearch indexing/search plus integrated Supervisor path are
verified. No job was run implicitly by deployment.
