mock_provider "aws" {}

run "development_foundation_is_plannable" {
  command = plan

  variables {
    aws_account_id               = "123456789012"
    aws_region                   = "ap-southeast-1"
    project                      = "ask-david"
    environment                  = "development"
    additional_tags              = {}
    vpc_cidr                     = "10.42.0.0/16"
    public_subnet_cidr           = "10.42.0.0/24"
    application_subnet_cidrs     = ["10.42.16.0/20", "10.42.32.0/20"]
    data_subnet_cidrs            = ["10.42.64.0/20", "10.42.80.0/20"]
    availability_zones           = ["ap-southeast-1a", "ap-southeast-1b"]
    internal_ingress_cidrs       = ["10.42.0.0/16"]
    rds_instance_class           = "db.t4g.micro"
    redis_node_type              = "cache.t4g.micro"
    rds_deletion_protection      = true
    rds_skip_final_snapshot      = false
    log_retention_days           = 30
    enable_opensearch_foundation = false
    opensearch_collection_prefix = "ask-david"
    bucket_name_prefix           = "ask-david-contract"
  }
}
