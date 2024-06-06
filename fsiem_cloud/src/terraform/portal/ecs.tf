/*
  This file creates a simple ECS cluster.
  Setting the runtime to FARGATE
*/

module "ecs" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "~> 5.2.0"

  cluster_name = "portal-cluster-${var.environment}"

  fargate_capacity_providers = {
    FARGATE      = {}
    FARGATE_SPOT = {}
  }
  cluster_settings = {
    "name" : "containerInsights",
    "value" : "disabled"
  }
}

locals {
  ecs_name                = "fsiem-deploy-${var.environment}"
  fsiem_terraform_updater = "fsiem-terraform-updater-${var.environment}"
  fsiem_scheduled_upgrade = "fsiem-scheduled-upgrade-${var.environment}"
  fsiem_daily_job         = "fsiem-daily-job-${var.environment}"
}

/*
  Create a simple service onto the ECS cluster.
  Using the private subnets from the VPC.
*/
resource "aws_ecs_service" "fsiem_deploy" {
  name            = local.ecs_name
  cluster         = module.ecs.cluster_id
  task_definition = aws_ecs_task_definition.fsiem_deploy.arn
  launch_type     = "FARGATE"
  network_configuration {
    subnets = module.vpc.private_subnets
  }
  desired_count = 0

  deployment_maximum_percent         = 100
  deployment_minimum_healthy_percent = 0
}

