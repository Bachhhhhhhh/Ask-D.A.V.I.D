mock_provider "aws" {}

run "private_synthetic_smoke_tasks_are_pinned_and_least_privilege" {
  command = plan

  variables {
    name_prefix           = "ask-david-development"
    account_id            = "123456789012"
    region                = "ap-southeast-1"
    runtime_log_group_arn = "arn:aws:logs:ap-southeast-1:123456789012:log-group:/ask-david-development/runtime"
    rds_endpoint          = "database.example.internal"
    rds_master_secret_arn = "arn:aws:secretsmanager:ap-southeast-1:123456789012:secret:rds-master-AbCd" # pragma: allowlist secret -- synthetic ARN only
    redis_endpoint        = "redis.example.internal"
    raw_bucket_name       = "ask-david-raw"
    curated_bucket_name   = "ask-david-curated"
    tags = {
      Project = "ask-david"
    }
  }

  assert {
    condition     = length(aws_ecs_task_definition.this) == 3
    error_message = "Exactly three static smoke task definitions are required."
  }

  assert {
    condition     = strcontains(aws_iam_role_policy.task.policy, "s3:ListBucket") && !strcontains(aws_iam_role_policy.task.policy, "ask-david-curated")
    error_message = "The smoke task role must list only the approved raw bucket."
  }

  assert {
    condition     = strcontains(aws_ecs_task_definition.this["postgres"].container_definitions, "123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/ecr-public/docker/library/postgres@sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777") && strcontains(aws_ecs_task_definition.this["redis"].container_definitions, "123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/ecr-public/docker/library/redis@sha256:e7723ff73d963f5cc6d9c4643ea3d989527a402a319239054e9472a7fb9219a2") && strcontains(aws_ecs_task_definition.this["s3"].container_definitions, "123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/ecr-public/aws-cli/aws-cli@sha256:7e0331f50ea97c09241521688082ef39a95b5f10ddd2eaabeef4313d974b5258")
    error_message = "Every smoke image must use the private ECR pull-through cache and a reviewed digest."
  }

  assert {
    condition     = strcontains(aws_iam_role_policy.execution_pull_through_cache.policy, "ecr:BatchImportUpstreamImage") && strcontains(aws_iam_role_policy.execution_pull_through_cache.policy, "ecr:CreateRepository") && strcontains(aws_iam_role_policy.execution_pull_through_cache.policy, "repository/ecr-public/*")
    error_message = "The execution role must be limited to importing the approved private ECR cache namespace."
  }

  assert {
    condition     = strcontains(aws_ecs_task_definition.this["redis"].container_definitions, "redis-cli --tls --sni") && strcontains(aws_ecs_task_definition.this["redis"].container_definitions, " -h ") && strcontains(aws_ecs_task_definition.this["redis"].container_definitions, " -p 6379") && !strcontains(aws_ecs_task_definition.this["redis"].container_definitions, "--host") && !strcontains(aws_ecs_task_definition.this["redis"].container_definitions, "--port")
    error_message = "The Redis smoke command must use the supported redis-cli -h and -p options."
  }
}
