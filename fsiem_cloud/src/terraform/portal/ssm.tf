/*
  SSM: automation that interacts with AWS resources as well as
  runs scripts on the instances.
*/
resource "aws_ssm_document" "fsiem_upgrade" {
  name            = "fsiem_upgrade_${var.environment}"
  document_format = "YAML"
  document_type   = "Automation"
  content = templatefile("yaml/ssm_upgrade.yaml",
    {
      assume_role              = aws_iam_role.fsiem_upgrade_ssm_role.arn
      environment              = var.environment
      backup_vault_name        = aws_backup_vault.vault.id
      backup_role              = aws_iam_role.fsiem_upgrade_create_backup_role.arn
      region                   = var.region
      bucket                   = local.s3_upgrade_packages_bucket
      ssm_log_group            = local.ssm_automation_lg
      user                     = "ec2-user"
      s3_scripts_bucket        = local.s3_scripts_bucket
      s3_scripts_bucket_region = var.region
    }
  )
}

resource "aws_ssm_document" "fsiem_tac_logs" {
  name            = "fsiem_tac_logs_${var.environment}"
  document_format = "YAML"
  document_type   = "Automation"
  content = templatefile("yaml/ssm_tac_logs.yaml",
    {
      assume_role   = aws_iam_role.fsiem_upgrade_ssm_role.arn
      environment   = var.environment
      region        = var.region
      ssm_log_group = local.ssm_automation_lg
    }
  )
}

resource "aws_ssm_document" "test_external_storage" {
  name            = "fsiem_test_ext_storage_${var.environment}"
  document_format = "YAML"
  document_type   = "Automation"
  content = templatefile("yaml/ssm_test_ext_storage.yaml",
    {
      assume_role   = aws_iam_role.fsiem_ext_storage_test_ssm_role.arn
      environment   = var.environment
      region        = var.region
      ssm_log_group = local.ssm_automation_lg
      account_id    = data.aws_caller_identity.current.account_id
    }
  )
}

resource "aws_ssm_document" "ingestion_setup" {
  name            = "fsiem_ingestion_setup_${var.environment}"
  document_format = "YAML"
  document_type   = "Automation"
  content = templatefile("yaml/ssm_ingestion_setup.yaml",
    {
      assume_role              = aws_iam_role.fsiem_upgrade_ssm_role.arn
      environment              = var.environment
      s3_scripts_bucket        = local.s3_scripts_bucket
      s3_scripts_bucket_region = var.region
      ssm_log_group            = local.ssm_automation_lg
      user                     = "ec2-user"
      num_exp_disks            = 2
    }
  )
}
