/*
  Ec2 autoscaling group for the ingestion workers
*/

locals {
  fsiem_worker_autoscaling_name = "fsiem_worker_autoscaling_${var.serial_number}_${var.environment}"
}

data "aws_ec2_instance_type_offering" "worker_ingestion" {
  filter {
    name   = "instance-type"
    values = var.ingestion_instance_types
  }
  filter {
    name   = "location"
    values = [data.aws_subnet.worker.availability_zone_id]
  }
  location_type            = "availability-zone-id"
  preferred_instance_types = var.ingestion_instance_types
}

# Autoscaling group
resource "aws_launch_template" "worker_ingestion" {
  name_prefix   = "fsiem_workers_group_${var.serial_number}_${var.environment}"
  image_id      = local.siem_ami
  instance_type = data.aws_ec2_instance_type_offering.worker_ingestion.id
  iam_instance_profile {
    arn = aws_iam_instance_profile.instance_profile.arn
  }

  block_device_mappings {
    device_name = "/dev/sda1"
    ebs {
      delete_on_termination = true
      encrypted             = true
      volume_size           = 25
      volume_type           = "gp3"
    }
  }

  # Opt disk
  block_device_mappings {
    device_name = "/dev/sdf"
    ebs {
      delete_on_termination = true
      encrypted             = true
      volume_size           = 100
      volume_type           = "gp3"
      iops                  = var.opt_iops
      throughput            = var.opt_throughput
    }
  }

  # Clickhouse volume - not used in ingestion workers but the fsiem API requires at
  # least one disk when adding a worker to the fsiem cluster
  block_device_mappings {
    device_name = "/dev/sdg"
    ebs {
      delete_on_termination = true
      encrypted             = true
      volume_size           = var.data_disk_size
      volume_type           = "gp3"
      iops                  = var.data_disk_iops
      throughput            = var.data_disk_throughput
    }
  }

  vpc_security_group_ids = [aws_security_group.worker.id]
}

resource "aws_autoscaling_group" "worker_ingestion" {
  name                 = "fsiem_workers_group_${var.serial_number}_${var.environment}"
  desired_capacity     = var.ingestion_workers
  max_size             = 10
  min_size             = 0
  suspended_processes  = ["HealthCheck"]
  termination_policies = ["OldestInstance"]
  vpc_zone_identifier  = [data.aws_subnet.worker.id]

  launch_template {
    id      = aws_launch_template.worker_ingestion.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.serial_number}_ingestion_worker"
    propagate_at_launch = true
  }
  tag {
    key                 = "Role"
    value               = "ingestion"
    propagate_at_launch = true
  }

  # Global tags are not added to autoscaling instances for some reason, this adds them
  dynamic "tag" {
    for_each = local.global_tags

    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
}

resource "aws_sqs_queue" "worker_lifecycle" {
  name = local.fsiem_worker_autoscaling_name
}

resource "aws_autoscaling_lifecycle_hook" "worker_termination" {
  name                    = "${var.serial_number}_${var.environment}_ingestion_termination"
  autoscaling_group_name  = aws_autoscaling_group.worker_ingestion.name
  default_result          = "ABANDON"
  heartbeat_timeout       = 3600
  lifecycle_transition    = "autoscaling:EC2_INSTANCE_TERMINATING"
  notification_target_arn = aws_sqs_queue.worker_lifecycle.arn
  role_arn                = aws_iam_role.autoscaling_role.arn
}

resource "aws_autoscaling_lifecycle_hook" "worker_launch" {
  name                    = "${var.serial_number}_${var.environment}_ingestion_launch"
  autoscaling_group_name  = aws_autoscaling_group.worker_ingestion.name
  default_result          = "ABANDON"
  heartbeat_timeout       = 3600
  lifecycle_transition    = "autoscaling:EC2_INSTANCE_LAUNCHING"
  notification_target_arn = aws_sqs_queue.worker_lifecycle.arn
  role_arn                = aws_iam_role.autoscaling_role.arn
}

data "aws_iam_policy_document" "autoscaling" {
  statement {
    actions = [
      "sqs:SendMessage",
      "sqs:GetQueueUrl",
      "sns:Publish"
    ]
    resources = [
      aws_sqs_queue.worker_lifecycle.arn
    ]
  }
}

