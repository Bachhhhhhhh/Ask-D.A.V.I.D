variable "aws_account_id" {
  type = string
  validation {
    condition     = can(regex("^[0-9]{12}$", var.aws_account_id))
    error_message = "aws_account_id must contain exactly 12 digits."
  }
}

variable "aws_region" {
  type = string
  validation {
    condition     = var.aws_region == "ap-southeast-1"
    error_message = "The development state bootstrap must use ap-southeast-1."
  }
}

variable "bucket_name" {
  type = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.bucket_name))
    error_message = "bucket_name must be a valid lowercase S3 bucket name."
  }
}

variable "tags" {
  type = map(string)
  validation {
    condition = alltrue([
      for key in [
        "Project",
        "Environment",
        "Component",
        "ManagedBy",
        "Owner",
        "CostCenter",
        "DataClassification",
      ] : try(trimspace(var.tags[key]) != "", false)
    ]) && try(var.tags["ManagedBy"] == "terraform", false)
    error_message = "tags must contain non-empty mandatory tags and ManagedBy=terraform."
  }
}
