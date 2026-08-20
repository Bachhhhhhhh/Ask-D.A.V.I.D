variable "name_prefix" { type = string }
variable "tags" { type = map(string) }

variable "account_id" {
  description = "AWS account that owns the observability log groups."
  type        = string
}

variable "region" {
  description = "AWS Region that contains the observability log groups."
  type        = string
}

variable "storage_access_role_arn" {
  description = "Optional exact Unity Catalog role allowed to use the storage key."
  type        = string
  default     = null
  nullable    = true
}

variable "goal_6_enabled" {
  description = "Include the exact Goal 6 Doris CloudWatch log group in the observability key policy."
  type        = bool
  default     = false
}