/*
  Create a simple task definition for the service
*/
resource "aws_ecs_task_definition" "fsiem_deploy" {
  family                   = local.ecs_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 2048
  memory                   = 4096
  execution_role_arn       = aws_iam_role.ecs_exec_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  container_definitions = jsonencode([
    {
      name : local.ecs_name,
      image : aws_ecr_repository.fsiem-deploy.repository_url,
      cpu : 1024,
      memory : 2048,
      environment : [
        { name : "TERRAGRUNT_IAM_ROLE", value : aws_iam_role.fsiem_deployment_role.arn },
        { name : "DEPLOYMENT_BUCKET", value : var.deployment_bucket },
        { name : "DEPLOYMENT_BUCKET_REGION", value : var.deployment_bucket_region },
        { name : "DYNAMODB_ACTIVATION_TABLE", value : local.dynamodb_activation_table },
        { name : "DYNAMODB_BACKUP_OPTIONS_TABLE", value : local.dynamodb_backup_options_table },
        { name : "DYNAMODB_BACKUP_TABLE", value : local.dynamodb_backup_table },
        { name : "DYNAMODB_RESTORE_TABLE", value : local.dynamodb_restore_table },
        { name : "DYNAMODB_COMPUTE_OVERRIDE_TABLE", value : local.dynamodb_compute_override_table },
        { name : "DYNAMODB_SCHEDULE_UPGRADES_TABLE", value : local.dynamodb_scheduled_upgrades_table },
        { name : "DYNAMODB_POC_APPROVAL_TABLE", value : local.dynamodb_poc_approval_table },
        { name : "DYNAMODB_STORAGE_APPROVAL_TABLE", value : local.dynamodb_storage_approval_table },
        { name : "DYNAMODB_EXT_STORAGE_TABLE", value : local.dynamodb_ext_storage_table },
        { name : "DYNAMODB_EXT_STORAGE_STATUS_TABLE", value : local.dynamodb_ext_storage_status_table },
        { name : "ENVIRONMENT", value : var.environment },
        { name : "WORKLOAD_CLASSIFICATION", value : var.workload_classification }
      ],
      logConfiguration : {
        logDriver : "awslogs",
        options : {
          "awslogs-group" : local.ecs_name,
          "awslogs-region" : "us-east-1",
          "awslogs-stream-prefix" : "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "fsiem_deploy" {
  name = local.ecs_name
}

/*
  Terraform Updater container
*/
resource "aws_ecs_task_definition" "fsiem_terraform_updater" {
  family                   = local.fsiem_terraform_updater
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_exec_role.arn
  task_role_arn            = aws_iam_role.fsiem_terraform_updater_role.arn
  container_definitions = jsonencode(
    [
      {
        name : local.fsiem_terraform_updater,
        image : aws_ecr_repository.fsiem_terraform_updater.repository_url,
        environment : [
          { name : "DYNAMODB_ACTIVATION_TABLE", value : local.dynamodb_activation_table },
          { name : "AWS_REGION", value : var.region },
          { name : "EVENT_BUS_NAME", value : "portal-bus-${var.environment}" }
        ],
        logConfiguration : {
          logDriver : "awslogs",
          options : {
            "awslogs-group" : local.fsiem_terraform_updater,
            "awslogs-region" : var.region,
            "awslogs-stream-prefix" : "ecs"
          }
        }
      }
  ])
}

# Cloudwatch logs
resource "aws_cloudwatch_log_group" "fsiem_terraform_updater" {
  name              = local.fsiem_terraform_updater
  retention_in_days = local.log_persistance_days_short
}

# Cloudwatch event to trigger the fsiem-setup task
resource "aws_cloudwatch_event_rule" "fsiem_terraform_updater" {
  name                = local.fsiem_terraform_updater
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "fsiem_terraform_updater" {
  rule     = aws_cloudwatch_event_rule.fsiem_terraform_updater.name
  arn      = module.ecs.cluster_arn
  role_arn = aws_iam_role.events.arn
  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.fsiem_terraform_updater.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = module.vpc.private_subnets
      security_groups = [aws_security_group.terraform_updater.id] #TODO
    }
  }
}

/*
  Scheduled daily job container
*/
resource "aws_ecs_task_definition" "fsiem_daily_job" {
  family                   = local.fsiem_daily_job
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_exec_role.arn
  task_role_arn            = aws_iam_role.daily_job.arn
  container_definitions = jsonencode(
    [
      {
        name : local.fsiem_daily_job,
        image : aws_ecr_repository.fsiem_daily_job.repository_url,
        environment : [
          { name : "AWS_ACCOUNT_ID", value : local.account_id },
          { name : "DYNAMODB_REGION", value : var.region },
          { name : "DYNAMODB_ACTIVATION_TABLE", value : local.dynamodb_activation_table },
          { name : "LAMBDA_REGION", value : var.region },
          { name : "S3_TAG_LAMBDA_NAME", value : local.lambda_s3_tag_name },
          { name : "S3_TAG_LAMBDA_ROLE_ARN", value : local.s3_tagging_role_arn },
          { name : "S3_MANIFEST_BUCKET", value : local.s3_job_bucket_name },
          { name : "ENVIRONMENT", value : var.environment },
          { name : "EMAIL_FROM_ADDR", value : local.email_from_addr },
          { name : "EMAIL_TO_ADDR", value : local.email_to_addr }
        ],
        logConfiguration : {
          logDriver : "awslogs",
          options : {
            "awslogs-group" : local.fsiem_daily_job,
            "awslogs-region" : var.region,
            "awslogs-stream-prefix" : "ecs"
          }
        }
      }
  ])
}

# Cloudwatch logs
resource "aws_cloudwatch_log_group" "fsiem_daily_job" {
  name              = local.fsiem_daily_job
  retention_in_days = local.log_persistance_days_short
}

# Cloudwatch event to trigger the fsiem-daily-job task
resource "aws_cloudwatch_event_rule" "fsiem_daily_job" {
  name                = local.fsiem_daily_job
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "fsiem_daily_job" {
  rule     = aws_cloudwatch_event_rule.fsiem_daily_job.name
  arn      = module.ecs.cluster_id
  role_arn = aws_iam_role.events.arn
  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.fsiem_daily_job.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = module.vpc.private_subnets
      security_groups = [aws_security_group.lambda.id]
    }
  }
}
