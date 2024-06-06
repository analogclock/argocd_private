/*
  Storage enforcer
*/

locals {
  fsiem_storage_enforcer_clickhouse = "fsiem_storage_enforcer_clickhouse_${var.serial_number}"
}

#
# Clickhouse
#
resource "aws_ecs_task_definition" "fsiem_storage_enforcer_clickhouse" {
  family                   = local.fsiem_storage_enforcer_clickhouse
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.fsiem_storage_enforcer_task_role.arn
  container_definitions = jsonencode([
    {
      name : local.fsiem_storage_enforcer_clickhouse,
      image : local.fsiem_storage_enforcer_ecr_repo_url,
      environment : [
        { name : "SN", value : var.serial_number },
        { name : "REGION", value : var.region },
        { name : "SIZE_LIMIT_GB", value : tostring(local.archive_size_limit_gb) },
        { name : "BUFFER_GB", value : "20" },
        { name : "DYNAMODB_REGION", value : local.portal_region },
        { name : "DYNAMODB_EXT_STORAGE_TABLE", value : local.dynamodb_ext_storage_table },
        { name : "DYNAMODB_EXT_STORAGE_STATUS_TABLE", value : local.dynamodb_ext_storage_status_table }
      ],
      logConfiguration : {
        logDriver : "awslogs",
        options : {
          "awslogs-group" : "${local.fsiem_storage_enforcer_clickhouse}",
          "awslogs-region" : "${var.region}",
          "awslogs-stream-prefix" : "ecs"
        }
      }
    }
  ])
}

# Cloudwatch log group
resource "aws_cloudwatch_log_group" "fsiem_storage_enforcer_clickhouse" {
  name              = local.fsiem_storage_enforcer_clickhouse
  retention_in_days = local.log_persistance_days_short
}

# Cloudwatch event to trigger the fsiem-storage-enforcer task
resource "aws_cloudwatch_event_rule" "fsiem_storage_enforcer_clickhouse" {
  name                = "${local.fsiem_storage_enforcer_clickhouse}_${var.environment}"
  schedule_expression = "rate(1 day)"
}

# Cloudwatch trigger, run a task when event is received
resource "aws_cloudwatch_event_target" "fsiem_storage_enforcer_clickhouse" {
  rule     = aws_cloudwatch_event_rule.fsiem_storage_enforcer_clickhouse.name
  arn      = module.ecs.cluster_id
  role_arn = aws_iam_role.scheduled_task_cloudwatch.arn
  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.fsiem_storage_enforcer_clickhouse.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = module.vpc.private_subnets
      security_groups = [aws_security_group.fsiem_storage_enforcer.id]
    }
  }
}
