variable "enabled" { type = bool }
variable "account_id" { type = string }
variable "role_name" { type = string }
variable "bucket_arns" { type = set(string) }
variable "managed_prefixes" { type = set(string) }
variable "managed_object_arns" { type = set(string) }
variable "source_read_prefixes" {
  description = "Approved read-only source prefixes used by governed ingestion."
  type        = set(string)
  default     = []
}
variable "source_read_object_arns" {
  description = "Approved read-only source object ARNs used by governed ingestion."
  type        = set(string)
  default     = []
}
variable "managed_root_markers" {
  description = "Zero-byte S3 objects that make each approved managed-storage root an addressable path."
  type = map(object({
    bucket = string
    key    = string
  }))

  validation {
    condition = alltrue([
      for marker in values(var.managed_root_markers) :
      trimspace(marker.bucket) != "" &&
      !startswith(marker.key, "/") &&
      endswith(marker.key, "/")
    ])
    error_message = "Every managed-root marker needs a bucket and a relative S3 key ending in a slash."
  }
}
variable "storage_kms_key_arn" { type = string }
variable "external_id" {
  type      = string
  sensitive = true
}
variable "unity_catalog_iam_arn" { type = string }
variable "self_assumption_enabled" {
  type        = bool
  default     = false
  description = "Whether the existing storage role may assume itself after the initial role-creation apply."
}
variable "tags" { type = map(string) }
