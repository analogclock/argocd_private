/*
  Scheduled Upgrade container
*/
resource "aws_ecs_task_definition" "fsiem_scheduled_upgrade" {
  family                   = local.fsiem_scheduled_upgrade
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_exec_role.arn
  task_role_arn            = aws_iam_role.fsiem_scheduled_upgrade_role.arn
  container_definitions = jsonencode(
    [
      {
        name : local.fsiem_scheduled_upgrade,
        image : aws_ecr_repository.fsiem_scheduled_upgrade.repository_url,
        environment : [
          { name : "DYNAMODB_ACTIVATION_TABLE", value : local.dynamodb_activation_table },
          { name : "DYNAMODB_SCHEDULED_UPGRADES_TABLE", value : local.dynamodb_scheduled_upgrades_table },
          { name : "DYNAMODB_UPGRADE_TABLE", value : local.dynamodb_upgrades_table },
          { name : "TABLES_REGION", value : var.region },
          { name : "AUTOMATION_ROLE", value : aws_iam_role.fsiem_upgrade_ssm_role.name },
          { name : "EVENT_BUS_NAME", value : "portal-bus-${var.environment}" }
        ],
        logConfiguration : {
          logDriver : "awslogs",
          options : {
            "awslogs-group" : local.fsiem_scheduled_upgrade,
            "awslogs-region" : var.region,
            "awslogs-stream-prefix" : "ecs"
          }
        }
      }
  ])
}

# Cloudwatch logs
resource "aws_cloudwatch_log_group" "fsiem_scheduled_upgrade" {
  name              = local.fsiem_scheduled_upgrade
  retention_in_days = local.log_persistance_days_short
}

# Cloudwatch event to trigger the fsiem-setup task
resource "aws_cloudwatch_event_rule" "fsiem_scheduled_upgrade" {
  name                = local.fsiem_scheduled_upgrade
  schedule_expression = "rate(15 minutes)"
}

resource "aws_cloudwatch_event_target" "fsiem_scheduled_upgrade" {
  rule     = aws_cloudwatch_event_rule.fsiem_scheduled_upgrade.name
  arn      = module.ecs.cluster_arn
  role_arn = aws_iam_role.events.arn
  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.fsiem_scheduled_upgrade.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = module.vpc.private_subnets
      security_groups = [aws_security_group.scheduled_upgrade.id]
    }
  }
}
