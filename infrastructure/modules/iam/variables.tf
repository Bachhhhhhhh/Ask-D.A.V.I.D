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
variable "goal7_enabled" {
  description = "Enable the narrowly scoped OpenSearch Serverless data-plane API permission for Goal 7."
  type        = bool
  default     = false
}
variable "goal7_collection_name" {
  description = "Collection-name condition for the Goal 7 AOSS API permission."
  type        = string
  default     = null
  nullable    = true
}
variable "goal7_secret_arns" {
  description = "Exact Goal 7 secret ARNs that ECS task execution may read."
  type        = list(string)
  default     = []
}
variable "goal7_secrets_enabled" {
  description = "Plan-time gate for the exact Goal 7 task-execution secret policy."
  type        = bool
  default     = false
}
variable "goal7_secrets_kms_key_arn" {
  description = "KMS key encrypting the Goal 7 OAuth secret container."
  type        = string
  default     = null
  nullable    = true
}
