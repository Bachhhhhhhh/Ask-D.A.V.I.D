output "admin_security_group_id" { value = try(aws_security_group.admin[0].id, null) }
output "verifier_security_group_id" { value = try(aws_security_group.verifier[0].id, null) }
output "admin_task_definition_arn" { value = try(aws_ecs_task_definition.admin[0].arn, null) }
output "verifier_task_definition_arn" { value = try(aws_ecs_task_definition.verifier[0].arn, null) }
output "repository_url" { value = try(aws_ecr_repository.image[0].repository_url, null) }
