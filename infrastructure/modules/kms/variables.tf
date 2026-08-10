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
