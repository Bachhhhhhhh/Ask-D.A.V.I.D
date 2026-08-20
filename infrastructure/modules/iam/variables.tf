variable "name_prefix" { type = string }
variable "runtime_log_group_arn" { type = string }
variable "tags" { type = map(string) }
variable "goal6_secret_arns" {
  description = "Exact Goal 6 secret ARNs that ECS agent injection may read."
  type        = list(string)
  default     = []
}
variable "goal6_secrets_kms_key_arn" {
  description = "KMS key ARN encrypting the exact Goal 6 Secrets Manager containers."
  type        = string
  default     = null
  nullable    = true
}
