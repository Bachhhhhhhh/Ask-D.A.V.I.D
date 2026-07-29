variable "enabled" { type = bool }
variable "name_prefix" { type = string }
variable "collection_prefix" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "security_group_ids" { type = list(string) }
