/*
  Lambda function to remove fsiem monitor container from fortimonitor
*/
resource "aws_lambda_function" "monitor_cleanup" {
  function_name    = "monitor_cleanup_${var.environment}"
  filename         = var.monitor_cleanup_zip
  source_code_hash = filebase64sha256(var.monitor_cleanup_zip)
  role             = aws_iam_role.lambda_monitor_cleanup_role.arn
  handler          = "main.main"
  runtime          = local.runtime_python_lambda
  layers           = [aws_lambda_layer_version.layer_fsiem_api_client.arn]
  memory_size      = 1024
  timeout          = 900
  environment {
    variables = {
      SECRET_ARN    = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
      SECRET_REGION = var.region
      ENVIRONMENT   = var.environment
    }
  }
}

resource "aws_lambda_event_source_mapping" "monitor_cleanup_activation" {
  event_source_arn  = aws_dynamodb_table.fsiem_activation_table.stream_arn
  function_name     = aws_lambda_function.monitor_cleanup.arn
  starting_position = "TRIM_HORIZON"
  batch_size        = 1
}

data "aws_iam_policy_document" "lambda_monitor_cleanup_assume_role_policy" {
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

data "aws_iam_policy_document" "lambda_monitor_cleanup_policy" {
  statement {
    actions = [
      "dynamodb:DescribeStream",
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:ListStreams"
    ]
    resources = [
      "${aws_dynamodb_table.fsiem_activation_table.arn}/stream/*"
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
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      aws_secretsmanager_secret.fortimonitor_api_key_write.arn
    ]
  }
  statement {
    actions = [
      "kms:Decrypt"
    ]
    resources = [
      aws_kms_key.key.arn
    ]
  }
}

resource "aws_iam_role" "lambda_monitor_cleanup_role" {
  name               = "lambda-monitor-cleanup-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_monitor_cleanup_assume_role_policy.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}

resource "aws_iam_role_policy" "lambda_monitor_cleanup_policy" {
  role   = aws_iam_role.lambda_monitor_cleanup_role.id
  policy = data.aws_iam_policy_document.lambda_monitor_cleanup_policy.json
}

resource "aws_cloudwatch_log_group" "monitor_cleanup" {
  name              = "/aws/lambda/${aws_lambda_function.monitor_cleanup.function_name}"
  retention_in_days = local.log_persistance_days_short
}
