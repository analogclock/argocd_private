/* Create SNS topics,access policy,subscription and
 add backup notifications in all Aws regions supported by FSIEM.
 The default region is us-east-1.
 The module backup-alerts is invoked here.
*/

module "bkupsns-us-east-1" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
}

module "bkupsns-eu-central-1" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.eu-central-1
  }
}

module "bkupsns-eu-west-1" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.eu-west-1
  }
}

module "bkupsns-eu-west-2" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.eu-west-2
  }
}

module "bkupsns-eu-west-3" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.eu-west-3
  }
}

module "bkupsns-eu-north-1" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.eu-north-1
  }
}

module "bkupsns-us-east-2" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.us-east-2
  }
}

module "bkupsns-us-west-2" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.us-west-2
  }
}

module "bkupsns-ca-central-1" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.ca-central-1
  }
}

module "bkupsns-ap-south-1" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.ap-south-1
  }
}

module "bkupsns-ap-southeast-1" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.ap-southeast-1
  }
}

module "bkupsns-ap-southeast-2" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.ap-southeast-2
  }
}

module "bkupsns-me-south-1" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.me-south-1
  }
}

module "bkupsns-ap-east-1" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.ap-east-1
  }
}

module "bkupsns-af-south-1" {
  source       = "./modules/backup-alerts/"
  bkupsns_env  = var.environment
  notify_email = local.notification_email
  providers = {
    aws = aws.af-south-1
  }
}
