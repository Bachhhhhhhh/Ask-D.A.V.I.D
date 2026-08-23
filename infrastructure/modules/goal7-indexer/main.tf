locals {
  tags = merge(var.tags, {
    Component          = "goal7-indexer"
    Goal               = "goal-07"
    DataClassification = "synthetic-only"
  })
}

resource "aws_ecs_task_definition" "this" {
  count = var.enabled ? 1 : 0

  family                   = "${var.name_prefix}-goal7-indexer"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.workload_role_arn

  container_definitions = jsonencode([{
    name      = "goal7-indexer"
    image     = var.image
    essential = true
    command   = ["python", "-m", "ask_david_goal7.indexer"]
    environment = [
      { name = "AWS_REGION", value = var.region },
      { name = "DATABRICKS_WORKSPACE_HOST", value = var.databricks_workspace_host },
      { name = "DATABRICKS_WAREHOUSE_ID", value = var.databricks_warehouse_id },
      { name = "GOAL7_CATALOG", value = var.catalog_name },
      { name = "GOAL7_AOSS_ENDPOINT", value = var.aoss_endpoint },
      { name = "GOAL7_COLLECTION_NAME", value = var.collection_name },
      { name = "GOAL7_INDEX_NAME", value = var.index_name },
    ]
    secrets = [{
      name      = "DATABRICKS_OAUTH_SECRET"
      valueFrom = var.databricks_oauth_secret_arn
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = var.runtime_log_group_name
        awslogs-region        = var.region
        awslogs-stream-prefix = "goal7-indexer"
      }
    }
  }])

  tags = local.tags
}
