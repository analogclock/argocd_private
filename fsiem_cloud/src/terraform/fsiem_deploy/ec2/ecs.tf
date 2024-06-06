/*
  This file creates a Fargate ECS cluster to host the setup components
*/

locals {
  ecs_name          = "${var.serial_number}-ecs"
  fsiem_backup_name = "fsiem_backup_${var.serial_number}"
  fsiem_setup_name  = "fsiem_setup_${var.serial_number}"
  fsiem_license     = "fsiem_license_${var.serial_number}"
  fsiem_metrics     = "fsiem_metrics_${var.serial_number}"
}

module "ecs" {
  source       = "terraform-aws-modules/ecs/aws"
  version      = "~> 5.2.0"
  cluster_name = local.ecs_name
  fargate_capacity_providers = {
    FARGATE      = {}
    FARGATE_SPOT = {}
  }
  cluster_settings = {
    "name" : "containerInsights",
    "value" : "disabled"
  }
}

# ARN of secrets that are passed to containers via env variables.
# Such as ARN of VM authentication secret and ARN of licensing secret
data "aws_secretsmanager_secrets" "fsiem_vm_auth_credentials" {
  filter {
    name   = "name"
    values = ["fsiem-vm-auth-creds-${var.environment}"]
  }
}

data "aws_secretsmanager_secret" "fsiem_vm_auth_credentials" {
  arn = tolist(data.aws_secretsmanager_secrets.fsiem_vm_auth_credentials.arns)[0]
}

data "aws_secretsmanager_secrets" "licensing_creds" {
  filter {
    name   = "name"
    values = ["licensing-creds-${var.environment}"]
  }
}

data "aws_secretsmanager_secret" "licensing_creds" {
  arn = tolist(data.aws_secretsmanager_secrets.licensing_creds.arns)[0]
}

# Definition for the fsiem setup task
resource "aws_ecs_task_definition" "fsiem_setup" {
  family                   = local.fsiem_setup_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.fsiem_setup_role.arn

  container_definitions = jsonencode([
    {
      name : local.fsiem_setup_name,
      image : local.fsiem_setup_ecr_repo_url,
      secrets : [
        { name : "NEW_PASSWORD", valueFrom : local.parameter_admin_password_arn },
        { name : "SECRET_VM_AUTH", valueFrom : data.aws_secretsmanager_secret.fsiem_vm_auth_credentials.arn },
      ],
      environment : [
        { name : "SUPER_URL", value : aws_instance.super.private_ip },
        { name : "COGNITO_URL", value : local.cognito_url },
        {
          name : "CLICKHOUSE_S3_BUCKET",
          value : "${local.clickhouse_data_bucket}/${local.clickhouse_archive_dir_name}"
        },
        { name : "CLICKHOUSE_S3_REGION", value : var.region },
        { name : "EMAIL", value : var.deployment_email },
        { name : "WORKER_URL", value : aws_route53_record.worker.fqdn },
        { name : "SERIAL_NUMBER", value : var.serial_number },
        { name : "DYNAMODB_ACTIVATION_TABLE", value : local.dynamodb_activation_table },
        { name : "DYNAMODB_REGION", value : local.portal_region },
        { name : "APP_SERVER_MEM_GB", value : "${var.app_server_mem_gb}" }
      ],
      logConfiguration : {
        logDriver : "awslogs",
        options : {
          "awslogs-group" : local.fsiem_setup_name,
          "awslogs-region" : var.region,
          "awslogs-stream-prefix" : "ecs"
        }
      }
    }
  ])
}

# Cloudwatch logs
resource "aws_cloudwatch_log_group" "fsiem_setup" {
  name              = local.fsiem_setup_name
  retention_in_days = local.log_persistance_days_short
}

# Cloudwatch event to trigger the fsiem-setup task
resource "aws_cloudwatch_event_rule" "fsiem_setup" {
  name                = "${local.fsiem_setup_name}_${var.environment}"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "fsiem_setup" {
  rule     = aws_cloudwatch_event_rule.fsiem_setup.name
  arn      = module.ecs.cluster_arn
  role_arn = aws_iam_role.scheduled_task_cloudwatch.arn
  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.fsiem_setup.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = module.vpc.private_subnets
      security_groups = [aws_security_group.fsiem_setup.id]
    }
  }
}

