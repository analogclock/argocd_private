/*
  Lambda function to handle rejected emails from SES
*/
resource "aws_lambda_function" "ses_reject" {
  function_name    = "ses_reject_${var.environment}"
  filename         = var.ses_reject_zip
  source_code_hash = filebase64sha256(var.ses_reject_zip)
  role             = aws_iam_role.lambda_ses_reject_role.arn
  handler          = "main.main"
  runtime          = local.runtime_python_lambda
  memory_size      = 1024
  timeout          = 900
  environment {
    variables = {
      DYNAMODB_EMAIL_BLOCK_TABLE = aws_dynamodb_table.fsiem_email_block_table.id
      TABLE_REGION               = var.region
    }
  }
}

resource "aws_sns_topic_subscription" "bounce" {
  topic_arn = aws_sns_topic.bounce.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.ses_reject.arn
}

resource "aws_lambda_permission" "bounce" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ses_reject.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.bounce.arn
}

resource "aws_sns_topic_subscription" "complaint" {
  topic_arn = aws_sns_topic.complaint.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.ses_reject.arn
}

resource "aws_lambda_permission" "complaint" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ses_reject.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.complaint.arn
}

data "aws_iam_policy_document" "lambda_ses_reject_assume_role_policy" {
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

data "aws_iam_policy_document" "lambda_ses_reject_policy" {
  statement {
    actions = [
      "dynamodb:PutItem"
    ]
    resources = [
      aws_dynamodb_table.fsiem_email_block_table.arn
    ]
  }
}

resource "aws_iam_role_policy" "lambda_ses_reject_policy" {
  role   = aws_iam_role.lambda_ses_reject_role.id
  policy = data.aws_iam_policy_document.lambda_ses_reject_policy.json
}

resource "aws_iam_role" "lambda_ses_reject_role" {
  name               = "lambda-ses-reject-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_ses_reject_assume_role_policy.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}

resource "aws_cloudwatch_log_group" "ses_reject" {
  name              = "/aws/lambda/${aws_lambda_function.ses_reject.function_name}"
  retention_in_days = local.log_persistance_days_short
}
