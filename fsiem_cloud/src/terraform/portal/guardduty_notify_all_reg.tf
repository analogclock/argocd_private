/*
  Create SNS topics,policies,subscriptions & Eventbridge rules required to notify when
  Guardduty findings are detected in all AWS regions supported by FSIEM.
  The default region is us-east-1.
  The module guardduty_alerts is invoked here.
*/

module "gdsns-us-east-1" {
  source       = "./modules/guardduty_alerts"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
}

module "gdsns-eu-central-1" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.eu-central-1
  }
}

module "gdsns-eu-west-1" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.eu-west-1
  }
}

module "gdsn-eu-west-2" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.eu-west-2
  }
}

module "gdsns-eu-west-3" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.eu-west-3
  }
}

module "gdsns-eu-north-1" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.eu-north-1
  }
}

module "gdsns-us-east-2" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.us-east-2
  }
}

module "gdsns-us-west-2" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.us-west-2
  }
}

module "gdsns-ca-central-1" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.ca-central-1
  }
}

module "gdsns-ap-south-1" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.ap-south-1
  }
}

module "gdsns-ap-southeast-1" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.ap-southeast-1
  }
}

module "gdsns-ap-southeast-2" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.ap-southeast-2
  }
}

module "gdsns-me-south-1" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.me-south-1
  }
}

module "gdsns-ap-east-1" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.ap-east-1
  }
}

module "gdsns-af-south-1" {
  source       = "./modules/guardduty_alerts/"
  gdsns_env    = var.environment
  notify_email = local.notification_email
  cert_domain  = var.hosted_zone_name[var.environment]
  providers = {
    aws = aws.af-south-1
  }
}
