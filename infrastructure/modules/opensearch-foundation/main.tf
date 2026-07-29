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
