variable "name_prefix" { type = string }
variable "kms_key_id" { type = string }
variable "tags" { type = map(string) }
variable "additional_containers" {
  description = "Additional secret container suffixes, never secret values."
  type        = set(string)
  default     = []
}
