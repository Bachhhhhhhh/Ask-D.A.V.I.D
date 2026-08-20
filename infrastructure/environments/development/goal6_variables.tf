variable "goal_6_enabled" {
  description = "Approval gate for the Goal 6 foundation, initially without verifier task definitions."
  type        = bool
  default     = false
}

variable "goal_6_verifier_tasks_enabled" {
  description = "Second approval gate for ECS task definitions after a reviewed verifier image digest is pushed to the Terraform-created ECR repository."
  type        = bool
  default     = false
}

variable "goal_6_data_subnet_id" {
  description = "One approved private data subnet for the single-AZ development FE/BE pair."
  type        = string
  default     = null
  nullable    = true
}

variable "goal_6_fe_private_ip" {
  description = "Terraform-managed stable private IPv4 address for the development Doris FE."
  type        = string
  default     = "10.42.64.238"

  validation {
    condition     = var.goal_6_fe_private_ip == "10.42.64.238"
    error_message = "Goal 6 development FE private IP is fixed at 10.42.64.238 to match the persisted development Doris metadata state."
  }
}

variable "goal_6_be_private_ip" {
  description = "Terraform-managed stable private IPv4 address for the development Doris BE."
  type        = string
  default     = "10.42.71.97"

  validation {
    condition     = var.goal_6_be_private_ip == "10.42.71.97"
    error_message = "Goal 6 development BE private IP is fixed at 10.42.71.97 to match the persisted development Doris serving state."
  }
}

variable "goal_6_ami_id" {
  description = "Pinned approved Linux AMI ID for private Doris hosts."
  type        = string
  default     = null
  nullable    = true
}

variable "goal_6_fe_image" {
  description = "Digest-pinned Apache Doris FE image; never a floating tag."
  type        = string
  default     = null
  nullable    = true
}

variable "goal_6_be_image" {
  description = "Digest-pinned Apache Doris BE image; never a floating tag."
  type        = string
  default     = null
  nullable    = true
}

variable "goal_6_verifier_image" {
  description = "Digest-pinned private ECR Goal 6 verifier image."
  type        = string
  default     = null
  nullable    = true
}

variable "goal_6_fe_instance_type" {
  type        = string
  default     = "m7i.xlarge"
  description = "Cost-conscious private development FE instance type."

  validation {
    condition     = var.goal_6_fe_instance_type == "m7i.xlarge"
    error_message = "Goal 6 development FE is fixed at m7i.xlarge pending a separately approved sizing change."
  }
}

variable "goal_6_be_instance_type" {
  type        = string
  default     = "m7i.xlarge"
  description = "Cost-conscious private development BE instance type."

  validation {
    condition     = var.goal_6_be_instance_type == "m7i.xlarge"
    error_message = "Goal 6 development BE is fixed at m7i.xlarge pending a separately approved sizing change."
  }
}

variable "goal_6_fe_data_volume_gib" {
  type        = number
  default     = 20
  description = "Encrypted gp3 volume for disposable FE metadata."
}

variable "goal_6_be_data_volume_gib" {
  type        = number
  default     = 50
  description = "Encrypted gp3 volume for disposable BE serving state."
}

variable "goal_6_rebuild_serving_state" {
  type        = bool
  default     = false
  description = "Explicit recovery gate: create fresh FE metadata and BE serving-state volumes while retaining previous encrypted volumes without deletion or reformat."
}

variable "goal_6_fe_root_volume_gib" {
  type        = number
  default     = 30
  description = "Encrypted gp3 root volume for the private FE host and its pinned Docker image."

  validation {
    condition     = var.goal_6_fe_root_volume_gib == 30
    error_message = "Goal 6 development FE root storage is fixed at 30 GiB pending a separately approved sizing change."
  }
}

variable "goal_6_be_root_volume_gib" {
  type        = number
  default     = 30
  description = "Encrypted gp3 root volume for the private BE host and its pinned Docker image."

  validation {
    condition     = var.goal_6_be_root_volume_gib == 30
    error_message = "Goal 6 development BE root storage is fixed at 30 GiB pending a separately approved sizing change."
  }
}

variable "goal_6_be_bootstrap_generation" {
  type        = number
  default     = 2
  description = "BE-only cloud-init generation. Generation 2 is the reviewed recovery from the failed 8 GiB-root bootstrap."

  validation {
    condition     = var.goal_6_be_bootstrap_generation == 2
    error_message = "Goal 6 BE bootstrap generation is fixed at 2 until a separately approved recovery change."
  }
}

variable "goal_6_fe_bootstrap_generation" {
  type        = number
  default     = 2
  description = "FE cloud-init generation for the Docker discovery/listener remediation."

  validation {
    condition     = var.goal_6_fe_bootstrap_generation == 2
    error_message = "Goal 6 FE bootstrap generation is fixed at 2 until a separately approved recovery change."
  }
}

check "goal_6_enabled_inputs" {
  assert {
    condition = !var.goal_6_enabled || alltrue([
      var.goal_6_data_subnet_id != null,
      var.goal_6_ami_id != null,
      var.goal_6_fe_private_ip != var.goal_6_be_private_ip,
      can(regex("^[0-9]{1,3}(\\.[0-9]{1,3}){3}$", var.goal_6_fe_private_ip)),
      can(regex("^[0-9]{1,3}(\\.[0-9]{1,3}){3}$", var.goal_6_be_private_ip)),
      can(regex("@sha256:[a-f0-9]{64}$", coalesce(var.goal_6_fe_image, ""))),
      can(regex("@sha256:[a-f0-9]{64}$", coalesce(var.goal_6_be_image, ""))),
      var.goal_6_fe_data_volume_gib >= 20,
      var.goal_6_be_data_volume_gib >= 50,
      var.goal_6_fe_root_volume_gib >= 30,
      var.goal_6_be_root_volume_gib >= 30,
    ])
    error_message = "Goal 6 foundation requires one selected private subnet, distinct approved private IP inputs, an approved AMI, digest-pinned Doris FE/BE images, and the minimum encrypted volume sizes."
  }
}

check "goal_6_verifier_task_image" {
  assert {
    condition = !var.goal_6_verifier_tasks_enabled || (
      var.goal_6_enabled &&
      can(regex("@sha256:[a-f0-9]{64}$", coalesce(var.goal_6_verifier_image, "")))
    )
    error_message = "Goal 6 verifier task definitions require the enabled foundation and a digest-pinned image already pushed to the Terraform-created ECR repository."
  }
}
