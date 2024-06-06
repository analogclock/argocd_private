/*
  Fortimonitor
*/
locals {
  fsiem_monitor_name = "fsiem_monitor_${var.serial_number}"
  # plugin_url         = "https://${local.s3_scripts_bucket}.s3.amazonaws.com/fsiem_api.py"
  plugin_url = "https://s3.amazonaws.com/${local.s3_scripts_bucket}/fsiem_api.py"
}

resource "aws_ecs_service" "fsiem_monitor" {
  name                               = local.fsiem_monitor_name
  cluster                            = module.ecs.cluster_id
  task_definition                    = aws_ecs_task_definition.fsiem_monitor.arn
  deployment_maximum_percent         = 100
  deployment_minimum_healthy_percent = 0
  desired_count                      = 1
  launch_type                        = "FARGATE"
  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.fsiem_monitor.id]
  }
}

resource "aws_ecs_task_definition" "fsiem_monitor" {
  family                   = local.fsiem_monitor_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.fsiem_monitor_role.arn
  container_definitions = jsonencode([
    {
      name : local.fsiem_monitor_name,
      image : local.fsiem_monitor_ecr_repo_url,
      secrets : [
        { name : "SECRET_VM_AUTH", valueFrom : data.aws_secretsmanager_secret.fsiem_vm_auth_credentials.arn }
      ],
      environment : [
        { name : "CUSTOMER_KEY", value : jsondecode(data.aws_secretsmanager_secret_version.fortimonitor.secret_string)["customer_key"] },
        { name : "TAGS", value : "${var.serial_number},fsiemcontainer" },
        { name : "PLUGIN_URL", value : local.plugin_url },
        { name : "ENVIRONMENT", value : var.environment },
        { name : "SERIAL_NUMBER", value : var.serial_number },
        { name : "SUPER_URL", value : "https://${aws_instance.super.private_ip}" },
        { name : "DYNAMODB_ACTIVATION_TABLE", value : local.dynamodb_activation_table },
        { name : "DYNAMODB_REGION", value : local.portal_region },
        { name : "COGNITO_URL", value : local.cognito_url },
        { name : "REGION", value : var.region }
      ],
      logConfiguration : {
        logDriver : "awslogs",
        options : {
          "awslogs-group" : "${local.fsiem_monitor_name}",
          "awslogs-region" : "${var.region}",
          "awslogs-stream-prefix" : "ecs"
        }
      }
    }
  ])
}

# Cloudwatch log group
resource "aws_cloudwatch_log_group" "fsiem_monitor" {
  name              = local.fsiem_monitor_name
  retention_in_days = local.log_persistance_days_short
}
