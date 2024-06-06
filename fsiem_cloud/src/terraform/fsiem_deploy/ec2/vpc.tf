/*
  Setup for the VPC. Uses the vpc module for ease of use
*/

locals {
  /*
  if we are using CH then we choose 1 primary (from provisioning), and any other
  availability zone other than the primary from the lists of availabiltty zoness in a region
  */
  /* az's are maintained as a list with primary az as the first item.
  all the instances and nat gateway will be in the primary az
  please do not change the order as of the az's as this will result
  in inter availabiilty zone data transfer which will have addtional costs.
  */
  clickhouse_azs = concat(local.primary_availability_zone, tolist(setsubtract(data.aws_availability_zones.available.names, local.primary_availability_zone)))
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0.0"

  name = var.serial_number
  cidr = "10.0.0.0/16"

  azs = local.clickhouse_azs

  private_subnets = ["10.0.101.0/24"]
  public_subnets  = ["10.0.104.0/24", "10.0.105.0/24"]

  enable_nat_gateway = true
  /* If single_nat_gateway = true, then all private subnets will route their
  internet traffic through this single NAT gateway.
  The NAT gateway will be placed in the first public subnet in your
  public_subnets block.(the first availability zone in the aws_subnet.public[*].id list)
  This essentially ties the NAT Gateway to a specific availability zone
  */
  single_nat_gateway     = true
  one_nat_gateway_per_az = false

  enable_vpn_gateway   = false
  enable_dns_hostnames = true
  enable_dns_support   = true

  enable_ipv6 = true

  public_subnet_assign_ipv6_address_on_creation                = true
  public_subnet_enable_dns64                                   = true
  public_subnet_enable_resource_name_dns_aaaa_record_on_launch = true
  public_subnet_ipv6_prefixes                                  = [0, 1]

  private_subnet_enable_dns64                                   = false
  private_subnet_enable_resource_name_dns_aaaa_record_on_launch = false
  # private_subnet_ipv6_prefixes                   = [3, 4, 5]

  manage_default_security_group  = true
  default_security_group_name    = "${var.serial_number}-default"
  default_security_group_egress  = []
  default_security_group_ingress = []

  enable_flow_log                                 = true
  create_flow_log_cloudwatch_log_group            = true
  create_flow_log_cloudwatch_iam_role             = true
  flow_log_destination_type                       = "cloud-watch-logs"
  flow_log_cloudwatch_log_group_name_prefix       = "fsiem_${var.serial_number}_"
  flow_log_cloudwatch_log_group_retention_in_days = local.log_persistance_days_short
  flow_log_per_hour_partition                     = true
  flow_log_traffic_type                           = "ALL"
  /*
  Custom flow log format
  https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html#flow-logs-custom
  flow_log version|account-id|vpc-id|subnet-id|instance-id|
  interface-id|type|srcaddr|dstaddr|srcport|dstport|pkt-srcaddr|pkt-dstaddr|
  protocol|bytes|packets|start|end|action|tcp-flags|log-status|
  region|az-id|sublocation-type|sublocation-id|
  pkt-src-aws-service|pkt-dst-aws-service|flow-direction|traffic-path
  */
  flow_log_log_format = "$${version} $${account-id} $${vpc-id} $${subnet-id} $${interface-id} $${instance-id} $${type} $${srcaddr} $${srcport} $${dstaddr} $${dstport} $${protocol} $${packets} $${bytes} $${action} $${log-status} $${start} $${end} $${flow-direction} $${traffic-path} $${tcp-flags} $${pkt-srcaddr} $${pkt-src-aws-service} $${pkt-dstaddr} $${pkt-dst-aws-service} $${region} $${az-id} $${sublocation-type} $${sublocation-id}"
  /*
  Loginsight query examples
  https://aws.amazon.com/premiumsupport/knowledge-center/cloudwatch-vpc-flow-logs/
  -----------------------example query1--------------------------------------------
parse @message "* * * * * * * * * * * * * * * * * * * * * * * * * * * * *" as version, account_id, vpc_id, subnet_id, interface_id, instance_id, type, srcaddr, srcport, dstaddr, dstport, protocol, packets, bytes, action, log_status, start, end, flow_direction, traffic_path, tcp_flags, pkt_srcaddr, pkt_src_aws_service, pkt_dstaddr, pkt_dst_aws_service, region, az_id, sublocation_type, sublocation_id
| stats sum(bytes) as Data_Transferred by srcaddr, dstaddr, flow_direction
| sort by Data_Transferred desc
| limit 10
  -----------------------example query2--------------------------------------------------
parse @message "* * * * * * * * * * * * * * * * * * * * * * * * * * * * *" as version, account_id, vpc_id, subnet_id, interface_id, instance_id, type, srcaddr, srcport, dstaddr, dstport, protocol, packets, bytes, action, log_status, start, end, flow_direction, traffic_path, tcp_flags, pkt_srcaddr, pkt_src_aws_service, pkt_dstaddr, pkt_dst_aws_service, region, az_id, sublocation_type, sublocation_id
| filter srcaddr = "35.190.4.8"
| limit  15
  --------------------------------------------------------------------------------
  */
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
