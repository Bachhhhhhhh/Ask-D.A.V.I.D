variable "name_prefix" { type = string }
variable "vpc_id" { type = string }
variable "retention_days" { type = number }
variable "kms_key_arn" { type = string }
variable "tags" { type = map(string) }
