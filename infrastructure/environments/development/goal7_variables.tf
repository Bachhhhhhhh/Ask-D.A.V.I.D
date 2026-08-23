variable "goal_7_enabled" {
  description = "Explicit Goal 7 gate for one synthetic OpenSearch vector collection and service boundary."
  type        = bool
  default     = false
}

variable "goal_7_collection_name" {
  description = "One Goal 7 AOSS VECTORSEARCH collection; no duplicate collections are permitted."
  type        = string
  default     = "ask-david-development-knowledge"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,31}$", var.goal_7_collection_name))
    error_message = "goal_7_collection_name must be 3-32 lowercase letters, digits, or hyphens and start with a letter."
  }
}

variable "goal_7_vector_index_name" {
  description = "Controlled data-plane index name for the one Goal 7 vector index."
  type        = string
  default     = "synthetic-document-chunks"

  validation {
    condition     = can(regex("^[a-z][a-z0-9_-]{2,62}$", var.goal_7_vector_index_name))
    error_message = "goal_7_vector_index_name must be a lowercase OpenSearch index name."
  }
}

variable "goal_7_embedding_model_id" {
  description = "Canonical Databricks embedding model ID used for indexing and query-time retrieval."
  type        = string
  default     = "databricks-gte-large-en"

  validation {
    condition     = var.goal_7_embedding_model_id == "databricks-gte-large-en"
    error_message = "Goal 7 uses the approved canonical Databricks GTE Large English embedding model."
  }
}

variable "goal_7_embedding_dimension" {
  description = "Fixed vector dimension for the canonical embedding model."
  type        = number
  default     = 1024

  validation {
    condition     = var.goal_7_embedding_dimension == 1024
    error_message = "Goal 7 canonical Databricks GTE Large embedding dimension is fixed at 1024."
  }
}

variable "goal_7_indexer_task_enabled" {
  description = "Explicit gate for the one-shot private Goal 7 outbox index/search task."
  type        = bool
  default     = false
}

variable "goal_7_demo_task_enabled" {
  description = "Explicit gate for the one-shot private integrated Supervisor demo task."
  type        = bool
  default     = false
}

variable "goal_7_indexer_image" {
  description = "Immutable digest-pinned image for the controlled Goal 7 indexer task."
  type        = string
  default     = null
  nullable    = true
}

variable "goal_7_demo_image" {
  description = "Immutable digest-pinned image for the controlled Goal 7 integrated demo task."
  type        = string
  default     = null
  nullable    = true
}

check "goal_7_enabled_inputs" {
  assert {
    condition = !var.goal_7_enabled || (
      var.enable_opensearch_foundation &&
      var.goal_7_collection_name != null &&
      var.goal_7_vector_index_name != null &&
      var.goal_7_embedding_model_id == "databricks-gte-large-en" &&
      var.goal_7_embedding_dimension == 1024 &&
      (!var.goal_7_indexer_task_enabled || var.goal_7_indexer_image != null) &&
      (!var.goal_7_demo_task_enabled || var.goal_7_demo_image != null) &&
      (!(var.goal_7_indexer_task_enabled && var.goal_7_demo_task_enabled) ||
      var.goal_7_indexer_image != var.goal_7_demo_image)
    )
    error_message = "Goal 7 requires the existing AOSS foundation, one approved collection/index name, and the canonical Databricks embedding configuration."
  }
}

check "goal_7_indexer_requires_foundation" {
  assert {
    condition     = !var.goal_7_indexer_task_enabled || var.goal_7_enabled
    error_message = "The private Goal 7 indexer requires the Goal 7 AOSS and Databricks foundation gate."
  }
}

check "goal_7_demo_requires_doris" {
  assert {
    condition     = !var.goal_7_demo_task_enabled || (var.goal_7_enabled && var.goal_6_enabled)
    error_message = "The integrated Goal 7 demo requires both Goal 7 and the verified Goal 6 Doris foundation."
  }
}
