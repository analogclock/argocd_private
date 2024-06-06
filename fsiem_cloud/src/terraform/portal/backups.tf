/*
  AWS Backup service to backup and restore selected resources, currently EC2 instances,
  EBS and EFS volumes
*/

locals {
  schedule  = "cron(0 0 * * ? *)" # Once a day at midnight
  retention = 3                   # days
}

# Main region backup
resource "aws_backup_vault" "vault" {
  name = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan" {
  name = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault.name
    schedule          = local.schedule
    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection" {
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# us-east-2 region backup
resource "aws_backup_vault" "vault_us_east_2" {
  provider = aws.us-east-2
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_us_east_2" {
  provider = aws.us-east-2
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_us_east_2.name
    schedule          = local.schedule
    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_us_east_2" {
  provider     = aws.us-east-2
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_us_east_2.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# us-west-2 region backup
resource "aws_backup_vault" "vault_us_west_2" {
  provider = aws.us-west-2
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_us_west_2" {
  provider = aws.us-west-2
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_us_west_2.name
    schedule          = local.schedule
    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_us_west_2" {
  provider     = aws.us-west-2
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_us_west_2.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# eu-central-1 region backup
resource "aws_backup_vault" "vault_eu_central_1" {
  provider = aws.eu-central-1
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_eu_central_1" {
  provider = aws.eu-central-1
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_eu_central_1.name
    schedule          = local.schedule
    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_eu_central_1" {
  provider     = aws.eu-central-1
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_eu_central_1.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# eu-west-1 region backup
resource "aws_backup_vault" "vault_eu_west_1" {
  provider = aws.eu-west-1
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_eu_west_1" {
  provider = aws.eu-west-1
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_eu_west_1.name
    schedule          = local.schedule
    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_eu_west_1" {
  provider     = aws.eu-west-1
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_eu_west_1.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# eu-west-2 region backup
resource "aws_backup_vault" "vault_eu_west_2" {
  provider = aws.eu-west-2
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_eu_west_2" {
  provider = aws.eu-west-2
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_eu_west_2.name
    schedule          = local.schedule
    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_eu_west_2" {
  provider     = aws.eu-west-2
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_eu_west_2.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# eu-west-3 region backup
resource "aws_backup_vault" "vault_eu_west_3" {
  provider = aws.eu-west-3
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_eu_west_3" {
  provider = aws.eu-west-3
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_eu_west_3.name
    schedule          = local.schedule
    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_eu_west_3" {
  provider     = aws.eu-west-3
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_eu_west_3.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# eu-north-1 region backup
resource "aws_backup_vault" "vault_eu_north_1" {
  provider = aws.eu-north-1
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_eu_north_1" {
  provider = aws.eu-north-1
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_eu_north_1.name
    schedule          = local.schedule
    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_eu_north_1" {
  provider     = aws.eu-north-1
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_eu_north_1.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# ca-central-1 region backup
resource "aws_backup_vault" "vault_ca_central_1" {
  provider = aws.ca-central-1
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_ca_central_1" {
  provider = aws.ca-central-1
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_ca_central_1.name
    schedule          = local.schedule
    start_window      = 60
    completion_window = 300

    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_ca_central_1" {
  provider     = aws.ca-central-1
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_ca_central_1.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# ap-south-1 region backup
resource "aws_backup_vault" "vault_ap_south_1" {
  provider = aws.ap-south-1
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_ap_south_1" {
  provider = aws.ap-south-1
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_ap_south_1.name
    schedule          = local.schedule
    start_window      = 60
    completion_window = 300

    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_ap_south_1" {
  provider     = aws.ap-south-1
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_ap_south_1.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# ap-southeast-1 region backup
resource "aws_backup_vault" "vault_ap_southeast_1" {
  provider = aws.ap-southeast-1
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_ap_southeast_1" {
  provider = aws.ap-southeast-1
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_ap_southeast_1.name
    schedule          = local.schedule
    start_window      = 60
    completion_window = 300

    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_ap_southeast_1" {
  provider     = aws.ap-southeast-1
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_ap_southeast_1.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# ap-southeast-2 region backup
resource "aws_backup_vault" "vault_ap_southeast_2" {
  provider = aws.ap-southeast-2
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_ap_southeast_2" {
  provider = aws.ap-southeast-2
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_ap_southeast_2.name
    schedule          = local.schedule
    start_window      = 60
    completion_window = 300

    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_ap_southeast_2" {
  provider     = aws.ap-southeast-2
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_ap_southeast_2.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# me-south-1 region backup
resource "aws_backup_vault" "vault_me_south_1" {
  provider = aws.me-south-1
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_me_south_1" {
  provider = aws.me-south-1
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_me_south_1.name
    schedule          = local.schedule
    start_window      = 60
    completion_window = 300

    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_me_south_1" {
  provider     = aws.me-south-1
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_me_south_1.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# af-south-1 region backup
resource "aws_backup_vault" "vault_af_south_1" {
  provider = aws.af-south-1
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_af_south_1" {
  provider = aws.af-south-1
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_af_south_1.name
    schedule          = local.schedule
    start_window      = 60
    completion_window = 300

    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_af_south_1" {
  provider     = aws.af-south-1
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_af_south_1.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}

# ap-east-1 region backup
resource "aws_backup_vault" "vault_ap_east_1" {
  provider = aws.ap-east-1
  name     = "${var.environment}-vault"
}

resource "aws_backup_plan" "plan_ap_east_1" {
  provider = aws.ap-east-1
  name     = "${var.environment}-plan"

  rule {
    rule_name         = "Hourly-backup-7-day-retention"
    target_vault_name = aws_backup_vault.vault_ap_east_1.name
    schedule          = local.schedule
    start_window      = 60
    completion_window = 300

    lifecycle {
      delete_after = local.retention
    }
  }
}

resource "aws_backup_selection" "selection_ap_east_1" {
  provider     = aws.ap-east-1
  iam_role_arn = aws_iam_role.backup_role.arn
  name         = "${var.environment}-selection"
  plan_id      = aws_backup_plan.plan_ap_east_1.id

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = var.environment
  }
}
