output "vpc_endpoint_id" { value = try(aws_opensearchserverless_vpc_endpoint.this[0].id, null) }
