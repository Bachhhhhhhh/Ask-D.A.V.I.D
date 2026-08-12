output "role_arn" {
  value = try(aws_iam_role.this[0].arn, null)
}

output "role_name" {
  value = try(aws_iam_role.this[0].name, null)
}

output "self_assumption_enabled" {
  value = var.self_assumption_enabled
}

output "managed_root_marker_keys" {
  value = {
    for root_name, marker in aws_s3_object.managed_root_marker :
    root_name => marker.key
  }
}
