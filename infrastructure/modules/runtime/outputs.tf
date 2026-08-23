output "cluster_name" { value = aws_ecs_cluster.this.name }
output "cluster_arn" { value = aws_ecs_cluster.this.arn }
output "internal_alb_dns_name" { value = aws_lb.internal.dns_name }
output "langgraph_runtime_repository_url" { value = aws_ecr_repository.langgraph_runtime.repository_url }
