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
