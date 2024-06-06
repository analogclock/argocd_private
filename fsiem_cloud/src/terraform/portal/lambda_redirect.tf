/*
  Creates the lambda function for the UI POST redirect along with its logging,
  iam permissions, and security group.
*/
locals {
  redirect_js  = "${path.module}/index.js"
  redirect_zip = "${path.module}/redirect.zip"
}

data "aws_iam_policy_document" "lambda_redirect_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
        "edgelambda.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "iam_for_lambda_redirect" {
  name               = "lambda-redirect-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_redirect_assume_role_policy.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.url_redirect.function_name}"
  retention_in_days = local.log_persistance_days_medium
}

data "archive_file" "redirect_lambda_package" {
  type        = "zip"
  source_file = local.redirect_js
  output_path = local.redirect_zip
}

resource "aws_lambda_function" "url_redirect" {
  function_name = "url_redirect_${var.environment}"
  filename      = local.redirect_zip
  role          = aws_iam_role.iam_for_lambda_redirect.arn
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  memory_size   = 128
  timeout       = 3
}
