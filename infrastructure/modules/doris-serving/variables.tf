variable "enabled" { type = bool }
variable "name_prefix" { type = string }
variable "region" { type = string }
variable "vpc_id" { type = string }
variable "data_subnet_id" { type = string }
variable "fe_private_ip" {
  description = "Stable private IPv4 address reserved for the Terraform-managed FE in the selected data subnet."
  type        = string
}
variable "be_private_ip" {
  description = "Stable private IPv4 address reserved for the Terraform-managed BE in the selected data subnet."
  type        = string
}
variable "data_kms_key_arn" { type = string }
variable "observability_kms_key_arn" { type = string }
variable "log_retention_days" { type = number }
variable "fe_instance_type" { type = string }
variable "be_instance_type" { type = string }
variable "ami_id" { type = string }
variable "fe_image" { type = string }
variable "be_image" { type = string }
variable "fe_data_volume_gib" { type = number }
variable "be_data_volume_gib" { type = number }
variable "rebuild_serving_state" {
  description = "Explicit recovery gate for fresh disposable FE/BE serving-state volumes; previously managed encrypted volumes remain untouched."
  type        = bool
  default     = false
}
variable "fe_root_volume_gib" { type = number }
variable "be_root_volume_gib" { type = number }
variable "be_bootstrap_generation" {
  description = "Explicit BE-only first-boot generation; changing it intentionally replaces BE so cloud-init runs again."
  type        = number
}
variable "fe_bootstrap_generation" {
  description = "Explicit FE first-boot generation; changing it intentionally replaces FE so Docker discovery variables and listener guards run again."
  type        = number
}
variable "admin_secret_arn" { type = string }
variable "query_secret_arn" { type = string }
variable "priority_networks" {
  description = "Existing VPC CIDR used by FE/BE to select their private interface."
  type        = string
}
variable "tags" { type = map(string) }
