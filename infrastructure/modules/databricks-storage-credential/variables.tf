variable "enabled" { type = bool }
variable "name" { type = string }
variable "iam_role_arn" { type = string }
variable "owner" { type = string }
variable "workspace_id" { type = number }
variable "bind_to_workspace" { type = bool }
variable "skip_validation" { type = bool }

variable "comment" {
  type    = string
  default = "Ask DAVID development managed-Iceberg storage credential"
}
