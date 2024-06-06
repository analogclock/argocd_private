/*
  Security groups to control network access to and between the resources
*/

resource "aws_security_group" "collector" {
  count  = var.data_collectors > 0 ? 1 : 0
  name   = "${var.bm_serial_number}-collector"
  vpc_id = data.aws_vpc.bmvpc.id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "collector_ingress_all" {
  count             = var.data_collectors > 0 ? 1 : 0
  description       = "All inbound"
  type              = "ingress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.collector[0].id
  cidr_blocks       = ["0.0.0.0/0"]
}


# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "collector_egress_all" {
  count             = var.data_collectors > 0 ? 1 : 0
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.collector[0].id
  cidr_blocks       = ["0.0.0.0/0"]
}

