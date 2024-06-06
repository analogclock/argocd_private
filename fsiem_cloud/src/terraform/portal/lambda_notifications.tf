/*
  Lambda function to notify on failed deployments
*/
resource "aws_lambda_function" "notifications" {
  function_name    = "notifications_${var.environment}"
  filename         = var.notification_email_zip
  source_code_hash = filebase64sha256(var.notification_email_zip)
  role             = aws_iam_role.lambda_notifications_role.arn
  handler          = "main.main"
  runtime          = local.runtime_python_lambda
  layers           = [aws_lambda_layer_version.layer_fsiem_api_client.arn]
  memory_size      = 1024
  timeout          = 900
  environment {
    variables = {
      TOPIC                  = aws_sns_topic.notifications.arn
      ENVIRONMENT            = var.environment
      REGION                 = var.region
      FROM_ADDRESS           = local.email_from_addr
      FSIEM_BCC_ADDRESS      = local.notification_email
      ACTIVATION_ARN         = aws_dynamodb_table.fsiem_activation_table.arn
      POC_APPROVAL_ARN       = aws_dynamodb_table.fsiem_poc_approval_table.arn
      STORAGE_APPROVAL_ARN   = aws_dynamodb_table.fsiem_storage_approval_table.arn
      SCHEDULED_UPGRADE_ARN  = aws_dynamodb_table.fsiem_scheduled_upgrades_table.arn
      UPGRADES_TABLE_NAME    = local.dynamodb_upgrades_table
      ACTIVATION_TABLE_NAME  = local.dynamodb_activation_table
      EMAIL_BLOCK_TABLE_NAME = local.dynamodb_email_block_table
    }
  }
}

/*
  This can produce an error during apply: Error: Provider produced inconsistent final plan
  This is a know issue with the AWS provider: https://github.com/hashicorp/terraform-provider-aws/issues/10297
  It will cause a failure during the initial apply, however if you run apply again it will run without errors
*/
resource "aws_lambda_event_source_mapping" "activation" {
  event_source_arn  = aws_dynamodb_table.fsiem_activation_table.stream_arn
  function_name     = aws_lambda_function.notifications.arn
  starting_position = "TRIM_HORIZON"
  batch_size        = 1
}

resource "aws_lambda_event_source_mapping" "poc_approval" {
  event_source_arn  = aws_dynamodb_table.fsiem_poc_approval_table.stream_arn
  function_name     = aws_lambda_function.notifications.arn
  starting_position = "TRIM_HORIZON"
  batch_size        = 1
}

resource "aws_lambda_event_source_mapping" "storage_approval" {
  event_source_arn  = aws_dynamodb_table.fsiem_storage_approval_table.stream_arn
  function_name     = aws_lambda_function.notifications.arn
  starting_position = "TRIM_HORIZON"
  batch_size        = 1
}

resource "aws_lambda_event_source_mapping" "scheduled_upgrade" {
  event_source_arn  = aws_dynamodb_table.fsiem_scheduled_upgrades_table.stream_arn
  function_name     = aws_lambda_function.notifications.arn
  starting_position = "TRIM_HORIZON"
  batch_size        = 1
}

resource "aws_sns_topic" "notifications" {
  name = "notifications-${var.environment}"
}

resource "aws_sns_topic_subscription" "notifications" {
  topic_arn = aws_sns_topic.notifications.arn
  protocol  = "email"
  endpoint  = local.notification_email
}

resource "aws_sns_topic_subscription" "teams_notifications" {
  topic_arn = aws_sns_topic.notifications.arn
  protocol  = "email"
  endpoint  = local.teams_email
}

data "aws_iam_policy_document" "lambda_notifications_assume_role_policy" {
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

data "aws_iam_policy_document" "lambda_notifications_policy" {
  statement {
    actions = [
      "dynamodb:DescribeStream",
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:ListStreams"
    ]
    resources = [
      "${aws_dynamodb_table.fsiem_activation_table.arn}/stream/*",
      "${aws_dynamodb_table.fsiem_poc_approval_table.arn}/stream/*",
      "${aws_dynamodb_table.fsiem_storage_approval_table.arn}/stream/*",
      "${aws_dynamodb_table.fsiem_scheduled_upgrades_table.arn}/stream/*"
    ]
  }
  statement {
    actions = [
      "sns:Publish"
    ]
    resources = [
      aws_sns_topic.notifications.arn
    ]
  }
  statement {
    actions = [
      "dynamodb:GetItem"
    ]
    resources = [
      aws_dynamodb_table.fsiem_activation_table.arn,
      aws_dynamodb_table.fsiem_upgrades_table.arn,
      aws_dynamodb_table.fsiem_email_block_table.arn
    ]
  }
  statement {
    actions = [
      "ses:SendEmail"
    ]
    resources = [
      "arn:aws:ses:${var.region}:${data.aws_caller_identity.current.account_id}:identity/*"
    ]
  }
}

resource "aws_iam_role" "lambda_notifications_role" {
  name               = "lambda-notifications-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_notifications_assume_role_policy.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}

resource "aws_iam_role_policy" "lambda_notifications_policy" {
  role   = aws_iam_role.lambda_notifications_role.id
  policy = data.aws_iam_policy_document.lambda_notifications_policy.json
}

resource "aws_cloudwatch_log_group" "notifications" {
  name              = "/aws/lambda/${aws_lambda_function.notifications.function_name}"
  retention_in_days = local.log_persistance_days_short
}