data "aws_iam_policy_document" "autoscaling_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "autoscaling.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role_policy" "autoscaling_policy" {
  role   = aws_iam_role.autoscaling_role.id
  policy = data.aws_iam_policy_document.autoscaling.json
}

resource "aws_iam_role" "autoscaling_role" {
  name               = "autoscaling-role-${var.serial_number}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.autoscaling_assume_role_policy.json
}

resource "aws_cloudwatch_event_rule" "fsiem_worker_autoscaling" {
  name                = local.fsiem_worker_autoscaling_name
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "fsiem_worker_autoscaling" {
  rule     = aws_cloudwatch_event_rule.fsiem_worker_autoscaling.name
  arn      = module.ecs.cluster_arn
  role_arn = aws_iam_role.scheduled_task_cloudwatch.arn
  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.fsiem_worker_autoscaling.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = module.vpc.private_subnets
      security_groups = [aws_security_group.fsiem_worker_autoscaling.id]
    }
  }
}

# Definition for the fsiem clickhouse backup task
resource "aws_ecs_task_definition" "fsiem_worker_autoscaling" {
  family                   = local.fsiem_worker_autoscaling_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.fsiem_worker_autoscaling_role.arn
  container_definitions = jsonencode([
    {
      name : local.fsiem_worker_autoscaling_name,
      image : local.fsiem_worker_autoscaling_ecr_repo_url,
      secrets : [
        { name : "SECRET_VM_AUTH", valueFrom : data.aws_secretsmanager_secret.fsiem_vm_auth_credentials.arn }
      ],
      environment : [
        { name : "SQS_QUEUE_NAME", value : local.fsiem_worker_autoscaling_name },
        { name : "SUPER_ADDRESS", value : aws_instance.super.private_ip },
        { name : "COGNITO_URL", value : local.cognito_url },
        { name : "SERIAL_NO", value : var.serial_number },
        { name : "ENVIRONMENT", value : var.environment },
        { name : "CLUSTER_REGION", value : var.region },
        { name : "PORTAL_REGION", value : local.portal_region },
        { name : "S3_BUCKET", value : "${local.clickhouse_data_bucket}/${local.clickhouse_archive_dir_name}" },
        { name : "S3_REGION", value : var.region },
        { name : "DYNAMODB_ACTIVATION_TABLE", value : local.dynamodb_activation_table },
        { name : "SETUP_DOC_NAME", value : local.setup_doc_name },
        { name : "AUTOMATION_ROLE_NAME", value : local.upgrade_iam_role },
        { name : "FMON_CUST_KEY", value : jsondecode(data.aws_secretsmanager_secret_version.fortimonitor.secret_string)["customer_key"] }
      ],
      logConfiguration : {
        logDriver : "awslogs",
        options : {
          "awslogs-group" : local.fsiem_worker_autoscaling_name,
          "awslogs-region" : var.region,
          "awslogs-stream-prefix" : "ecs"
        }
      }
    }
  ])
}

# Cloudwatch logs
resource "aws_cloudwatch_log_group" "fsiem_worker_autoscaling" {
  name              = local.fsiem_worker_autoscaling_name
  retention_in_days = local.log_persistance_days_short
}

resource "aws_iam_role" "fsiem_worker_autoscaling_role" {
  name               = "fsiem-worker-autoscaling-${var.serial_number}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role_policy.json
}

resource "aws_iam_role_policy" "fsiem_worker_autoscaling_policy" {
  role   = aws_iam_role.fsiem_worker_autoscaling_role.id
  policy = data.aws_iam_policy_document.fsiem_worker_autoscaling_policy_doc.json
}

data "aws_iam_policy_document" "fsiem_worker_autoscaling_policy_doc" {
  # Read from SQS
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:GetQueueUrl",
      "sqs:DeleteMessage"
    ]
    resources = [aws_sqs_queue.worker_lifecycle.arn]
  }
  # Finish lifecycle hook
  statement {
    actions = [
      "autoscaling:CompleteLifecycleAction"
    ]
    resources = [
      aws_autoscaling_group.worker_ingestion.arn
    ]
  }
  # Get info like IP and DNS that api calls to fsiem require
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
      "ssm:StartAutomationExecution",
      "ssm:DescribeAutomationExecutions"
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "dynamodb:GetItem"
    ]
    resources = [
      local.dynamodb_activation_table_arn
    ]
  }
}
