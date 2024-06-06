/*
  Security groups to control network access to and between the resources
*/
resource "aws_security_group" "super" {
  name   = "super"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "super_https" {
  description              = "Http access from load balancer"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.super.id
  source_security_group_id = aws_security_group.super_alb.id
}

resource "aws_security_group_rule" "super_setup" {
  description              = "Http access from setup container"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.super.id
  source_security_group_id = aws_security_group.fsiem_setup.id
}

resource "aws_security_group_rule" "super_license" {
  description              = "Http access from license container"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.super.id
  source_security_group_id = aws_security_group.fsiem_license.id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "super_ingress_worker" {
  description              = "Super ingress worker"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.super.id
  source_security_group_id = aws_security_group.worker.id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "super_ingress_keeper" {
  count                    = var.keeper_workers > 0 ? 1 : 0
  description              = "Super ingress worker"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.super.id
  source_security_group_id = aws_security_group.keeper[0].id
}

resource "aws_security_group_rule" "super_ingress_monitor" {
  description              = "Super ingress monitor container"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.super.id
  source_security_group_id = aws_security_group.fsiem_monitor.id
}

resource "aws_security_group_rule" "super_ingress_worker_autoscaling" {
  description              = "Super ingress worker autoscaling container"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.super.id
  source_security_group_id = aws_security_group.fsiem_worker_autoscaling.id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "super_egress_all" {
  description       = "All outbound"
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.super.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group" "worker" {
  name   = "${var.serial_number}-worker"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "worker_https" {
  description              = "Http access from worker alb"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.worker.id
  source_security_group_id = aws_security_group.worker_alb.id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "worker_ingress_super" {
  description              = "Worker ingress super"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.worker.id
  source_security_group_id = aws_security_group.super.id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "worker_ingress_keeper" {
  count                    = var.keeper_workers > 0 ? 1 : 0
  description              = "Worker ingress keeper"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.worker.id
  source_security_group_id = aws_security_group.keeper[0].id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "worker_ingress_worker" {
  description              = "Worker ingress worker"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.worker.id
  source_security_group_id = aws_security_group.worker.id
}

resource "aws_security_group_rule" "worker_ingress_querywkr" {
  description              = "Worker ingress querywkr"
  type                     = "ingress"
  from_port                = 7916
  to_port                  = 7916
  protocol                 = "tcp"
  security_group_id        = aws_security_group.worker.id
  source_security_group_id = aws_security_group.worker.id
}

resource "aws_security_group_rule" "worker_ingress_fortiinsight" {
  description              = "Worker ingress fortiinsight"
  type                     = "ingress"
  from_port                = 5555
  to_port                  = 5555
  protocol                 = "tcp"
  security_group_id        = aws_security_group.worker.id
  source_security_group_id = aws_security_group.worker.id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "worker_egress_all" {
  description       = "All outbound"
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.worker.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# Worker keeper security rules

resource "aws_security_group" "keeper" {
  count  = var.keeper_workers > 0 ? 1 : 0
  name   = "${var.serial_number}-keeper"
  vpc_id = module.vpc.vpc_id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "keeper_egress_all" {
  count             = var.keeper_workers > 0 ? 1 : 0
  description       = "All outbound"
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.keeper[0].id
  cidr_blocks       = ["0.0.0.0/0"]
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "keeper_ingress_super" {
  count                    = var.keeper_workers > 0 ? 1 : 0
  description              = "Keeper ingress super"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.keeper[0].id
  source_security_group_id = aws_security_group.super.id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "keeper_ingress_worker" {
  count                    = var.keeper_workers > 0 ? 1 : 0
  description              = "Keeper ingress worker"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.keeper[0].id
  source_security_group_id = aws_security_group.worker.id
}

# TODO: tighten up this rule once ports are known
resource "aws_security_group_rule" "keeper_ingress_keeper" {
  count                    = var.keeper_workers > 0 ? 1 : 0
  description              = "Keeper ingress keepers"
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.keeper[0].id
  source_security_group_id = aws_security_group.keeper[0].id
}

# Worker Load balancer group and rules
resource "aws_security_group" "worker_alb" {
  name   = "${var.serial_number}-worker-alb"
  vpc_id = module.vpc.vpc_id
  tags = {
    Role = "worker-alb"
  }
}

resource "aws_vpc_security_group_ingress_rule" "worker_alb_ingress_external_ipv4" {
  count             = length(local.ingress_cidrs_ipv4)
  security_group_id = aws_security_group.worker_alb.id
  cidr_ipv4         = local.ingress_cidrs_ipv4[count.index]
  description       = "Load balancer access from external networks"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_vpc_security_group_ingress_rule" "worker_alb_ingress_external_ipv6" {
  count             = length(local.ingress_cidrs_ipv6)
  security_group_id = aws_security_group.worker_alb.id
  cidr_ipv6         = local.ingress_cidrs_ipv6[count.index]
  description       = "Load balancer access from external networks"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_security_group_rule" "worker_alb_egress_worker" {
  description              = "Access from the load balancer to worker"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.worker_alb.id
  source_security_group_id = aws_security_group.worker.id
}

# Super Load balancer group and rules
resource "aws_security_group" "super_alb" {
  name   = "${var.serial_number}-super-alb"
  vpc_id = module.vpc.vpc_id
  tags = {
    Role = "super-alb"
  }
}

resource "aws_vpc_security_group_ingress_rule" "super_alb_ingress_external_ipv4" {
  count             = length(local.ingress_cidrs_ipv4)
  security_group_id = aws_security_group.super_alb.id
  cidr_ipv4         = local.ingress_cidrs_ipv4[count.index]
  description       = "Load balancer access from external networks"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_vpc_security_group_ingress_rule" "super_alb_ingress_external_ipv6" {
  count             = length(local.ingress_cidrs_ipv6)
  security_group_id = aws_security_group.super_alb.id
  cidr_ipv6         = local.ingress_cidrs_ipv6[count.index]
  description       = "Load balancer access from external networks"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_security_group_rule" "super_alb_egress_worker" {
  description              = "Access from the load balancer to super"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.super_alb.id
  source_security_group_id = aws_security_group.super.id
}

# Setup container group and rules
resource "aws_security_group" "fsiem_setup" {
  name   = "${var.serial_number}-fsiem-setup"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "fsiem_setup_super_egress" {
  description              = "Access to super from setup container"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.fsiem_setup.id
  source_security_group_id = aws_security_group.super.id
}

resource "aws_security_group_rule" "fsiem_setup_ecr_egress" {
  description       = "Allow any outgoing tcp traffic to dest port 443"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.fsiem_setup.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# Backup container group and rules
resource "aws_security_group" "fsiem_backup" {
  name   = "${var.serial_number}-fsiem-backup"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "fsiem_backup_https_egress" {
  description       = "Allow any outgoing tcp traffic to dest port 443"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.fsiem_backup.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# Storage enforcer container group and rules
resource "aws_security_group" "fsiem_storage_enforcer" {
  name   = "${var.serial_number}-fsiem-storage-enforcer"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "fsiem_storage_enforcer_ecr_egress" {
  description       = "Allow any outgoing tcp traffic to dest port 443"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.fsiem_storage_enforcer.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# License container group and rules
resource "aws_security_group" "fsiem_license" {
  name   = "${var.serial_number}-fsiem-license"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "fsiem_license_super_egress" {
  description              = "Access to super from license container"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.fsiem_license.id
  source_security_group_id = aws_security_group.super.id
}

resource "aws_security_group_rule" "fsiem_license_ecr_egress" {
  description       = "Allow any outgoing tcp traffic to dest port 443"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.fsiem_license.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# Metrics container group and rules
resource "aws_security_group" "fsiem_metrics" {
  name   = "${var.serial_number}-fsiem-metrics"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "fsiem_metrics_ecr_egress" {
  description       = "Allow any outgoing tcp traffic to dest port 443"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.fsiem_metrics.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# Metrics container group and rules
resource "aws_security_group" "fsiem_monitor" {
  name   = "${var.serial_number}-fsiem-monitor"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "fsiem_monitor_super_egress" {
  description              = "Access to super from monitor container"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.fsiem_monitor.id
  source_security_group_id = aws_security_group.super.id
}

resource "aws_security_group_rule" "fsiem_monitor_egress_443" {
  description       = "Https egress for internet access from monitor container"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.fsiem_monitor.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "fsiem_monitor_egress_80" {
  description       = "Http access for internet access from monitor container"
  type              = "egress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  security_group_id = aws_security_group.fsiem_monitor.id
  cidr_blocks       = ["0.0.0.0/0"]
}


# Worker autoscaling container
resource "aws_security_group" "fsiem_worker_autoscaling" {
  name   = "${var.serial_number}-fsiem-worker-autoscaling"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "fsiem_worker_autoscaling_super_egress" {
  description              = "Access to super from worker autoscaling container"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.fsiem_worker_autoscaling.id
  source_security_group_id = aws_security_group.super.id
}

resource "aws_security_group_rule" "fsiem_worker_autoscaling_ecr_egress" {
  description       = "Allow any outgoing tcp traffic to dest port 443"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.fsiem_worker_autoscaling.id
  cidr_blocks       = ["0.0.0.0/0"]
}
