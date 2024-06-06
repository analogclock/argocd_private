# Aws Network firewall configurations

# Local values
locals {
  # vpc endpoint id - gateway load balance endpoint created when firewall is added to vpc
  networkfirewall_endpoints = try(tolist(aws_networkfirewall_firewall.anfw[0].firewall_status[0].sync_states)[0].attachment[0].endpoint_id, "")
}

# Create firewall subnet,routing table and routes

resource "aws_subnet" "firewall_subnet" {
  count  = var.has_nfw ? 1 : 0
  vpc_id = module.vpc.vpc_id
  # firewall subnet should be created in the primary az as the private subnet
  availability_zone = var.primary_az
  # firewall CIDR block is different from the private and public CIDRs, but it is still part of the same VPC CIDR
  cidr_block = "10.0.108.0/24"
}

resource "aws_route_table" "firewall_route_table" {
  count  = var.has_nfw ? 1 : 0
  vpc_id = module.vpc.vpc_id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = module.vpc.natgw_ids[0]
  }

  route {
    ipv6_cidr_block        = "::/0"
    egress_only_gateway_id = module.vpc.egress_only_internet_gateway_id
  }
}

# firewall route table explicitly associated to firewall subnet
resource "aws_route_table_association" "firewall_rt_st_association" {
  count          = var.has_nfw ? 1 : 0
  route_table_id = aws_route_table.firewall_route_table[0].id
  subnet_id      = aws_subnet.firewall_subnet[0].id
}

# Create AWS Network firewall
resource "aws_networkfirewall_firewall" "anfw" {
  count               = var.has_nfw ? 1 : 0
  name                = "${var.serial_number}-NFW-${var.environment}"
  firewall_policy_arn = aws_networkfirewall_firewall_policy.anfw_policy[0].arn
  vpc_id              = module.vpc.vpc_id
  subnet_mapping {
    subnet_id = aws_subnet.firewall_subnet[0].id
  }

}

/*
Terraforms's default vpc module creates the vpc for all customer fsiem stacks.
In the private route table created, by default the target for the routes 0.0.0.0/0 and ::/0
is NAT gateway and egress only internet gateway so that the egress traffic to internet will be
routed to internet gateway.

Traffic from private subnet to internet needs to be routed via the firewall vpc endpoint for
the firewall to inspect the egress traffic.
In the private subnet route table ,the routes 0.0.0.0/0 and ::/0 targets
needs to be re routed to target the firewall vpc endpoint.

**The only option available is to use local-exec provisioner to do this.

Firewall route table has the routes 0.0.0.0/0 and ::/0 that will target
NAT gateway and egress only internet gateway respectively so that the
egress traffic to internet will be re-routed to internet gateway after inspection.

The 'triggers' inside null_resource is required as a new timestamp will be generated
every time when terraform plan or apply is executed and that will
force the provisioner to rerun the commands.
The 'depends_on' inside the null_resource will make it automatically wait
for the vpc module to be created and then exexute the null_resource block.
*/

resource "null_resource" "private_sub_null_resource" {
  count = var.has_nfw ? 1 : 0
  triggers = {
    always_run = "${timestamp()}"
  }
  depends_on = [module.vpc.vpc_id]

  provisioner "local-exec" {
    command = "aws ec2 replace-route --route-table-id ${module.vpc.private_route_table_ids[0]} --destination-cidr-block 0.0.0.0/0 --vpc-endpoint-id ${local.networkfirewall_endpoints}"
  }

  provisioner "local-exec" {
    command = "aws ec2 replace-route --route-table-id ${module.vpc.private_route_table_ids[0]} --destination-ipv6-cidr-block ::/0 --vpc-endpoint-id ${local.networkfirewall_endpoints}"
  }

}
