#
# Add IAM permissions to allow for EventBridge to schedule tasks
# and execute tasks.
#

# ECS task execution role that the Amazon ECS container agent and
# the Docker daemon can assume.
data "aws_iam_policy_document" "ecs_exec_assume_role_policy_doc" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.fsiem_deployment_role.arn]
    }
  }
}
resource "aws_iam_role" "ecs_exec_role" {
  name               = "portal-${var.environment}-ecs"
  assume_role_policy = data.aws_iam_policy_document.ecs_exec_assume_role_policy_doc.json
}

# Attach policy to ECS exec role. Let ECS container agent
# and the Docker daemon to run tasks, pull images, send logs, etc.
data "aws_iam_policy_document" "ecs_exec_policy_doc" {
  statement {
    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "ecs:RunTask"
    ]
    resources = ["*"]
  }
}
resource "aws_iam_role_policy" "ecs_execution_role_policy" {
  role   = aws_iam_role.ecs_exec_role.id
  policy = data.aws_iam_policy_document.ecs_exec_policy_doc.json
}

# ECS task role. This role allows our Amazon ECS
# container task to make calls to other AWS services.
data "aws_iam_policy_document" "ecs_task_assume_policy_doc" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "ecs_task_role" {
  name               = "portal-${var.environment}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_policy_doc.json
}

# Allow actions from the container in EKS
# Ignored as the wildcard is needed to describe multiple cluster
#tfsec:ignore:aws-iam-no-policy-wildcards
data "aws_iam_policy_document" "ecs_task_policy_doc" {
  statement {
    actions = [
      "eks:DescribeCluster",
      "dynamodb:PartiQLUpdate"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "dynamodb:PartiQLSelect"
    ]
    resources = [
      aws_dynamodb_table.fsiem_compute_override_table.arn
    ]
  }
}
resource "aws_iam_role_policy" "ecs_task_role_policy" {
  role   = aws_iam_role.ecs_task_role.id
  policy = data.aws_iam_policy_document.ecs_task_policy_doc.json
}

data "aws_iam_policy_document" "ecs_task_assume_role_policy_doc" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.ecs_task_role.arn]
    }
  }
}
# TODO: FIX ME
# this needs to be restricted somewhat to just EC2 more than likely
# but for the time being it was causing me lots of issues
data "aws_iam_policy_document" "fsiem_deployment_policy_doc" {
  statement {
    actions   = ["*"]
    resources = ["*"]
  }
}
resource "aws_iam_role" "fsiem_deployment_role" {
  name               = "portal-${var.environment}-deployment-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy_doc.json
  inline_policy {
    name   = "fsiem_deployment_role"
    policy = data.aws_iam_policy_document.fsiem_deployment_policy_doc.json
  }
}

# Eventbridge role
data "aws_iam_policy_document" "eventbridge_assume_role_policy_doc" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "eventbridge_role" {
  name               = "portal-${var.environment}-eventbridge"
  assume_role_policy = data.aws_iam_policy_document.eventbridge_assume_role_policy_doc.json
}

# Allow cloud watch role to run tasks in ECS and pass iam role
data "aws_iam_policy_document" "eventbridge_policy_doc" {
  statement {
    actions = [
      "ecs:RunTask",
      "iam:PassRole"
    ]
    resources = ["*"]
  }
}
resource "aws_iam_role_policy" "eventbridge_role_policy" {
  role   = aws_iam_role.eventbridge_role.id
  policy = data.aws_iam_policy_document.eventbridge_policy_doc.json
}


/* Permissions for AWS Backup to backup and restore resources */
data "aws_iam_policy_document" "backup_assume_role_policy_doc" {
  statement {
    sid     = "AssumeServiceRole"
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["backup.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "backup_role" {
  name               = "portal-${var.environment}-backup"
  assume_role_policy = data.aws_iam_policy_document.backup_assume_role_policy_doc.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup",
    "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
  ]
}

/* Needed to allow the backup service to restore from a snapshot to an EC2 instance
 See https://stackoverflow.com/questions/61802628/aws-backup-missing-permission-iampassrole */
data "aws_iam_policy_document" "backup_pass_role_policy_doc" {
  statement {
    sid       = "ExamplePassRole"
    actions   = ["iam:PassRole"]
    effect    = "Allow"
    resources = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*"]
  }
}

resource "aws_iam_role_policy" "backup_pass_role_policy" {
  policy = data.aws_iam_policy_document.backup_pass_role_policy_doc.json
  role   = aws_iam_role.backup_role.name
}

## Cloudwatch scheduled task
data "aws_iam_policy_document" "events_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "events.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy_document" "ecs_run_task_policy_doc" {
  statement {
    actions = [
      "ecs:RunTask"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "iam:PassRole"
    ]
    resources = [
      "*" # TODO: tighten up this policy
    ]
  }
}

