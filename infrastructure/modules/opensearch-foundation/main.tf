resource "aws_opensearchserverless_vpc_endpoint" "this" {
  count              = var.enabled ? 1 : 0
  name               = "${var.name_prefix}-aoss"
  vpc_id             = var.vpc_id
  subnet_ids         = var.subnet_ids
  security_group_ids = var.security_group_ids
}
resource "aws_opensearchserverless_security_policy" "encryption" {
  count  = var.enabled ? 1 : 0
  name   = "${var.name_prefix}-encryption"
  type   = "encryption"
  policy = jsonencode({ Rules = [{ ResourceType = "collection", Resource = ["collection/${var.collection_prefix}*"] }], AWSOwnedKey = true })
}
resource "aws_opensearchserverless_security_policy" "network" {
  count  = var.enabled ? 1 : 0
  name   = "${var.name_prefix}-network"
  type   = "network"
  policy = jsonencode([{ Rules = [{ ResourceType = "collection", Resource = ["collection/${var.collection_prefix}*"] }], AllowFromPublic = false, SourceVPCEs = [aws_opensearchserverless_vpc_endpoint.this[0].id] }])
}

resource "aws_opensearchserverless_collection" "knowledge" {
  count = var.knowledge_enabled ? 1 : 0

  name             = var.knowledge_collection_name
  type             = "VECTORSEARCH"
  description      = "Synthetic-only Ask D.A.V.I.D. Goal 7 vector retrieval collection."
  standby_replicas = "DISABLED"

  depends_on = [
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_security_policy.network,
  ]
}

resource "aws_opensearchserverless_access_policy" "knowledge" {
  count = var.knowledge_enabled ? 1 : 0

  name = "${var.name_prefix}-aoss-data"
  type = "data"
  policy = jsonencode([{
    Description = "Goal 7 synthetic vector index access through the controlled indexing/retrieval service."
    Principal   = var.knowledge_principal_arns
    Rules = [
      {
        ResourceType = "collection"
        Resource     = ["collection/${var.knowledge_collection_name}"]
        Permission   = ["aoss:DescribeCollectionItems"]
      },
      {
        ResourceType = "index"
        Resource     = ["index/${var.knowledge_collection_name}/*"]
        Permission = [
          "aoss:CreateIndex",
          "aoss:DescribeIndex",
          "aoss:ReadDocument",
          "aoss:WriteDocument",
        ]
      },
    ]
  }])

  depends_on = [aws_opensearchserverless_collection.knowledge]
}