# Definition for the fsiem clickhouse backup task
resource "aws_ecs_task_definition" "fsiem_backup" {
  family                   = local.fsiem_backup_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.fsiem_backup_role.arn
  container_definitions = jsonencode([
    {
      name : local.fsiem_backup_name,
      image : local.fsiem_backup_ecr_repo_url,
      environment : [
        { name : "SERIAL_NUMBER", value : var.serial_number },
        { name : "DYNAMODB_BACKUP_TABLE", value : local.dynamodb_backup_table },
        { name : "DYNAMODB_BACKUP_OPTIONS_TABLE", value : local.dynamodb_backup_options_table },
        { name : "DYNAMODB_REGION", value : local.portal_region },
        { name : "DYNAMODB_ACTIVATION_TABLE", value : local.dynamodb_activation_table },
        { name : "REGION", value : var.region },
        { name : "REMOTE_STORAGE", value : "s3" },
        { name : "LOG_LEVEL", value : "WARN" },
        { name : "S3_BUCKET", value : local.clickhouse_backup_bucket },
        { name : "S3_PATH", value : var.serial_number },
        { name : "S3_COMPRESSION_LEVEL", value : "1" },
        { name : "S3_COMPRESSION_FORMAT", value : "tar" },
        { name : "S3_USE_CUSTOM_STORAGE_CLASS", value : "false" },
        { name : "S3_STORAGE_CLASS", value : "STANDARD" },
        { name : "S3_CONCURRENCY", value : "1" },
        { name : "S3_DEBUG", value : "false" },
        { name : "MAX_BACKUPS_IN_CHAIN", value : "3" },
        { name : "EMAIL_FROM_ADDR", value : local.email_from_addr },
        { name : "EMAIL_TO_ADDR", value : local.email_to_addr },
      ],
      logConfiguration : {
        logDriver : "awslogs",
        options : {
          "awslogs-group" : local.fsiem_backup_name,
          "awslogs-region" : var.region,
          "awslogs-stream-prefix" : "ecs"
        }
      }
    }
  ])
}

# Cloudwatch logs
resource "aws_cloudwatch_log_group" "fsiem_backup" {
  name              = local.fsiem_backup_name
  retention_in_days = local.log_persistance_days_long
}

# Scheduler that triggers ECS backup container using local time zone
resource "aws_scheduler_schedule" "fsiem_backup" {
  name        = "${local.fsiem_backup_name}_${var.environment}"
  description = <<EOT
    Trigger to run ECS backup container for ${local.fsiem_backup_name}
    at 2AM using ${local.region_tz} timezone
  EOT
  flexible_time_window {
    mode = "OFF"
  }

  # Runs once a day, at 2 AM local time, for example:
  # Fri, 02 Jun 2023 02:00:00 (UTC -07:00)
  # Sat, 03 Jun 2023 02:00:00 (UTC -07:00)
  # Sun, 04 Jun 2023 02:00:00 (UTC -07:00)
  schedule_expression = "cron(0 2 * * ? *)"

  # IANA timezone, such as 'America/Los_Angeles'
  schedule_expression_timezone = local.region_tz

  target {
    arn      = module.ecs.cluster_arn
    role_arn = aws_iam_role.scheduled_task_cloudwatch.arn
    ecs_parameters {
      task_count          = 1
      task_definition_arn = aws_ecs_task_definition.fsiem_backup.arn
      launch_type         = "FARGATE"
      network_configuration {
        subnets         = module.vpc.private_subnets
        security_groups = [aws_security_group.fsiem_backup.id]
      }
    }
    retry_policy {
      # Maximum amount of time, in seconds, to continue to make retry attempts
      maximum_event_age_in_seconds = 3600 # 1 hour in seconds
      # Maximum number of retry attempts to make before the request fails
      maximum_retry_attempts = 3
    }
  }
}


