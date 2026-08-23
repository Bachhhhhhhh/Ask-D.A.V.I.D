output "vpc_endpoint_id" { value = try(aws_opensearchserverless_vpc_endpoint.this[0].id, null) }
output "knowledge_collection_id" { value = try(aws_opensearchserverless_collection.knowledge[0].id, null) }
output "knowledge_collection_arn" { value = try(aws_opensearchserverless_collection.knowledge[0].arn, null) }
output "knowledge_collection_endpoint" { value = try(aws_opensearchserverless_collection.knowledge[0].collection_endpoint, null) }
