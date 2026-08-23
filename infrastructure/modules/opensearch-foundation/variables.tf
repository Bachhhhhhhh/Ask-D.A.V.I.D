variable "enabled" { type = bool }
variable "name_prefix" { type = string }
variable "collection_prefix" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "security_group_ids" { type = list(string) }

variable "knowledge_enabled" {
  type        = bool
  default     = false
  description = "Goal 7 gate for one vector collection and its least-privilege data policy."
}

variable "knowledge_collection_name" {
  type        = string
  default     = null
  nullable    = true
  description = "Terraform-managed Goal 7 VECTORSEARCH collection name."
}

variable "knowledge_principal_arns" {
  type        = list(string)
  default     = []
  description = "Exact workload/service principals allowed to use the Goal 7 collection."
}
