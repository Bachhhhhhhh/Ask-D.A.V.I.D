# Smoke images are fetched by the Amazon ECR service from the public ECR
# upstream and pulled by Fargate from this account's private ECR endpoint.
resource "aws_ecr_pull_through_cache_rule" "public_ecr" {
  ecr_repository_prefix = "ecr-public"
  upstream_registry_url = "public.ecr.aws"
}

# Fargate task definitions pin image digests. Mutable tags remain the AWS
# recommendation for pull-through cache repositories so ECR can refresh tags;
# tags are not used by the smoke tasks.
resource "aws_ecr_repository_creation_template" "public_ecr" {
  prefix               = "ecr-public"
  description          = "Goal 3B synthetic smoke images from Amazon ECR Public"
  applied_for          = ["PULL_THROUGH_CACHE"]
  image_tag_mutability = "MUTABLE"

  encryption_configuration {
    encryption_type = "AES256"
  }
}
