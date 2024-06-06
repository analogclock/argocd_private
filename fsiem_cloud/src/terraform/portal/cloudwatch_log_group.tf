/*
  Create cloudwatch log group for ssm_automation in all AWS regions supported by FSIEM.
  The default region is us-east-1.
  The module cloudwatch_log_group is invoked here.
*/


module "log-group-us-east-1" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short
}

module "log-group-eu-central-1" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.eu-central-1
  }
}

module "log-group-eu-west-1" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.eu-west-1
  }
}

module "log-group-eu-west-2" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.eu-west-2
  }
}

module "log-group-eu-west-3" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.eu-west-3
  }
}

module "log-group-eu-north-1" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.eu-north-1
  }
}

module "log-group-us-east-2" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.us-east-2
  }
}

module "log-group-us-west-2" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.us-west-2
  }
}

module "log-group-ca-central-1" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.ca-central-1
  }
}

module "log-group-ap-south-1" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.ap-south-1
  }
}

module "log-group-ap-southeast-1" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.ap-southeast-1
  }
}

module "log-group-ap-southeast-2" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.ap-southeast-2
  }
}
module "log-group-me-south-1" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.me-south-1
  }
}
module "log-group-ap-east-1" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.ap-east-1
  }
}
module "log-group-af-south-1" {
  source            = "./modules/cloudwatch_log_group/"
  name              = local.ssm_automation_lg
  retention_in_days = local.log_persistance_days_short

  providers = {
    aws = aws.af-south-1
  }
}
