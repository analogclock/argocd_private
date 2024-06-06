/*
  Security groups to control network access to and between the resources
*/

# Ignoring this as it needs all outbound for aws services and forticloud, which keeps its public IPs secret
#tfsec:ignore:aws-vpc-no-public-egress-sgr
resource "aws_security_group" "lambda" {
  vpc_id = module.vpc.vpc_id
  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ECR VPC Endpoints
resource "aws_security_group" "ecr_endpoint" {
  name   = "portal-${var.environment}-ecr"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "ecr_endpoints" {
  description              = "Access from default sec group to ECR endpoints"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecr_endpoint.id
  source_security_group_id = module.vpc.default_security_group_id
}

resource "aws_security_group_rule" "ecr_lambda" {
  description              = "Access from lambda sec group to ECR endpoints"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecr_endpoint.id
  source_security_group_id = aws_security_group.lambda.id
}

resource "aws_security_group_rule" "ecr_terraform_updater" {
  description              = "Access from terraform updater to ECR endpoints"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecr_endpoint.id
  source_security_group_id = aws_security_group.terraform_updater.id
}

resource "aws_security_group_rule" "ecr_scheduled_upgrade" {
  description              = "Access from scheduled upgrade to ECR endpoints"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecr_endpoint.id
  source_security_group_id = aws_security_group.scheduled_upgrade.id
}

# Default sec group rules
resource "aws_security_group_rule" "default_vpc_endpoints" {
  description              = "Access from default sec group to interface vpc endpoints"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = module.vpc.default_security_group_id
  source_security_group_id = aws_security_group.ecr_endpoint.id
}

resource "aws_security_group_rule" "default_s3_gateway" {
  description       = "Access from default sec group to S3 VPC endpoint gateway"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = module.vpc.default_security_group_id
  cidr_blocks       = data.aws_prefix_list.s3.cidr_blocks
}

# Terraform updater
resource "aws_security_group" "terraform_updater" {
  name   = "terraform-updater-${var.environment}"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "terraform_updater_vpc_endpoints" {
  description              = "Access from terraform updater to interface vpc endpoints"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.terraform_updater.id
  source_security_group_id = aws_security_group.ecr_endpoint.id
}

resource "aws_security_group_rule" "terraform_updater_egress_s3" {
  description       = "Access from terraform updater to S3 VPC endpoint gateway"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.terraform_updater.id
  cidr_blocks       = data.aws_prefix_list.s3.cidr_blocks
}

resource "aws_security_group_rule" "terraform_updater_egress_https" {
  description       = "Access from terraform updater to all https"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.terraform_updater.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# Scheduled upgrade
resource "aws_security_group" "scheduled_upgrade" {
  name   = "scheduled-upgrade-${var.environment}"
  vpc_id = module.vpc.vpc_id
}

resource "aws_security_group_rule" "scheduled_upgrade_vpc_endpoints" {
  description              = "Access from scheduled upgrade to interface vpc endpoints"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.scheduled_upgrade.id
  source_security_group_id = aws_security_group.ecr_endpoint.id
}

resource "aws_security_group_rule" "scheduled_upgrade_egress_s3" {
  description       = "Access from scheduled upgrade to S3 VPC endpoint gateway"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.scheduled_upgrade.id
  cidr_blocks       = data.aws_prefix_list.s3.cidr_blocks
}

# This should be replaced with VPC endpoints
resource "aws_security_group_rule" "scheduled_upgrade_egress_https" {
  description       = "Access from scheduled upgrade to all https"
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.scheduled_upgrade.id
  cidr_blocks       = ["0.0.0.0/0"]
}
