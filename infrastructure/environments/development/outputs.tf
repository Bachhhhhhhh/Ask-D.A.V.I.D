output "vpc_id" { value = module.network.vpc_id }
output "task_execution_role_arn" { value = module.iam.task_execution_role_arn }
output "workload_role_arn" { value = module.iam.workload_role_arn }
