variable "name_prefix" { type = string }
variable "vpc_id" { type = string }
variable "retention_days" { type = number }
variable "kms_key_arn" { type = string }
variable "tags" { type = map(string) }

variable "account_id" {
  description = "AWS account that owns the VPC Flow Log."
  type        = string
}

variable "region" {
  description = "AWS Region that receives VPC Flow Logs."
  type        = string
}

variable "rds_instance_identifier" {
  description = "Terraform-managed RDS instance identifier monitored by the base CPU alarm."
  type        = string

  validation {
    condition     = trimspace(var.rds_instance_identifier) != ""
    error_message = "rds_instance_identifier must not be empty."
  }
}

variable "rds_cpu_alarm_threshold_percent" {
  description = "Average RDS CPU percentage that triggers the base alarm after five consecutive one-minute datapoints."
  type        = number

  validation {
    condition = (
      var.rds_cpu_alarm_threshold_percent > 0 &&
      var.rds_cpu_alarm_threshold_percent <= 100
    )
    error_message = "rds_cpu_alarm_threshold_percent must be greater than 0 and no greater than 100."
  }
}
