locals {
  role_arn = "arn:aws:iam::${var.account_id}:role/${var.role_name}"
}

data "aws_iam_policy_document" "assume_role" {
  count = var.enabled ? 1 : 0

  statement {
    sid     = "UnityCatalogAssumeRole"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type = "AWS"
      identifiers = concat(
        [var.unity_catalog_iam_arn],
        var.self_assumption_enabled ? [local.role_arn] : [],
      )
    }

    condition {
      test     = "StringEquals"
      variable = "sts:ExternalId"
      values   = [var.external_id]
    }
  }
}

resource "aws_iam_role" "this" {
  count = var.enabled ? 1 : 0

  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.assume_role[0].json
  tags               = var.tags
}

data "aws_iam_policy_document" "storage" {
  count = var.enabled ? 1 : 0

  statement {
    sid       = "LocateApprovedBuckets"
    effect    = "Allow"
    actions   = ["s3:GetBucketLocation"]
    resources = var.bucket_arns
  }

  statement {
    sid       = "ListApprovedManagedPrefixes"
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = var.bucket_arns

    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values = flatten([
        for prefix in var.managed_prefixes : [prefix, "${prefix}/*"]
      ])
    }
  }

  statement {
    sid    = "ManageApprovedIcebergObjects"
    effect = "Allow"
    actions = [
      "s3:AbortMultipartUpload",
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:ListMultipartUploadParts",
      "s3:PutObject",
    ]
    resources = var.managed_object_arns
  }

  statement {
    sid    = "UseStorageKmsKey"
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey",
      "kms:GenerateDataKeyWithoutPlaintext",
      "kms:ReEncryptFrom",
      "kms:ReEncryptTo",
    ]
    resources = [var.storage_kms_key_arn]
  }

  statement {
    sid       = "SelfAssumeRole"
    effect    = "Allow"
    actions   = ["sts:AssumeRole"]
    resources = [local.role_arn]
  }
}

resource "aws_iam_role_policy" "this" {
  count = var.enabled ? 1 : 0

  name   = "${var.role_name}-managed-iceberg"
  role   = aws_iam_role.this[0].id
  policy = data.aws_iam_policy_document.storage[0].json
}

resource "aws_s3_object" "managed_root_marker" {
  for_each = var.enabled ? var.managed_root_markers : {}

  bucket                 = each.value.bucket
  key                    = each.value.key
  content                = ""
  server_side_encryption = "aws:kms"
  kms_key_id             = var.storage_kms_key_arn
}
