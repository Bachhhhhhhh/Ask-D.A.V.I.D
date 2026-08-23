output "task_definition_arn" {
  value = try(aws_ecs_task_definition.this[0].arn, null)
}

output "task_definition_family" {
  value = try(aws_ecs_task_definition.this[0].family, null)
}
