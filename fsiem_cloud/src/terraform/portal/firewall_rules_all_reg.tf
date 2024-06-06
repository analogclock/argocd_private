/*
  Create firewall rules required in all AWS regions supported by FSIEM.
  The default region is us-east-1.
  The module firewall_rules is invoked here.
*/

module "fwrules-us-east-1" {
  source      = "./modules/firewall_rules"
  fwrules_env = var.environment
}

module "fwrules-eu-central-1" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment

  providers = { aws = aws.eu-central-1 }
}

module "fwrules-eu-west-1" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment

  providers = { aws = aws.eu-west-1 }
}

module "fwrules-eu-west-2" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.eu-west-2 }
}

module "fwrules-eu-west-3" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.eu-west-3 }
}

module "fwrules-eu-north-1" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.eu-north-1 }
}

module "fwrules-us-east-2" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.us-east-2 }
}

module "fwrules-us-west-2" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.us-west-2 }
}

module "fwrules-ca-central-1" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.ca-central-1 }
}

module "fwrules-ap-south-1" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment

  providers = { aws = aws.ap-south-1 }
}

module "fwrules-ap-southeast-1" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.ap-southeast-1 }
}

module "fwrules-ap-southeast-2" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.ap-southeast-2 }
}

module "fwrules-me-south-1" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.me-south-1 }
}

module "fwrules-ap-east-1" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.ap-east-1 }
}

module "fwrules-af-south-1" {
  source      = "./modules/firewall_rules/"
  fwrules_env = var.environment
  providers   = { aws = aws.af-south-1 }
}
