output "storage_key_arn" { value = aws_kms_key.storage.arn }
output "data_key_arn" { value = aws_kms_key.data.arn }
output "secrets_key_id" { value = aws_kms_key.secrets.key_id }
output "observability_key_arn" { value = aws_kms_key.observability.arn }
