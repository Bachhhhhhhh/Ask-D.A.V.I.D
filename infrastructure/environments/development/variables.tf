variable "aws_account_id" { type = string }
variable "aws_region" { type = string }
variable "project" { type = string }
variable "environment" { type = string }
variable "additional_tags" { type = map(string) }
variable "vpc_cidr" { type = string }
variable "public_subnet_cidr" { type = string }
variable "application_subnet_cidrs" { type = list(string) }
variable "data_subnet_cidrs" { type = list(string) }
variable "availability_zones" { type = list(string) }
variable "internal_ingress_cidrs" { type = list(string) }
variable "nat_gateway_mode" {
  type    = string
  default = "single"
  validation {
    condition     = contains(["single", "per_az"], var.nat_gateway_mode)
    error_message = "nat_gateway_mode must be single or per_az."
  }
}
variable "rds_instance_class" { type = string }
variable "redis_node_type" { type = string }
variable "rds_deletion_protection" { type = bool }
variable "rds_skip_final_snapshot" { type = bool }
variable "log_retention_days" { type = number }
variable "enable_opensearch_foundation" { type = bool }
variable "opensearch_collection_prefix" { type = string }
variable "bucket_name_prefix" {
  type = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{2,40}$", var.bucket_name_prefix))
    error_message = "bucket_name_prefix must be a lowercase S3-safe prefix."
  }
}
