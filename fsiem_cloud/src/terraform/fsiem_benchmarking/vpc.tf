/*
  Setup for the VPC. Uses the vpc module for ease of use
*/

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0.0"

  name = "bm-${var.environment}"
  cidr = "10.0.0.0/16"

  azs = ["${data.aws_availability_zones.available.names[0]}"]

  private_subnets = ["10.0.101.0/24"]
  public_subnets  = ["10.0.104.0/24"]

  enable_nat_gateway   = true
  enable_vpn_gateway   = false
  enable_dns_hostnames = true
  enable_dns_support   = true

  enable_ipv6                                    = false
  public_subnet_assign_ipv6_address_on_creation  = false
  private_subnet_assign_ipv6_address_on_creation = false

  manage_default_security_group  = true
  default_security_group_name    = "${var.serial_number}-default"
  default_security_group_egress  = []
  default_security_group_ingress = []

  enable_flow_log                                 = true
  create_flow_log_cloudwatch_log_group            = true
  create_flow_log_cloudwatch_iam_role             = true
  flow_log_destination_type                       = "cloud-watch-logs"
  flow_log_cloudwatch_log_group_name_prefix       = "fsiem-benchmarking-${var.environment}-"
  flow_log_cloudwatch_log_group_retention_in_days = var.log_persistance_days_short
  flow_log_per_hour_partition                     = true
  flow_log_traffic_type                           = "ALL"

}

# S3 vpc endpoint gateway
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = module.vpc.private_route_table_ids
}

# Gives the cidr blocks used by the gateway
data "aws_prefix_list" "s3" {
  prefix_list_id = aws_vpc_endpoint.s3.prefix_list_id
}
