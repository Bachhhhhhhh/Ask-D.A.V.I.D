resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-rds"
  subnet_ids = var.data_subnet_ids
  tags       = var.tags
}
resource "aws_db_instance" "postgres" {
  identifier                  = "${var.name_prefix}-postgres"
  engine                      = "postgres"
  engine_version              = "16"
  instance_class              = var.rds_instance_class
  allocated_storage           = 20
  db_name                     = "platform"
  username                    = "platformadmin"
  manage_master_user_password = true
  publicly_accessible         = false
  storage_encrypted           = true
  kms_key_id                  = var.kms_key_arn
  db_subnet_group_name        = aws_db_subnet_group.this.name
  vpc_security_group_ids      = [var.rds_security_group_id]
  deletion_protection         = var.rds_deletion_protection
  skip_final_snapshot         = var.rds_skip_final_snapshot
  tags                        = var.tags
}
resource "aws_elasticache_subnet_group" "this" {
  name       = "${var.name_prefix}-redis"
  subnet_ids = var.data_subnet_ids
}
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "${var.name_prefix}-redis"
  description                = "Private cache foundation"
  engine                     = "redis"
  node_type                  = var.redis_node_type
  num_cache_clusters         = 1
  automatic_failover_enabled = false
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true
  security_group_ids         = [var.redis_security_group_id]
  subnet_group_name          = aws_elasticache_subnet_group.this.name
  tags                       = var.tags
}
