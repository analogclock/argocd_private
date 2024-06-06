/*
  Create a simple Event Bridge (formerly Cloudwatch Events)
  Here we create one event bus, one pattern, and one target
  The event bus holds events as they are streamed into the system
  The pattern/rules match against said stream
  The target runs an action on match of the pattern
*/

locals {
  deployment_input_transformer = {
    input_paths = {
      deployment_name           = "$.detail.name"
      deployment_action         = "$.detail.action"
      deployment_region         = "$.detail.region"
      deployment_type           = "$.detail.deploymentType"
      deployment_email          = "$.detail.deploymentEmail"
      deployment_ipv4_cidr      = "$.detail.deploymentIPV4Cidr"
      deployment_ipv6_cidr      = "$.detail.deploymentIPV6Cidr"
      updating_deployment       = "$.detail.updatingDeployment"
      is_poc                    = "$.detail.isPOC"
      compute_size              = "$.detail.deploymentSKU.compute.quantity"
      live_storage              = "$.detail.deploymentSKU.onlineStorage.quantity"
      archive_storage           = "$.detail.deploymentSKU.archiveStorage.quantity"
      alternate_certificate_arn = "$.detail.alternateCertificateARN"
      primary_az                = "$.detail.primaryAZ"
      external_storage_dest     = "$.detail.externalStorageDest"
    }
    input_template = <<TEMPLATE
    {
      "containerOverrides": [
        {
          "name": "${local.ecs_name}",
          "environment": [
            { "name": "DEPLOYMENT_NAME", "value": <deployment_name> },
            { "name": "DEPLOYMENT_ACTION", "value": <deployment_action> },
            { "name": "DEPLOYMENT_TYPE", "value": <deployment_type> },
            { "name": "DEPLOYMENT_EMAIL", "value": <deployment_email> },
            { "name": "UPDATING_DEPLOYMENT", "value": <updating_deployment> },
            { "name": "IS_POC", "value": <is_poc> },
            { "name": "AWS_REGION", "value": <deployment_region> },
            { "name": "IPV4_CIDRS", "value": <deployment_ipv4_cidr> },
            { "name": "IPV6_CIDRS", "value": <deployment_ipv6_cidr> },
            { "name": "COMPUTE_SIZE", "value": <compute_size> },
            { "name": "LIVE_STORAGE", "value": <live_storage> },
            { "name": "ARCHIVE_STORAGE", "value": <archive_storage> },
            { "name": "ALTERNATE_DOMAIN_CERTIFICATE_ARN", "value": <alternate_certificate_arn> },
            { "name": "PRIMARY_AZ", "value": <primary_az> },
            { "name": "EXTERNAL_STORAGE_DEST", "value": <external_storage_dest> }
          ]
        }
      ]
    }
    TEMPLATE
  }
}

module "eventbridge" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "~> 2.3.0"

  bus_name = "portal-bus-${var.environment}"

  create_permissions = true
  create_bus         = true
  create_role        = true
  create_archives    = true

  rules = {
    upload = {
      description = "New deployment initiated"
      event_pattern = jsonencode(
        {
          "source" : ["fsiem.deploy.pipeline"]
          # "detail-type" : ["NewDeployment"]
      })
      enabled = true
    }
  }

  targets = {
    upload = [
      {
        name            = "process-email-with-ecs-task",
        arn             = module.ecs.cluster_arn,
        task_role_arn   = aws_iam_role.eventbridge_role.arn
        attach_role_arn = true
        ecs_target = {
          launch_type = "FARGATE"
          network_configuration = {
            subnets = module.vpc.private_subnets
          }
          task_count          = 1
          task_definition_arn = aws_ecs_task_definition.fsiem_deploy.arn
        }
        input_transformer = local.deployment_input_transformer
      }
    ]
  }

  archives = {
    "launch-archive-${var.environment}" = {
      description    = "Deploy launch archive for ${var.environment} environment",
      retention_days = 1
      event_pattern = jsonencode(
        {
          "source" : ["fsiem.deploy.pipeline"]
      })
    }
  }

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.eventbridge_policy_doc.json
}

