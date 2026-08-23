# Goal 7 is disabled by default. This extension reuses the Goal 3 AOSS VPC
# endpoint and policies and adds only separately approved synthetic retrieval
# resources when the Goal 7 gates are explicitly enabled.

locals {
  goal7_task_enabled = var.goal_7_indexer_task_enabled || var.goal_7_demo_task_enabled

  # Keep the Goal 7 task network boundary separate from the shared workload SG.
  # The fallback keeps disabled Goal 7 module inputs harmless in tests.
  goal7_task_security_group_id = try(
    aws_security_group.goal7_tasks[0].id,
    module.network.workload_security_group_id,
  )
}

resource "aws_security_group" "goal7_tasks" {
  count       = local.goal7_task_enabled ? 1 : 0
  name_prefix = "${local.name_prefix}-goal7-tasks-"
  description = "Private Goal 7 ECS tasks with explicit AWS-endpoint, S3, and Premium Databricks NAT paths."
  vpc_id      = module.network.vpc_id
  egress      = []

  # Egress is intentionally empty on the SG itself. The three explicit
  # aws_vpc_security_group_egress_rule resources below own the allowlist.
  # Prevent the legacy inline attribute from revoking those separately
  # managed rules during refresh/plan.
  lifecycle {
    ignore_changes = [egress]
  }

  tags = merge(local.tags, {
    Component = "goal7-private-tasks"
    Purpose   = "goal7-premium-nat-egress"
  })
}

# Premium workspaces use the existing private-subnet NAT path for the public
# Databricks workspace endpoint. The rule is deliberately attached only to
# this dedicated Goal 7 SG; the shared workload SG remains endpoint/prefix-list
# scoped. No ECS task receives a public IP.
#trivy:ignore:AVD-AWS-0104
resource "aws_vpc_security_group_egress_rule" "goal7_tasks_databricks_https" {
  count             = local.goal7_task_enabled ? 1 : 0
  security_group_id = aws_security_group.goal7_tasks[0].id
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Goal 7 Premium Databricks workspace HTTPS through the existing private-subnet NAT gateway."
}

resource "aws_vpc_security_group_egress_rule" "goal7_tasks_aws_endpoints" {
  count                        = local.goal7_task_enabled ? 1 : 0
  security_group_id            = aws_security_group.goal7_tasks[0].id
  ip_protocol                  = "tcp"
  from_port                    = 443
  to_port                      = 443
  referenced_security_group_id = module.network.aws_endpoints_security_group_id
  description                  = "Goal 7 private task access to approved AWS interface endpoints."
}

resource "aws_vpc_security_group_egress_rule" "goal7_tasks_s3" {
  count             = local.goal7_task_enabled ? 1 : 0
  security_group_id = aws_security_group.goal7_tasks[0].id
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  prefix_list_id    = module.network.s3_gateway_prefix_list_id
  description       = "Goal 7 private task access to the S3 gateway endpoint for image layers."
}

resource "aws_vpc_security_group_ingress_rule" "goal7_tasks_to_aws_endpoints" {
  count                        = local.goal7_task_enabled ? 1 : 0
  security_group_id            = module.network.aws_endpoints_security_group_id
  referenced_security_group_id = aws_security_group.goal7_tasks[0].id
  ip_protocol                  = "tcp"
  from_port                    = 443
  to_port                      = 443
  description                  = "Goal 7 private task access to approved AWS interface endpoints."
}

output "goal_7_collection_id" {
  value = module.opensearch_foundation.knowledge_collection_id
}

output "goal_7_collection_arn" {
  value = module.opensearch_foundation.knowledge_collection_arn
}

output "goal_7_collection_endpoint" {
  value = module.opensearch_foundation.knowledge_collection_endpoint
}

output "goal_7_embedding_model_id" {
  value = var.goal_7_embedding_model_id
}

output "goal_7_embedding_dimension" {
  value = var.goal_7_embedding_dimension
}

output "goal_7_indexer_task_definition_arn" {
  value = module.goal7_indexer.task_definition_arn
}

output "goal_7_demo_task_definition_arn" {
  value = module.goal7_demo.task_definition_arn
}

output "goal_7_indexer_repository_url" {
  value = module.runtime.langgraph_runtime_repository_url
}

resource "aws_vpc_security_group_ingress_rule" "goal7_indexer_to_aoss" {
  count = var.goal_7_indexer_task_enabled ? 1 : 0

  security_group_id            = module.network.aoss_endpoint_security_group_id
  referenced_security_group_id = local.goal7_task_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 443
  to_port                      = 443
  description                  = "Goal 7 private indexer access to the approved AOSS endpoint only."
}

resource "aws_vpc_security_group_ingress_rule" "goal7_demo_to_doris" {
  count = var.goal_7_demo_task_enabled ? 1 : 0

  security_group_id            = module.doris_serving.fe_security_group_id
  referenced_security_group_id = local.goal7_task_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 9030
  to_port                      = 9030
  description                  = "Goal 7 integrated demo read-only access to the private Doris FE only."
}

resource "aws_vpc_security_group_egress_rule" "goal7_demo_to_doris" {
  count = var.goal_7_demo_task_enabled ? 1 : 0

  security_group_id            = local.goal7_task_security_group_id
  referenced_security_group_id = module.doris_serving.fe_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 9030
  to_port                      = 9030
  description                  = "Goal 7 integrated demo read-only egress to the private Doris FE only."
}
