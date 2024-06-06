/*
  This is the IAM role and profile for the all of the ec2 instances. Currently just basic permissions to run.
*/
data "aws_iam_policy_document" "instance_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ecs_task_assume_role_policy" {
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

data "aws_iam_policy_document" "update_metrics_table_policy" {
  statement {
    actions = [
      "dynamodb:Scan",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:PartiQLInsert",
      "dynamodb:PartiQLUpdate"
    ]
    resources = [
      local.dynamodb_metrics_storage_table_arn
    ]
  }
}

data "aws_iam_policy_document" "update_dynamodb_policy" {
  statement {
    actions = [
      "dynamodb:Scan",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:PartiQLInsert",
      "dynamodb:PartiQLUpdate"
    ]
    resources = [
      local.dynamodb_activation_table_arn
    ]
  }
}

data "aws_iam_policy_document" "instance_get_s3_scripts_policy" {
  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      local.s3_scripts_bucket_arn,
      "${local.s3_scripts_bucket_arn}/*",
      local.s3_upgrade_packages_bucket_arn,
      "${local.s3_upgrade_packages_bucket_arn}/*"
    ]
  }
}

resource "aws_iam_role_policy" "instance_get_s3_scripts_policy" {
  role   = aws_iam_role.instance_role.id
  policy = data.aws_iam_policy_document.instance_get_s3_scripts_policy.json
}

data "aws_iam_policy_document" "taclogs_bucket_policy" {
  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
      "s3:PutObject"
    ]
    resources = [
      local.s3_taclogs_bucket_arn,
      "${local.s3_taclogs_bucket_arn}/${var.serial_number}/*"
    ]
  }
}

resource "aws_iam_role_policy" "taclogs_bucket_policy" {
  role   = aws_iam_role.instance_role.id
  policy = data.aws_iam_policy_document.taclogs_bucket_policy.json
}

data "aws_iam_policy_document" "external_storage_policy" {
  statement {
    actions = [
      "s3:ListBucket",
      "s3:PutObject"
    ]
    resources = [
      "arn:aws:s3:::${var.external_storage_prefix}-*"
    ]
  }
}

resource "aws_iam_role_policy" "external_storage_role_policy" {
  role   = aws_iam_role.instance_role.id
  policy = data.aws_iam_policy_document.external_storage_policy.json
}

# Clickhouse S3 bucket policy
# TODO: Reduce the scope here, there is no standard defined
# by the clickhouse team here:
# https://clickhouse.com/docs/en/guides/sre/configuring-s3-for-clickhouse-use/
data "aws_iam_policy_document" "clickhouse_archive_bucket_policy" {
  statement {
    actions = [
      "s3:*"
    ]
    resources = [
      "${local.clickhouse_data_arn}/${local.clickhouse_archive_dir_name}/*"
    ]
  }
}

resource "aws_iam_role_policy" "clickhouse_archive_bucket_policy" {
  role   = aws_iam_role.instance_role.id
  policy = data.aws_iam_policy_document.clickhouse_archive_bucket_policy.json
}

# Clickhouse S3 backup bucket policy, based on requirements in
# https://github.com/AlexAkulov/clickhouse-backup#s3
data "aws_iam_policy_document" "clickhouse_backup_bucket_policy" {
  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject"
    ]
    resources = [
      "${local.clickhouse_backup_arn}/${local.clickhouse_backup_dir_name}/*"
    ]
  }
  statement {
    actions   = ["s3:ListBucket"]
    resources = [local.clickhouse_backup_arn]
  }
}

resource "aws_iam_role_policy" "clickhouse_backup_bucket_policy" {
  role   = aws_iam_role.instance_role.id
  policy = data.aws_iam_policy_document.clickhouse_backup_bucket_policy.json
}

data "aws_iam_policy_document" "ssm_session_manager_policy" {
  statement {
    actions = [
      "ssmmessages:CreateControlChannel",
      "ssmmessages:CreateDataChannel",
      "ssmmessages:OpenControlChannel",
      "ssmmessages:OpenDataChannel",
      "ssm:UpdateInstanceInformation",
      "s3:GetEncryptionConfiguration",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams"
    ]
    resources = [
      "*"
    ]
  }
  statement {
    actions = [
      "s3:PutObject"
    ]
    resources = [
      "${local.session_manager_bucket_arn}/*"
    ]
  }
}

resource "aws_iam_role_policy" "ssm_session_manager_policy" {
  role   = aws_iam_role.instance_role.id
  policy = data.aws_iam_policy_document.ssm_session_manager_policy.json
}

