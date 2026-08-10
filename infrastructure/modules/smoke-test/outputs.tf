output "task_definition_arns" {
  value = { for name, task in aws_ecs_task_definition.this : name => task.arn }
}

output "task_definition_families" {
  value = { for name, task in aws_ecs_task_definition.this : name => task.family }
}
