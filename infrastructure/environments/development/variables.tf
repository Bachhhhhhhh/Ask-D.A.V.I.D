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
    error_message = "The development environment must use ap-southeast-1."
  }
}

variable "project" {
  type = string
  validation {
    condition     = trimspace(var.project) != ""
    error_message = "project must not be empty."
  }
}

variable "environment" {
  type = string
  validation {
    condition     = var.environment == "development"
    error_message = "Goal 3 supports only the development environment."
  }
}

variable "additional_tags" {
  type = map(string)
  validation {
    condition = alltrue([
      for key in ["Owner", "CostCenter"] :
      try(trimspace(var.additional_tags[key]) != "", false)
    ])
    error_message = "additional_tags must contain non-empty Owner and CostCenter values."
  }
}

variable "vpc_cidr" {
  type = string
  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "vpc_cidr must be a valid IPv4 CIDR."
  }
}

variable "public_subnet_cidr" {
  type = string
  validation {
    condition     = can(cidrnetmask(var.public_subnet_cidr))
    error_message = "public_subnet_cidr must be a valid IPv4 CIDR."
  }
}

variable "application_subnet_cidrs" {
  type = list(string)
  validation {
    condition = (
      length(var.application_subnet_cidrs) >= 2 &&
      length(distinct(var.application_subnet_cidrs)) == length(var.application_subnet_cidrs) &&
      alltrue([for cidr in var.application_subnet_cidrs : can(cidrnetmask(cidr))])
    )
    error_message = "application_subnet_cidrs must contain at least two unique valid IPv4 CIDRs."
  }
}

variable "data_subnet_cidrs" {
  type = list(string)
  validation {
    condition = (
      length(var.data_subnet_cidrs) >= 2 &&
      length(distinct(var.data_subnet_cidrs)) == length(var.data_subnet_cidrs) &&
      alltrue([for cidr in var.data_subnet_cidrs : can(cidrnetmask(cidr))])
    )
    error_message = "data_subnet_cidrs must contain at least two unique valid IPv4 CIDRs."
  }
}

variable "availability_zones" {
  type = list(string)
  validation {
    condition = (
      length(var.availability_zones) >= 2 &&
      length(distinct(var.availability_zones)) == length(var.availability_zones) &&
      alltrue([for az in var.availability_zones : startswith(az, "ap-southeast-1")])
    )
    error_message = "availability_zones must contain at least two unique ap-southeast-1 zones."
  }
}

variable "internal_ingress_cidrs" {
  type = list(string)
  validation {
    condition = (
      length(var.internal_ingress_cidrs) > 0 &&
      alltrue([for cidr in var.internal_ingress_cidrs : can(cidrnetmask(cidr))]) &&
      !contains(var.internal_ingress_cidrs, "0.0.0.0/0")
    )
    error_message = "internal_ingress_cidrs must contain valid restricted CIDRs and cannot include 0.0.0.0/0."
  }
}
variable "nat_gateway_mode" {
  type    = string
  default = "single"
  validation {
    condition     = contains(["single", "per_az"], var.nat_gateway_mode)
    error_message = "nat_gateway_mode must be single or per_az."
  }
}
variable "rds_instance_class" {
  type = string
  validation {
    condition     = startswith(var.rds_instance_class, "db.")
    error_message = "rds_instance_class must be an RDS DB instance class."
  }
}

variable "redis_node_type" {
  type = string
  validation {
    condition     = startswith(var.redis_node_type, "cache.")
    error_message = "redis_node_type must be an ElastiCache node type."
  }
}
variable "rds_deletion_protection" { type = bool }
variable "rds_skip_final_snapshot" { type = bool }
variable "log_retention_days" {
  type = number
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731,
      1096, 1827, 2192, 2557, 2922, 3288, 3653,
    ], var.log_retention_days)
    error_message = "log_retention_days must be a CloudWatch-supported retention value."
  }
}
variable "enable_opensearch_foundation" { type = bool }
variable "opensearch_collection_prefix" {
  type = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,31}$", var.opensearch_collection_prefix))
    error_message = "opensearch_collection_prefix must be 3-32 lowercase letters, digits, or hyphens and start with a letter."
  }
}
variable "bucket_name_prefix" {
  type = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{2,40}$", var.bucket_name_prefix))
    error_message = "bucket_name_prefix must be a lowercase S3-safe prefix."
  }
}