data "aws_iam_policy" "ssm_policy" {
  arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "ssm_policy" {
  policy = data.aws_iam_policy.ssm_policy.policy
  role   = aws_iam_role.instance_role.name
}

resource "aws_iam_role" "instance_role" {
  name               = "${var.serial_number}-fsiem-cloud-${var.environment}"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.instance_assume_role_policy.json
}

resource "aws_iam_instance_profile" "instance_profile" {
  role = aws_iam_role.instance_role.name
}

/*
  IAM permissions to allow for Cloudwatch to schedule tasks
  and execute fargate tasks.
*/
resource "aws_iam_role" "ecs_execution_role" {
  name               = "ecs-${var.serial_number}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

data "aws_iam_policy_document" "ecs_execution_role_policy" {
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
  role   = aws_iam_role.ecs_execution_role.id
  policy = data.aws_iam_policy_document.ecs_execution_role_policy.json
}

data "aws_iam_policy_document" "get_ssm_parameter_policy" {
  statement {
    actions = [
      "ssm:GetParameters"
    ]
    resources = [
      local.parameter_admin_password_arn
    ]
  }
}

resource "aws_iam_role_policy" "get_ssm_parameter_policy" {
  role   = aws_iam_role.ecs_execution_role.id
  policy = data.aws_iam_policy_document.get_ssm_parameter_policy.json
}

data "aws_iam_policy_document" "get_secret_policy" {
  statement {
    actions = [
      "secretsmanager:GetSecret",
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      data.aws_secretsmanager_secret.fsiem_vm_auth_credentials.arn,
      data.aws_secretsmanager_secret.fortimonitor.arn
    ]
  }
}

resource "aws_iam_role_policy" "get_secret_policy" {
  role   = aws_iam_role.ecs_execution_role.id
  policy = data.aws_iam_policy_document.get_secret_policy.json
}

/*
  IAM role for: fsiem setup
*/
resource "aws_iam_role" "fsiem_setup_role" {
  name               = "fsiem-setup-${var.serial_number}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

data "aws_iam_policy_document" "fsiem_setup_policy_doc" {
  statement {
    actions = [
      "ec2:DescribeInstances"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "ssm:GetCommandInvocation",
      "ssm:SendCommand",
      "ssm:ListCommandInvocations"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "fsiem_setup_policy" {
  role   = aws_iam_role.fsiem_setup_role.id
  policy = data.aws_iam_policy_document.fsiem_setup_policy_doc.json
}

resource "aws_iam_role_policy" "fsiem_setup_update_dynamodb_policy" {
  role   = aws_iam_role.fsiem_setup_role.id
  policy = data.aws_iam_policy_document.update_dynamodb_policy.json
}

/*
  IAM role for: fsiem backup
*/
resource "aws_iam_role" "fsiem_backup_role" {
  name               = "fsiem-backup-${var.serial_number}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

resource "aws_iam_role_policy" "fsiem_backup_policy" {
  role   = aws_iam_role.fsiem_backup_role.id
  policy = data.aws_iam_policy_document.fsiem_backup_policy_doc.json
}

data "aws_iam_policy_document" "fsiem_backup_policy_doc" {
  # Send email notifications
  statement {
    actions = [
      "ses:SendEmail"
    ]
    # Example: arn:aws:ses:us-east-1:023941436530:identity/playground.fortisiem.cloud
    resources = ["arn:aws:ses:${var.region}:${local.account_id}:identity/*"]
  }
  # Execute backup/restore using SSM
  statement {
    actions = [
      "ec2:DescribeInstances"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "ssm:GetCommandInvocation",
      "ssm:SendCommand",
      "ssm:ListCommandInvocations",
    ]
    resources = ["*"]
  }
  # Access to DynamoDb backup table
  statement {
    actions = [
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:ExecuteStatement",
      "dynamodb:PartiQLInsert",
      "dynamodb:PartiQLUpdate"
    ]
    resources = [
      local.dynamodb_backup_table_arn,
      local.dynamodb_backup_options_table_arn
    ]
  }
  # Access to DynamoDb restore table
  statement {
    actions = [
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:ExecuteStatement",
      "dynamodb:PartiQLInsert",
      "dynamodb:PartiQLUpdate"
    ]
    resources = [
      local.dynamodb_restore_table_arn
    ]
  }
  # Access to DynamoDb activation table
  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:UpdateItem"
    ]
    resources = [
      local.dynamodb_activation_table_arn
    ]
  }
}
/*
  IAM role for: fsiem license
*/
resource "aws_iam_role" "fsiem_license_role" {
  name               = "fsiem-license-${var.serial_number}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

resource "aws_iam_role_policy" "license_update_dynamodb_policy" {
  role   = aws_iam_role.fsiem_license_role.id
  policy = data.aws_iam_policy_document.update_dynamodb_policy.json
}

data "aws_iam_policy_document" "get_secret_value_policy" {
  statement {
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      data.aws_secretsmanager_secret.licensing_creds.arn
    ]
  }
}

resource "aws_iam_role_policy" "license_get_secret_policy" {
  role   = aws_iam_role.fsiem_license_role.id
  policy = data.aws_iam_policy_document.get_secret_value_policy.json
}

/*
  IAM role for FSIEM metrics
*/
resource "aws_iam_role" "fsiem_metrics_role" {
  name               = "fsiem-metrics-${var.serial_number}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

resource "aws_iam_role_policy" "add_dynamodb_policy_for_metrics" {
  role   = aws_iam_role.fsiem_metrics_role.id
  policy = data.aws_iam_policy_document.update_dynamodb_policy.json
}

resource "aws_iam_role_policy" "add_dynamodb_metrics_policy" {
  role   = aws_iam_role.fsiem_metrics_role.id
  policy = data.aws_iam_policy_document.update_metrics_table_policy.json
}

data "aws_iam_policy_document" "add_s3_for_metrics_policy" {
  statement {
    actions   = ["s3:ListBucket"]
    resources = ["${local.clickhouse_data_arn}"]
  }
}

resource "aws_iam_role_policy" "add_s3_for_metrics" {
  role   = aws_iam_role.fsiem_metrics_role.id
  policy = data.aws_iam_policy_document.add_s3_for_metrics_policy.json
}

data "aws_iam_policy_document" "add_ec2_query_capabilities_policy" {
  statement {
    actions = [
      "ec2:DescribeInstances"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "ssm:GetCommandInvocation",
      "ssm:SendCommand",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "add_ec2_query_capabilities" {
  role   = aws_iam_role.fsiem_metrics_role.id
  policy = data.aws_iam_policy_document.add_ec2_query_capabilities_policy.json
}

/*
  IAM role for fsiem storage enforcer task
*/
resource "aws_iam_role" "fsiem_storage_enforcer_task_role" {
  name               = "fsiem-storage-enforcer-${var.serial_number}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

data "aws_iam_policy_document" "ssm_run_commands_on_ec2_doc" {
  statement {
    actions = [
      "ec2:DescribeInstances",
      "ssm:GetCommandInvocation",
      "ssm:SendCommand",
      "ssm:ListCommandInvocations"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "ssm_run_commands_on_ec2_policy" {
  role   = aws_iam_role.fsiem_storage_enforcer_task_role.id
  policy = data.aws_iam_policy_document.ssm_run_commands_on_ec2_doc.json
}

data "aws_iam_policy_document" "dynamodb_query_on_ec2_policy_doc" {
  statement {
    actions = [
      "dynamodb:Query",
      "dynamodb:UpdateItem",
      "dynamodb:PutItem"
    ]
    resources = [
      local.dynamodb_ext_storage_table_arn,
      local.dynamodb_ext_storage_status_table_arn
    ]
  }
}

resource "aws_iam_role_policy" "dynamodb_query_on_ec2_policy" {
  role   = aws_iam_role.fsiem_storage_enforcer_task_role.id
  policy = data.aws_iam_policy_document.dynamodb_query_on_ec2_policy_doc.json
}

## Cloudwatch scheduled task
data "aws_iam_policy_document" "scheduled_task_cloudwatch_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "events.amazonaws.com",
        "scheduler.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy_document" "scheduled_task_cloudwatch_policy" {
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

resource "aws_iam_role_policy" "scheduled_task_cloudwatch_policy" {
  role   = aws_iam_role.scheduled_task_cloudwatch.id
  policy = data.aws_iam_policy_document.scheduled_task_cloudwatch_policy.json
}

resource "aws_iam_role" "scheduled_task_cloudwatch" {
  name               = "events-ecs-run-task-${var.serial_number}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.scheduled_task_cloudwatch_assume_role_policy.json
}

/*
  IAM role for fsiem monitor task
*/
resource "aws_iam_role" "fsiem_monitor_role" {
  name               = "fsiem-monitor-${var.serial_number}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

resource "aws_iam_role_policy" "fsiem_monitor_update_dynamodb_policy" {
  role   = aws_iam_role.fsiem_monitor_role.id
  policy = data.aws_iam_policy_document.update_dynamodb_policy.json
}

resource "aws_iam_role_policy" "fsiem_monitor_s3_scripts_policy" {
  role   = aws_iam_role.fsiem_monitor_role.id
  policy = data.aws_iam_policy_document.instance_get_s3_scripts_policy.json
}

resource "aws_iam_role_policy" "fsiem_monitor_get_secret_policy" {
  role   = aws_iam_role.fsiem_monitor_role.id
  policy = data.aws_iam_policy_document.get_secret_value_policy.json
}

resource "aws_iam_role_policy" "fsiem_monitor_ssm_run_commands_on_ec2_policy" {
  role   = aws_iam_role.fsiem_monitor_role.id
  policy = data.aws_iam_policy_document.ssm_run_commands_on_ec2_doc.json
}
