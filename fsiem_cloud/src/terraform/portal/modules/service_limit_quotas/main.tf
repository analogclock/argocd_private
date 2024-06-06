locals {
  quotas = var.environment == "prod" ? local.quotas_prod : local.quotas_dev
  quotas_dev = {
    "vpcs_per_region"                  = 50
    "elastic_ips_per_region"           = 50
    "network_firewalls_per_region"     = 50
    "nat_gateways_per_az"              = 50
    "sec_groups_per_network_interface" = 10
    "ipv4_blocks_per_vpc"              = 10
  }
  quotas_prod = {
    "vpcs_per_region"                  = 500
    "elastic_ips_per_region"           = 1500
    "network_firewalls_per_region"     = 50
    "nat_gateways_per_az"              = 500
    "sec_groups_per_network_interface" = 10
    "ipv4_blocks_per_vpc"              = 10
  }
}

/*
AWS CLI command to get AWS service codes
'aws service-quotas list-services --query Services[*].ServiceCode'

AWS CLI command get quota code for the aws service (example:network-firewall)
'aws service-quotas list-service-quotas --service-code network-firewall'
*/

# One per deployment
resource "aws_servicequotas_service_quota" "vpcs_per_region" {
  quota_code   = "L-F678F1CE"
  service_code = "vpc"
  value        = local.quotas["vpcs_per_region"]
}

# Three per deployment
# Disabled for now as we need more elastic IPs for testing
# resource "aws_servicequotas_service_quota" "elastic_ips_per_region" {
#   quota_code   = "L-0263D0A3"
#   service_code = "ec2"
#   value        = local.quotas["elastic_ips_per_region"]
# }

# One in each AZ per deployment
resource "aws_servicequotas_service_quota" "nat_gateways_per_az" {
  quota_code   = "L-FE5A380F"
  service_code = "vpc"
  value        = local.quotas["nat_gateways_per_az"]
}

resource "aws_servicequotas_service_quota" "sec_groups_per_network_interface" {
  quota_code   = "L-2AFB9258"
  service_code = "vpc"
  value        = local.quotas["sec_groups_per_network_interface"]
}

resource "aws_servicequotas_service_quota" "ipv4_blocks_per_vpc" {
  quota_code   = "L-83CA0A9D"
  service_code = "vpc"
  value        = local.quotas["ipv4_blocks_per_vpc"]
}

# One per deployment
# Currently disabled as the firewalls are not in use and we don't so many right now
# resource "aws_servicequotas_service_quota" "network_firewalls_per_region" {
#   quota_code   = "L-DE163D32"
#   service_code = "network-firewall"
#   value        = local.quotas["network_firewalls_per_region"]
# }