resource "aws_iam_role_policy" "events_policy" {
  role   = aws_iam_role.events.id
  policy = data.aws_iam_policy_document.ecs_run_task_policy_doc.json
}

resource "aws_iam_role" "events" {
  name               = "portal-${var.environment}-ecs-run-task"
  assume_role_policy = data.aws_iam_policy_document.events_assume_role_policy.json
}

# IAM role for fsiem terraform updater task
data "aws_iam_policy_document" "fsiem_terraform_updater_role_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "ecs-tasks.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "fsiem_terraform_updater_role" {
  name               = "portal-${var.environment}-terraform-updater"
  assume_role_policy = data.aws_iam_policy_document.fsiem_terraform_updater_role_assume_role_policy.json
}

data "aws_iam_policy_document" "fsiem_terraform_updater_policy" {
  statement {
    actions = [
      "dynamodb:Scan"
    ]
    resources = [
      aws_dynamodb_table.fsiem_activation_table.arn
    ]
  }
  statement {
    actions = [
      "events:PutEvents"
    ]
    resources = [
      "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:event-bus/portal-bus-${var.environment}"
    ]
  }
}

resource "aws_iam_role_policy" "scan_dynamodb_policy" {
  role   = aws_iam_role.fsiem_terraform_updater_role.id
  policy = data.aws_iam_policy_document.fsiem_terraform_updater_policy.json
}

# Daily job permissions
data "aws_iam_policy_document" "daily_job" {
  statement {
    actions   = ["lambda:InvokeFunction"]
    resources = [local.lambda_s3_tag_arn]
  }
  statement {
    actions   = ["iam:PassRole"]
    resources = ["arn:aws:iam::${local.account_id}:role/*"]
  }
  statement {
    actions   = ["dynamodb:Scan"]
    resources = [aws_dynamodb_table.fsiem_activation_table.arn]
  }
}
resource "aws_iam_role_policy" "daily_job" {
  role   = aws_iam_role.daily_job.id
  policy = data.aws_iam_policy_document.daily_job.json
}
resource "aws_iam_role_policy" "daily_job_trigger" {
  role   = aws_iam_role.daily_job.id
  policy = data.aws_iam_policy_document.ecs_exec_policy_doc.json
}
resource "aws_iam_role" "daily_job" {
  name               = "events-lambda-invoke-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_policy_doc.json
}

# IAM role for fsiem scheduled upgrade task
data "aws_iam_policy_document" "fsiem_scheduled_upgrade_role_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "ecs-tasks.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "fsiem_scheduled_upgrade_role" {
  name               = "portal-${var.environment}-fsiem-scheduled-upgrade"
  assume_role_policy = data.aws_iam_policy_document.fsiem_scheduled_upgrade_role_assume_role_policy.json
}

data "aws_iam_policy_document" "fsiem_scheduled_upgrade_policy" {
  statement {
    actions = [
      "dynamodb:Scan",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem"
    ]
    resources = [
      aws_dynamodb_table.fsiem_activation_table.arn,
      aws_dynamodb_table.fsiem_upgrades_table.arn,
      aws_dynamodb_table.fsiem_scheduled_upgrades_table.arn
    ]
  }
  statement {
    actions = [
      "ec2:DescribeInstances",
      "ec2:StopInstances",
      "ec2:StartInstances",
      "ec2:DescribeInstanceStatus",
      "ec2:DescribeSecurityGroups"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "ssm:StartAutomationExecution",
      "ssm:DescribeAutomationExecutions",
      "ssm:DescribeInstanceInformation",
      "ssm:SendCommand",
      "ssm:ListCommands",
      "ssm:ListCommandInvocations"
    ]
    # resources = [aws_ssm_document.fsiem_upgrade_640_650.default_version]
    resources = ["*"]
  }
  statement {
    actions = [
      "events:PutEvents"
    ]
    resources = [
      "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:event-bus/portal-bus-${var.environment}"
    ]
  }
}

