/*
  Sets up WAF for super in all required regions
*/

module "waf-super-us-east-1" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
}

module "waf-super-eu-central-1" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.eu-central-1
  }
}

module "waf-super-eu-west-1" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.eu-west-1
  }
}

module "waf-super-eu-west-2" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.eu-west-2
  }
}

module "waf-super-eu-west-3" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.eu-west-3
  }
}

module "waf-super-eu-north-1" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.eu-north-1
  }
}

module "waf-super-us-east-2" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.us-east-2
  }
}

module "waf-super-us-west-2" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.us-west-2
  }
}

module "waf-super-ca-central-1" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.ca-central-1
  }
}

module "waf-super-ap-south-1" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.ap-south-1
  }
}

module "waf-super-ap-southeast-1" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.ap-southeast-1
  }
}

module "waf-super-ap-southeast-2" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.ap-southeast-2
  }
}

module "waf-super-me-south-1" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.me-south-1
  }
}

module "waf-super-ap-east-1" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.ap-east-1
  }
}

module "waf-super-af-south-1" {
  source            = "./modules/waf_super/"
  environment       = var.environment
  retention_in_days = local.log_persistance_days_long
  providers = {
    aws = aws.af-south-1
  }
}
