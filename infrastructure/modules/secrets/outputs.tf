output "secret_arns" { value = { for purpose, secret in aws_secretsmanager_secret.this : purpose => secret.arn } }