resource "aws_iam_role_policy" "fsiem_scheduled_upgrade_policy" {
  role   = aws_iam_role.fsiem_scheduled_upgrade_role.id
  policy = data.aws_iam_policy_document.fsiem_scheduled_upgrade_policy.json
}

# IAM role for fsiem ssm upgrade task
data "aws_iam_policy_document" "fsiem_upgrade_ssm_role_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "ec2.amazonaws.com",
        "ssm.amazonaws.com"
      ]
    }
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
}

resource "aws_iam_role" "fsiem_upgrade_ssm_role" {
  name        = "fsiem-upgrade-ssm-role-${var.environment}"
  description = "Role for fsiem ssm automation on ${var.environment}"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonSSMAutomationRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
  assume_role_policy = data.aws_iam_policy_document.fsiem_upgrade_ssm_role_assume_role_policy.json
}
# IAM policy to support upgrade steps to add and delete inbound rules in alb security groups
data "aws_iam_policy_document" "fsiem_upgrade_ssm_policy" {
  statement {
    actions = [
      "dynamodb:Scan",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem"
    ]
    resources = [
      aws_dynamodb_table.fsiem_activation_table.arn,
      aws_dynamodb_table.fsiem_upgrades_table.arn,
      aws_dynamodb_table.fsiem_scheduled_upgrades_table.arn
    ]
  }
  statement {
    actions = [
      "elasticloadbalancing:*",
      "ec2:DescribeInstances",
      "ec2:StopInstances",
      "ec2:StartInstances",
      "ec2:DescribeInstanceStatus",
      "ec2:DescribeSecurityGroups",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:AuthorizeSecurityGroupIngress",
      "backup:StartBackupJob"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "ssm:StartAutomationExecution",
      "ssm:DescribeAutomationExecutions",
      "ssm:DescribeInstanceInformation",
      "ssm:SendCommand",
      "ssm:ListCommands",
      "ssm:ListCommandInvocations"
    ]
    # resources = [aws_ssm_document.fsiem_upgrade_640_650.default_version]
    resources = ["*"]
  }
  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
      "s3:PutObject"
    ]
    resources = [aws_s3_bucket.taclogs_bucket.arn]
  }
  statement {
    actions = [
      "iam:PassRole"
    ]
    resources = [aws_iam_role.fsiem_upgrade_create_backup_role.arn]
  }
  # IAM policy to support upgrade in Multi accounts and multi regions
  statement {
    actions = [
      "resource-groups:ListGroupResources",
      "tag:GetResources",
      "ec2:DescribeInstances"
    ]
    resources = ["*"]
  }
  statement {
    actions   = ["sts:AssumeRole"]
    resources = [aws_iam_role.fsiem_upgrade_ssm_role.arn]

  }
  statement {
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.fsiem_upgrade_ssm_role.arn]
  }
}

resource "aws_iam_role_policy" "fsiem_upgrade_ssm_policy" {
  role   = aws_iam_role.fsiem_upgrade_ssm_role.id
  policy = data.aws_iam_policy_document.fsiem_upgrade_ssm_policy.json
}

# IAM role for fsiem scheduled upgrade to make a backup of instances
data "aws_iam_policy_document" "fsiem_upgrade_create_backup_role_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "backup.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "fsiem_upgrade_create_backup_role" {
  name                = "portal-${var.environment}-fsiem-upgrade-create-backup"
  assume_role_policy  = data.aws_iam_policy_document.fsiem_upgrade_create_backup_role_assume_role_policy.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"]
}

# IAM role for fsiem expiry notification task
data "aws_iam_policy_document" "fsiem_expiry_notification_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "ecs-tasks.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "fsiem_expiry_notification" {
  name               = "portal-${var.environment}-fsiem-expiry-notification"
  assume_role_policy = data.aws_iam_policy_document.fsiem_expiry_notification_assume_role_policy.json
}

data "aws_iam_policy_document" "fsiem_expiry_notification_policy" {
  statement {
    actions = [
      "dynamodb:Scan"
    ]
    resources = [
      aws_dynamodb_table.fsiem_activation_table.arn
    ]
  }
  statement {
    actions = [
      "dynamodb:GetItem"
    ]
    resources = [
      aws_dynamodb_table.fsiem_email_block_table.arn
    ]
  }
  statement {
    actions = [
      "ses:SendEmail"
    ]
    resources = [
      "arn:aws:ses:${var.region}:${data.aws_caller_identity.current.account_id}:identity/*"
    ]
  }
}

