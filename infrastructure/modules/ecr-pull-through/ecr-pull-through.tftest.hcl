mock_provider "aws" {}

run "public_ecr_cache_uses_a_private_namespace" {
  command = plan

  assert {
    condition     = aws_ecr_pull_through_cache_rule.public_ecr.ecr_repository_prefix == "ecr-public" && aws_ecr_pull_through_cache_rule.public_ecr.upstream_registry_url == "public.ecr.aws"
    error_message = "The smoke cache must use Amazon ECR Public through the private ecr-public namespace."
  }

  assert {
    condition     = aws_ecr_repository_creation_template.public_ecr.prefix == "ecr-public" && contains(aws_ecr_repository_creation_template.public_ecr.applied_for, "PULL_THROUGH_CACHE") && aws_ecr_repository_creation_template.public_ecr.image_tag_mutability == "MUTABLE"
    error_message = "The cache repository template must be scoped to pull-through cache repositories."
  }
}
