// Goal 5 synthetic source fixtures only. Existing buckets and KMS encryption
// are reused; this does not create infrastructure, IAM, or new locations.
resource "aws_s3_object" "goal5_structured_source" {
  count        = var.goal_5_source_objects_enabled ? 1 : 0
  bucket       = module.storage.bucket_names["raw"]
  key          = "unity-catalog/development/goal5/structured/synthetic_events.csv"
  source       = "${path.root}/../../../synthetic_data/goal_05/structured/synthetic_events.csv"
  source_hash  = filebase64sha256("${path.root}/../../../synthetic_data/goal_05/structured/synthetic_events.csv")
  content_type = "text/csv"

  server_side_encryption = "aws:kms"
  kms_key_id             = module.kms.storage_key_arn

  tags = merge(local.tags, {
    Goal               = "goal-05"
    DataClassification = "synthetic-only"
    SourcePattern      = "structured-file"
  })
}

resource "aws_s3_object" "goal5_document_source" {
  count        = var.goal_5_source_objects_enabled ? 1 : 0
  bucket       = module.storage.bucket_names["documents"]
  key          = "unity-catalog/development/goal5/documents/neutral_technical_guide.md"
  source       = "${path.root}/../../../synthetic_data/goal_05/documents/neutral_technical_guide.md"
  source_hash  = filebase64sha256("${path.root}/../../../synthetic_data/goal_05/documents/neutral_technical_guide.md")
  content_type = "text/markdown"

  server_side_encryption = "aws:kms"
  kms_key_id             = module.kms.storage_key_arn

  tags = merge(local.tags, {
    Goal               = "goal-05"
    DataClassification = "synthetic-only"
    SourcePattern      = "unstructured-document"
  })
}

resource "aws_s3_object" "goal5_cdc_source" {
  count        = var.goal_5_source_objects_enabled ? 1 : 0
  bucket       = module.storage.bucket_names["raw"]
  key          = "unity-catalog/development/goal5/cdc/synthetic_changes.jsonl"
  source       = "${path.root}/../../../synthetic_data/goal_05/cdc/synthetic_changes.jsonl"
  source_hash  = filebase64sha256("${path.root}/../../../synthetic_data/goal_05/cdc/synthetic_changes.jsonl")
  content_type = "application/x-ndjson"

  server_side_encryption = "aws:kms"
  kms_key_id             = module.kms.storage_key_arn

  tags = merge(local.tags, {
    Goal               = "goal-05"
    DataClassification = "synthetic-only"
    SourcePattern      = "cdc-batch"
  })
}