resource "aws_iam_role_policy" "fsiem_expiry_notification_policy" {
  role   = aws_iam_role.fsiem_expiry_notification.id
  policy = data.aws_iam_policy_document.fsiem_expiry_notification_policy.json
}

data "aws_iam_policy_document" "lambda_ssm_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_ssm_policy" {
  statement {
    actions = [
      "dynamodb:Scan",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem"
    ]
    resources = [
      aws_dynamodb_table.fsiem_activation_table.arn,
      aws_dynamodb_table.fsiem_upgrades_table.arn,
      aws_dynamodb_table.fsiem_scheduled_upgrades_table.arn
    ]
  }
  statement {
    actions = [
      "elasticloadbalancing:*",
      "ec2:DescribeInstances",
      "ec2:StopInstances",
      "ec2:StartInstances",
      "ec2:DescribeInstanceStatus",
      "ec2:DescribeSecurityGroups",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:AuthorizeSecurityGroupIngress",
      "backup:StartBackupJob"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
      "s3:PutObject"
    ]
    resources = [aws_s3_bucket.taclogs_bucket.arn]
  }
  statement {
    actions = [
      "iam:PassRole"
    ]
    resources = [aws_iam_role.fsiem_upgrade_create_backup_role.arn]
  }
  statement {
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      aws_secretsmanager_secret.fortimonitor_api_key_write.arn
    ]
  }
  statement {
    actions = [
      "kms:Decrypt"
    ]
    resources = [
      aws_kms_key.key.arn
    ]
  }
}

resource "aws_iam_role" "lambda_ssm_role" {
  name               = "lambda-ssm-${var.environment}"
  description        = "Role for fsiem ssm lambda invokation on ${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_ssm_assume_role_policy.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}

resource "aws_iam_role_policy" "lambda_ssm_role_policy" {
  role   = aws_iam_role.lambda_ssm_role.id
  policy = data.aws_iam_policy_document.lambda_ssm_policy.json

}

# IAM role for fsiem external storage test
data "aws_iam_policy_document" "fsiem_ext_storage_test_ssm_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "ssm.amazonaws.com",
        "ec2.amazonaws.com"
      ]
    }
    principals {
      type        = "AWS"
      identifiers = ["${data.aws_caller_identity.current.account_id}"]
    }
  }
}
resource "aws_iam_role" "fsiem_ext_storage_test_ssm_role" {
  name               = "fsiem-ext-storage-test-ssm-role-${var.environment}"
  description        = "Role for fsiem external storage test ssm automation on ${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.fsiem_ext_storage_test_ssm_assume_role_policy.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonSSMAutomationRole"
  ]
}

# IAM policy to support iam operations requited for external storage test
data "aws_iam_policy_document" "fsiem_ext_storage_test_ssm_policy" {
  statement {
    actions = [
      "ssm:StartAutomationExecution",
      "ssm:DescribeAutomationExecutions",
      "ssm:DescribeInstanceInformation",
      "ssm:SendCommand",
      "ssm:ListCommands",
      "ssm:ListCommandInvocations"
    ]
    resources = [aws_iam_role.fsiem_ext_storage_test_ssm_role.arn]
  }
  # create an iam policy and attach to worker0 to do the external storage test
  # after test is done detach the iam policy from worker0 and delete the policy
  statement {
    actions = [
      "iam:CreatePolicy",
      "iam:AttachRolePolicy",
      "iam:DetachRolePolicy",
      "iam:DeletePolicy",
      "iam:ListAttachedRolePolicies"
    ]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*"
    ]
  }
  # IAM policy to support in Multi accounts and multi regions
  statement {
    actions = [
      "resource-groups:ListGroupResources",
      "tag:GetResources",
      "ec2:DescribeInstances"
    ]
    resources = [aws_iam_role.fsiem_ext_storage_test_ssm_role.arn]
  }
  statement {
    actions   = ["sts:AssumeRole"]
    resources = [aws_iam_role.fsiem_ext_storage_test_ssm_role.arn]

  }
  statement {
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.fsiem_ext_storage_test_ssm_role.arn]
  }
}

resource "aws_iam_role_policy" "fsiem_ext_storage_test_ssm_role_policy" {
  role   = aws_iam_role.fsiem_ext_storage_test_ssm_role.id
  policy = data.aws_iam_policy_document.fsiem_ext_storage_test_ssm_policy.json
}
