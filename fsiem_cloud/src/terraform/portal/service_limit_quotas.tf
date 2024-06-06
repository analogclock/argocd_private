/*
  Sets up service limit quotas for all required regions
*/

module "service-limits-east-1" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
}

module "service-limits-eu-central-1" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.eu-central-1
  }
}

module "service-limits-eu-west-1" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.eu-west-1
  }
}

module "service-limits-eu-west-2" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.eu-west-2
  }
}

module "service-limits-eu-west-3" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.eu-west-3
  }
}

module "service-limits-eu-north-1" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.eu-north-1
  }
}

module "service-limits-us-east-2" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.us-east-2
  }
}

module "service-limits-us-west-2" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.us-west-2
  }
}

module "service-limits-ca-central-1" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.ca-central-1
  }
}

module "service-limits-ap-south-1" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.ap-south-1
  }
}

module "service-limits-ap-southeast-1" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.ap-southeast-1
  }
}

module "service-limits-ap-southeast-2" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.ap-southeast-2
  }
}

module "service-limits-me-south-1" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.me-south-1
  }
}

module "service-limits-ap-east-1" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.ap-east-1
  }
}

module "service-limits-af-south-1" {
  source      = "./modules/service_limit_quotas/"
  environment = var.environment
  providers = {
    aws = aws.af-south-1
  }
}
