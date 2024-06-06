/*
  Fargate container that checks activation table for deployments that are close to expiry
  and sends out notification emails via SES
*/
locals {
  fsiem_expiry_notification = "fsiem-expiry-notification-${var.environment}"
}

resource "aws_ecs_task_definition" "fsiem_expiry_notification" {
  family                   = local.fsiem_expiry_notification
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_exec_role.arn
  task_role_arn            = aws_iam_role.fsiem_expiry_notification.arn
  container_definitions    = <<EOF
[
  {
    "name": "${local.fsiem_expiry_notification}",
    "image": "${aws_ecr_repository.fsiem_expiry_notification.repository_url}",
    "environment": [
      {
        "name": "DYNAMODB_ACTIVATION_TABLE",
        "value": "${aws_dynamodb_table.fsiem_activation_table.id}"
      },
      {
        "name": "EMAIL_BLOCK_TABLE",
        "value": "${aws_dynamodb_table.fsiem_email_block_table.id}"
      },
      {
        "name": "DYNAMODB_REGION",
        "value": "${var.region}"
      },
      {
        "name": "FROM_ADDRESS",
        "value": "${local.email_from_addr}"
      },
      {
        "name": "FSIEM_BCC_ADDRESS",
        "value": "${local.notification_email}"
      },
      {
        "name": "PORTAL_DOMAIN",
        "value": "${var.domain_name}"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${local.fsiem_expiry_notification}",
        "awslogs-region": "${var.region}",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }
]
EOF
}

# Cloudwatch logs
resource "aws_cloudwatch_log_group" "fsiem_expiry_notification" {
  name              = local.fsiem_expiry_notification
  retention_in_days = local.log_persistance_days_short
}

# Cloudwatch event to trigger the fsiem-storage-enforcer task
resource "aws_cloudwatch_event_rule" "fsiem_expiry_notification" {
  name                = local.fsiem_expiry_notification
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "fsiem_expiry_notification" {
  rule     = aws_cloudwatch_event_rule.fsiem_expiry_notification.name
  arn      = module.ecs.cluster_arn
  role_arn = aws_iam_role.events.arn
  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.fsiem_expiry_notification.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets = module.vpc.private_subnets
    }
  }
}
