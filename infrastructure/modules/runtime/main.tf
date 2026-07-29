resource "aws_ecr_repository" "api" {
  name                 = "${var.name_prefix}/api"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  tags = var.tags
}
resource "aws_ecr_repository" "langgraph_runtime" {
  name                 = "${var.name_prefix}/langgraph-runtime"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  tags = var.tags
}
resource "aws_ecs_cluster" "this" { name = "${var.name_prefix}-cluster" }
resource "aws_lb" "internal" {
  name                       = "${var.name_prefix}-internal"
  internal                   = true
  load_balancer_type         = "application"
  security_groups            = [var.alb_security_group_id]
  subnets                    = var.application_subnet_ids
  drop_invalid_header_fields = true
  tags                       = var.tags
}
