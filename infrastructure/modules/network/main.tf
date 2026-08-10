locals {
  application_subnets = zipmap(var.availability_zones, var.application_subnet_cidrs)
  data_subnets        = zipmap(var.availability_zones, var.data_subnet_cidrs)
}
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = var.tags
}
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = var.availability_zones[0]
  map_public_ip_on_launch = false
}
resource "aws_subnet" "application" {
  for_each                = local.application_subnets
  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  availability_zone       = each.key
  map_public_ip_on_launch = false
}
resource "aws_subnet" "data" {
  for_each                = local.data_subnets
  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  availability_zone       = each.key
  map_public_ip_on_launch = false
}
resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
}
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }
}
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = merge(var.tags, { NatGatewayMode = var.nat_gateway_mode })
}
resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id
  depends_on    = [aws_internet_gateway.this]
}
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.this.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.this.id
  }
}
resource "aws_route_table_association" "application" {
  for_each       = aws_subnet.application
  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}
resource "aws_route_table_association" "data" {
  for_each       = aws_subnet.data
  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}
resource "aws_security_group" "alb" {
  name_prefix = "${var.name_prefix}-alb-"
  vpc_id      = aws_vpc.this.id
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.internal_ingress_cidrs
  }
}
resource "aws_security_group" "workload" {
  name_prefix = "${var.name_prefix}-workload-"
  vpc_id      = aws_vpc.this.id
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
}

# This group is exclusively for the one-off Goal 3B validation tasks. Future
# workloads and agents must not use it.
resource "aws_security_group" "smoke" {
  name_prefix = "${var.name_prefix}-smoke-"
  vpc_id      = aws_vpc.this.id
  tags = merge(var.tags, {
    Component = "synthetic-smoke-test"
    Purpose   = "goal-3b-private-validation"
  })
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.name_prefix}-rds-"
  vpc_id      = aws_vpc.this.id
}
resource "aws_security_group" "redis" {
  name_prefix = "${var.name_prefix}-redis-"
  vpc_id      = aws_vpc.this.id
}
resource "aws_security_group" "aoss_endpoint" {
  name_prefix = "${var.name_prefix}-aoss-"
  vpc_id      = aws_vpc.this.id
}
resource "aws_security_group" "aws_endpoints" {
  name_prefix = "${var.name_prefix}-aws-endpoints-"
  vpc_id      = aws_vpc.this.id
}

# Keep the validation group separate from the future workload group. Every
# ingress rule for RDS, Redis, and AWS endpoints is standalone: mixing inline
# and standalone rules causes the provider to remove valid smoke access.
# The dedicated, one-off synthetic smoke tasks need TCP/443 through the
# existing NAT fallback because Fargate resolved the digest-pinned ECR
# pull-through image endpoint publicly despite PrivateLink being enabled. Tasks
# have no public IP and this group must never be reused.
#trivy:ignore:AVD-AWS-0104
resource "aws_vpc_security_group_egress_rule" "smoke_https" {
  security_group_id = aws_security_group.smoke.id
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Temporary NAT fallback for synthetic smoke images only"
}

resource "aws_vpc_security_group_egress_rule" "smoke_rds" {
  security_group_id            = aws_security_group.smoke.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  referenced_security_group_id = aws_security_group.rds.id
  description                  = "Static PostgreSQL smoke check only"
}

resource "aws_vpc_security_group_egress_rule" "smoke_redis" {
  security_group_id            = aws_security_group.smoke.id
  ip_protocol                  = "tcp"
  from_port                    = 6379
  to_port                      = 6379
  referenced_security_group_id = aws_security_group.redis.id
  description                  = "Static Redis TLS smoke check only"
}

resource "aws_vpc_security_group_egress_rule" "smoke_dns_udp" {
  security_group_id = aws_security_group.smoke.id
  ip_protocol       = "udp"
  from_port         = 53
  to_port           = 53
  cidr_ipv4         = "${cidrhost(var.vpc_cidr, 2)}/32"
  description       = "VPC resolver for private endpoint DNS"
}

resource "aws_vpc_security_group_egress_rule" "smoke_dns_tcp" {
  security_group_id = aws_security_group.smoke.id
  ip_protocol       = "tcp"
  from_port         = 53
  to_port           = 53
  cidr_ipv4         = "${cidrhost(var.vpc_cidr, 2)}/32"
  description       = "VPC resolver fallback for private endpoint DNS"
}

resource "aws_vpc_security_group_ingress_rule" "rds_smoke" {
  security_group_id            = aws_security_group.rds.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  referenced_security_group_id = aws_security_group.smoke.id
  description                  = "Static PostgreSQL smoke check only"
}

resource "aws_vpc_security_group_ingress_rule" "rds_workload" {
  security_group_id            = aws_security_group.rds.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  referenced_security_group_id = aws_security_group.workload.id
}

resource "aws_vpc_security_group_ingress_rule" "redis_smoke" {
  security_group_id            = aws_security_group.redis.id
  ip_protocol                  = "tcp"
  from_port                    = 6379
  to_port                      = 6379
  referenced_security_group_id = aws_security_group.smoke.id
  description                  = "Static Redis TLS smoke check only"
}

resource "aws_vpc_security_group_ingress_rule" "redis_workload" {
  security_group_id            = aws_security_group.redis.id
  ip_protocol                  = "tcp"
  from_port                    = 6379
  to_port                      = 6379
  referenced_security_group_id = aws_security_group.workload.id
}

resource "aws_vpc_security_group_ingress_rule" "aws_endpoints_smoke" {
  security_group_id            = aws_security_group.aws_endpoints.id
  ip_protocol                  = "tcp"
  from_port                    = 443
  to_port                      = 443
  referenced_security_group_id = aws_security_group.smoke.id
  description                  = "Static smoke access to ECR, Logs, and Secrets Manager endpoints"
}

resource "aws_vpc_security_group_ingress_rule" "aws_endpoints_workload" {
  security_group_id            = aws_security_group.aws_endpoints.id
  ip_protocol                  = "tcp"
  from_port                    = 443
  to_port                      = 443
  referenced_security_group_id = aws_security_group.workload.id
}

data "aws_region" "current" {}
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${data.aws_region.current.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
}
resource "aws_vpc_endpoint" "interface" {
  for_each            = toset(["ecr.api", "ecr.dkr", "logs", "secretsmanager"])
  vpc_id              = aws_vpc.this.id
  service_name        = "com.amazonaws.${data.aws_region.current.region}.${each.value}"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = values(aws_subnet.application)[*].id
  security_group_ids  = [aws_security_group.aws_endpoints.id]
}
