mock_provider "aws" {}

run "dedicated_smoke_egress_is_scoped_to_synthetic_nat_fallback" {
  command = plan

  variables {
    name_prefix              = "ask-david-development"
    vpc_cidr                 = "10.42.0.0/16"
    public_subnet_cidr       = "10.42.0.0/24"
    application_subnet_cidrs = ["10.42.16.0/20", "10.42.32.0/20"]
    data_subnet_cidrs        = ["10.42.64.0/20", "10.42.80.0/20"]
    availability_zones       = ["ap-southeast-1a", "ap-southeast-1b"]
    internal_ingress_cidrs   = ["10.42.0.0/16"]
    nat_gateway_mode         = "single"
    tags                     = { Project = "ask-david" }
  }

  assert {
    condition     = aws_vpc_security_group_egress_rule.smoke_https.from_port == 443 && aws_vpc_security_group_egress_rule.smoke_https.to_port == 443 && aws_vpc_security_group_egress_rule.smoke_https.cidr_ipv4 == "0.0.0.0/0" && aws_vpc_security_group_egress_rule.smoke_dns_udp.cidr_ipv4 == "10.42.0.2/32"
    error_message = "The documented synthetic smoke NAT fallback must be HTTPS-only, while DNS remains limited to the VPC resolver."
  }

  assert {
    condition     = aws_vpc_security_group_ingress_rule.rds_smoke.from_port == 5432 && aws_vpc_security_group_ingress_rule.redis_smoke.from_port == 6379 && aws_vpc_security_group_ingress_rule.aws_endpoints_smoke.from_port == 443 && aws_vpc_security_group_ingress_rule.rds_workload.from_port == 5432 && aws_vpc_security_group_ingress_rule.redis_workload.from_port == 6379 && aws_vpc_security_group_ingress_rule.aws_endpoints_workload.from_port == 443
    error_message = "RDS, Redis, and endpoint ingress must be standalone and limited to the smoke or workload security groups."
  }

  assert {
    condition     = aws_vpc_security_group_egress_rule.workload_aws_endpoints.from_port == 443 && aws_vpc_security_group_egress_rule.workload_aws_endpoints.to_port == 443 && aws_vpc_security_group_egress_rule.workload_aws_endpoints.referenced_security_group_id == aws_security_group.aws_endpoints.id
    error_message = "The private workload must have exactly the SG-scoped HTTPS egress path to existing AWS interface endpoints."
  }

  assert {
    condition     = aws_vpc_security_group_egress_rule.workload_s3.from_port == 443 && aws_vpc_security_group_egress_rule.workload_s3.to_port == 443 && aws_vpc_security_group_egress_rule.workload_s3.prefix_list_id == aws_vpc_endpoint.s3.prefix_list_id
    error_message = "The private workload must reach ECR image layers through the existing S3 gateway prefix list only."
  }
}
