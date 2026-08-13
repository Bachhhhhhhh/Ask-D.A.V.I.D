# Goal 5 Phase 5-3 connected revalidation and saved plan

Date: 2026-08-12  
Scope: read-only revalidation and one saved development Terraform plan only.

This checkpoint was executed after explicit approval for the Goal 5 Phase 5-3
connected read-only revalidation and saved plan. It did not apply the plan,
deploy a Databricks bundle, run a SQL/job task, create compute, or mutate AWS or
Databricks resources.

## Revalidation

| Check | Result | Evidence |
| --- | --- | --- |
| AWS caller account | PASS | `aws sts get-caller-identity` returned account `736956442295`; no credentials were printed. |
| AWS region | PASS | Approved development region is `ap-southeast-1`; Terraform variables/backend and the Unity Catalog metastore agree. |
| Databricks CLI | PASS | CLI `1.11.0`; named profile `ask-david-development` authenticated through the native OAuth keyring. |
| Workspace | PASS | Profile host is the approved development workspace; workspace ID `7474644358733471`; principal is the existing development governance administrator. |
| Unity Catalog metastore | PASS | Metastore `3a7f7e7a-680b-4bd6-907a-6d5e77b43178`, name `metastore_aws_ap_southeast_1`, region `ap-southeast-1`; existing workspace association retained. |
| Catalog inventory | PASS | Read-only catalog listing retained `workspace`, `system`, `samples`, `ml_model_store`, and `ask_david_development`; no catalog mutation occurred. |
| Existing SQL warehouse | PASS | Warehouse `757e0335c6efb51e`, `Serverless Starter Warehouse`, PRO/Small, serverless enabled, auto-stop 10 minutes, state `STOPPED` at inspection. |
| Goal 5 source-object flag | PASS | `goal_5_source_objects_enabled` is absent from ignored `terraform.tfvars` and therefore remains false by default; the plan enabled it only through an explicit transient `-var` argument. |

## Saved plan

Terraform `1.11.4` was used. Backend initialization read the configured
development remote state. The plan was generated from the repository root with:

```text
terraform -chdir=infrastructure/environments/development plan \
  -input=false -refresh=true -var-file=terraform.tfvars \
  -var=goal_5_source_objects_enabled=true \
  -out=/tmp/goal5-development-repo.tfplan
```

Saved plan artifact:

```text
SHA-256  457d6f7a50be5b7cca1ed6240b9cab7c5e16bb9c0ef4242d67d520e21f1b8474
Path     /tmp/goal5-development-repo.tfplan
```

`terraform show -json` independently confirmed the complete non-no-op action
set:

| Action | Count | Addresses |
| --- | ---: | --- |
| create | 3 | `aws_s3_object.goal5_structured_source[0]`, `aws_s3_object.goal5_document_source[0]`, `aws_s3_object.goal5_cdc_source[0]` |
| update | 0 | — |
| replace | 0 | — |
| destroy | 0 | — |

The three creates are limited to the approved development synthetic fixtures:

- CSV structured source in the existing raw bucket;
- neutral Markdown document in the existing documents bucket;
- JSONL CDC source in the existing raw bucket.

Each planned object uses the existing storage KMS key, SSE-KMS, synthetic-only
tags, and the Goal 5 prefixes. No new bucket, key, IAM role, catalog, schema,
warehouse, cluster, production resource, or Goal 6+ resource is planned.

## Verification boundary

The plan is **SAVED / AWAITING APPLY APPROVAL**, not applied and not a Goal 5
verification result. The following remain unverified and intentionally were not
run at this checkpoint:

- Terraform apply or destroy;
- S3 object existence/content and source-preservation checks;
- strict connected bundle validation or deployment;
- SQL/job execution and managed-table creation;
- Raw/Curated/Business output, quality, lineage, idempotency, or Tables API
  evidence.

The next separate approval is for applying exactly the saved plan above. Any
action other than the three creates, or any replacement/destroy, requires a new
review.