# Definition for the fsiem license task
resource "aws_ecs_task_definition" "fsiem_license" {
  family                   = local.fsiem_license
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.fsiem_license_role.arn
  container_definitions = jsonencode([
    {
      name : local.fsiem_license,
      image : local.fsiem_license_ecr_repo_url,
      secrets : [
        { name : "NEW_PASSWORD", valueFrom : local.parameter_admin_password_arn },
        { name : "SECRET_ID_VM_AUTH", valueFrom : data.aws_secretsmanager_secret.fsiem_vm_auth_credentials.arn }
      ],
      environment : [
        { name : "SUPER_URL", value : aws_instance.super.private_ip },
        { name : "LICENSE_TYPE", value : var.deployment_type },
        { name : "DEFAULT_PASSWORD", value : "admin*1" },
        { name : "SECRET_ID", value : data.aws_secretsmanager_secret.licensing_creds.arn },
        { name : "COGNITO_URL", value : local.cognito_url },
        { name : "PORTAL_API_URL", value : local.portal_api_url[var.environment] },
        { name : "SERIAL_NUMBER", value : var.serial_number },
        { name : "DYNAMODB_ACTIVATION_TABLE", value : local.dynamodb_activation_table },
        { name : "DYNAMODB_REGION", value : local.portal_region }
      ],
      logConfiguration : {
        logDriver : "awslogs",
        options : {
          "awslogs-group" : local.fsiem_license,
          "awslogs-region" : var.region,
          "awslogs-stream-prefix" : "ecs"
        }
      }
    }
  ])
}

# Cloudwatch logs
resource "aws_cloudwatch_log_group" "fsiem_license" {
  name              = local.fsiem_license
  retention_in_days = local.log_persistance_days_long
}

# Cloudwatch event to trigger the fsiem_license
resource "aws_cloudwatch_event_rule" "fsiem_license" {
  name                = "${local.fsiem_license}_${var.environment}"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "fsiem_license" {
  rule     = aws_cloudwatch_event_rule.fsiem_license.name
  arn      = module.ecs.cluster_arn
  role_arn = aws_iam_role.scheduled_task_cloudwatch.arn
  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.fsiem_license.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = module.vpc.private_subnets
      security_groups = [aws_security_group.fsiem_license.id]
    }
  }
}

# Definition for the fsiem metrics task
resource "aws_ecs_task_definition" "fsiem_metrics" {
  family                   = local.fsiem_metrics
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.fsiem_metrics_role.arn
  container_definitions = jsonencode([
    {
      name : local.fsiem_metrics,
      image : local.fsiem_metrics_ecr_repo_url,
      environment : [
        { name : "SERIAL_NUMBER", value : var.serial_number },
        { name : "DYNAMODB_ACTIVATION_TABLE", value : local.dynamodb_activation_table },
        { name : "DYNAMODB_METRICS_STORAGE_TABLE", value : local.dynamodb_metrics_storage_table },
        { name : "DYNAMODB_REGION", value : local.portal_region },
        { name : "S3_BUCKET", value : local.clickhouse_data_bucket },
        { name : "S3_DIR", value : local.clickhouse_archive_dir_name },
        { name : "REGION", value : var.region }
      ],
      logConfiguration : {
        logDriver : "awslogs",
        options : {
          "awslogs-group" : local.fsiem_metrics,
          "awslogs-region" : var.region,
          "awslogs-stream-prefix" : "ecs"
        }
      }
    }
  ])
}

# Cloudwatch logs
resource "aws_cloudwatch_log_group" "fsiem_metrics" {
  name              = local.fsiem_metrics
  retention_in_days = local.log_persistance_days_short
}

# Cloudwatch event to trigger the fsiem-metrics task
resource "aws_cloudwatch_event_rule" "fsiem_metrics" {
  name                = "${local.fsiem_metrics}_${var.environment}"
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "fsiem_metrics" {
  rule     = aws_cloudwatch_event_rule.fsiem_metrics.name
  arn      = module.ecs.cluster_arn
  role_arn = aws_iam_role.scheduled_task_cloudwatch.arn
  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.fsiem_metrics.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = module.vpc.private_subnets
      security_groups = [aws_security_group.fsiem_metrics.id]
    }
  }
}
