/*
  Creates the lambda function dotnetcore API along with its logging, iam
  permissions, and security group.
*/
resource "aws_lambda_function" "api" {
  function_name    = "gateway_api_${var.environment}"
  filename         = var.portal_api_build_zip
  source_code_hash = filebase64sha256(var.portal_api_build_zip)
  role             = aws_iam_role.iam_for_lambda_api.arn
  handler          = "not-applicable"
  runtime          = "provided"
  memory_size      = 1024
  timeout          = 900
  environment {
    variables = {
      ASPNETCORE_ENVIRONMENT        = var.aspnetcore_environment
      AWS__Region                   = var.region
      PortalListCache__BucketName   = aws_s3_bucket.api_bucket.id
      EventBus                      = module.eventbridge.eventbridge_bus_name
      LicensingCertificateKey       = local.licensing_certificate_key
      LicensingPassphraseKey        = local.licensing_passphrase_key
      FortinetOne__CertificateKey   = local.fortinet_one_certificate_key
      FortinetOne__PassphraseKey    = local.fortinet_one_passphrase_key
      Environment                   = var.environment
      FortiMonitor__TokenKey        = local.fortimonitor_api_key
      DynamoDbTable                 = aws_dynamodb_table.fsiem_activation_table.id
      ApproverDynamoDbTable         = aws_dynamodb_table.fsiem_poc_approval_table.id
      UpdateDynamoDbTable           = local.dynamodb_upgrades_table
      ScheduledUpgradeDynamoDbTable = local.dynamodb_scheduled_upgrades_table
      ExternalStorageDynamoDbTable  = aws_dynamodb_table.fsiem_external_storage_table.id
      MetricsStorageDynamoDbTable   = aws_dynamodb_table.fsiem_metrics_storage_table.id
    }
  }
  vpc_config {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.lambda.id]
  }
}

resource "aws_lambda_permission" "allow_api_gateway" {
  function_name = aws_lambda_function.api.function_name
  action        = "lambda:InvokeFunction"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.rest_api.execution_arn}/*/*/*"
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = local.log_persistance_days_short
}

data "aws_iam_policy_document" "lambda_api_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy_document" "lambda_api_aws_access_policy" {
  statement {
    actions = [
      "secretsmanager:GetResourcePolicy",
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecretVersionIds"
    ]
    resources = [
      "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:secret:${local.fortinet_one_certificate_key}-??????",
      "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:secret:${local.fortinet_one_passphrase_key}-??????",
      "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:secret:${local.licensing_certificate_key}-??????",
      "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:secret:${local.licensing_passphrase_key}-??????",
      "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:secret:${local.fortimonitor_api_key}-??????"
    ]
  }
  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject"
    ]
    resources = [
      "${aws_s3_bucket.api_bucket.arn}/*"
    ]
  }
  statement {
    actions = [
      "cloudformation:DescribeStacks"
    ]
    resources = [
      "*" # Unable to reduce permissions further
    ]
  }
  statement {
    actions = [
      "ec2:*"
    ]
    resources = [
      "*" # Unable to reduce permissions further
    ]
  }
  statement {
    actions = [
      "events:PutEvents"
    ]
    resources = [
      "arn:aws:events:*:${data.aws_caller_identity.current.account_id}:event-bus/${module.eventbridge.eventbridge_bus_name}"
    ]
  }
  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:Scan",
      "dynamodb:Query"
    ]
    resources = [
      aws_dynamodb_table.fsiem_activation_table.arn,
      aws_dynamodb_table.fsiem_poc_approval_table.arn,
      aws_dynamodb_table.fsiem_upgrades_table.arn,
      aws_dynamodb_table.fsiem_scheduled_upgrades_table.arn,
      aws_dynamodb_table.fsiem_external_storage_table.arn,
      aws_dynamodb_table.fsiem_metrics_storage_table.arn
    ]
  }
  # Separate policy specifically for Delete on storage_table
  statement {
    actions = [
      "dynamodb:DeleteItem"
    ]
    resources = [
      aws_dynamodb_table.fsiem_external_storage_table.arn
    ]
  }
  statement {
    actions = [
      "ssm:PutParameter",
      "ssm:DeleteParameter",
      "ssm:GetParameter"
    ]
    # Ignored as the wildcard is needed to create multiple parameter which we dont know the name of in advance
    #tfsec:ignore:aws-iam-no-policy-wildcards
    resources = [
      "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/*"
    ]
  }
  statement {
    actions = [
      "kms:*"
    ]
    resources = [
      aws_kms_key.key.arn
    ]
  }
  statement {
    actions = [
      "acm:DescribeCertificate",
      "acm:GetCertificate",
      "acm:ImportCertificate",
      "acm:DeleteCertificate",
      "acm:AddTagsToCertificate"
    ]
    resources = [
      "*"
    ]
  }

}

resource "aws_iam_role" "iam_for_lambda_api" {
  name               = "lambda-api-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_api_assume_role_policy.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
  ]
  inline_policy {
    name   = "aws_access_for_lambda"
    policy = data.aws_iam_policy_document.lambda_api_aws_access_policy.json
  }
}
