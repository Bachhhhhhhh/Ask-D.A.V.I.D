# Goal 5 Phase 5-4 source-object apply and read-back

Date: 2026-08-12  
Scope: apply of the previously reviewed saved Terraform plan and immediate
read-only S3 inspection.

## Apply evidence

The approved saved plan was revalidated before execution:

```text
Plan SHA-256  457d6f7a50be5b7cca1ed6240b9cab7c5e16bb9c0ef4242d67d520e21f1b8474
AWS account   736956442295
Region        ap-southeast-1
Terraform     1.11.4
```

Terraform applied exactly the saved plan:

```text
Apply complete! Resources: 3 added, 0 changed, 0 destroyed.
```

The three managed resources were the approved Goal 5 synthetic source objects:

| Resource | S3 object | Type | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| `aws_s3_object.goal5_structured_source[0]` | `s3://ask-david-dev-736956442295-ap-southeast-1-raw/unity-catalog/development/goal5/structured/synthetic_events.csv` | `text/csv` | 262 | `74259ed76c875198dad9208116cee55afe48cead876a8527a39dd9a0eefb9e35` |
| `aws_s3_object.goal5_document_source[0]` | `s3://ask-david-dev-736956442295-ap-southeast-1-documents/unity-catalog/development/goal5/documents/neutral_technical_guide.md` | `text/markdown` | 240 | `712692e5f791f53bb9ed79f94c0b77841d052f1d9109bd774b86b5b8ac6bf791` |
| `aws_s3_object.goal5_cdc_source[0]` | `s3://ask-david-dev-736956442295-ap-southeast-1-raw/unity-catalog/development/goal5/cdc/synthetic_changes.jsonl` | `application/x-ndjson` | 852 | `c343236747d062d8223bcefb43f34ec69778c9dd4b0466b9b3be79b2609e9abf` |

## Read-only inspection

`head-object`, object-tagging, and read-back hash checks passed for all three
objects. Every object reports `ServerSideEncryption=aws:kms` and the existing
Goal 3/4 storage KMS key
`arn:aws:kms:ap-southeast-1:736956442295:key/a480662f-1d15-48b4-badd-c698c74eeb18`.

All objects have the expected `Goal=goal-05`, `ManagedBy=terraform`,
`DataClassification=synthetic-only`, `Environment=development`, `Owner=bachvx`,
and `CostCenter=personal-dev` tags, plus the expected source-pattern tag.
Read-back SHA-256 values exactly match the repository fixtures; no source
content was changed in transit.

## Boundary and next checkpoint

No Databricks bundle validation or deployment, SQL/job execution, compute
creation, idempotency rerun, Terraform plan, or additional AWS mutation was
performed in this checkpoint.

Goal 5 remains unverified. The next separate approval is for one strict
connected Databricks bundle validation of the reviewed Goal 5 source set,
without deployment or SQL/job execution. Any warning, error, unexpected
resource, production scope, or Goal 6+ content must stop the sequence.
