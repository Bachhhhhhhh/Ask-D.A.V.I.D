output "fe_security_group_id" { value = try(aws_security_group.fe[0].id, null) }
output "be_security_group_id" { value = try(aws_security_group.be[0].id, null) }
output "fe_private_ip" { value = try(aws_instance.fe[0].private_ip, null) }
output "be_private_ip" { value = try(aws_instance.be[0].private_ip, null) }
output "log_group_name" { value = try(aws_cloudwatch_log_group.doris[0].name, null) }
output "log_group_arn" { value = try(aws_cloudwatch_log_group.doris[0].arn, null) }
