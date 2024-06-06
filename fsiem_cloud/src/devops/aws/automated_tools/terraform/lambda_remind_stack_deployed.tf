resource "aws_lambda_function" "remind_stack_deployed" {
  function_name    = "remind_stack_deployed"
  filename         = "../lambda/artifacts/remind_stack_deployed.zip"
  source_code_hash = filebase64sha256("../lambda/artifacts/remind_stack_deployed.zip")
  role             = aws_iam_role.lambda_role.arn
  runtime          = var.lambda_runtime
  handler          = "main.lambda_handler"
  timeout          = 60
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.remind_stack_deployed.function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name                = "lambda_schedule_rule"
  description         = "Schedule rule to trigger Lambda function every Friday at 8 am"
  schedule_expression = "cron(0 8 ? * FRI *)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule = aws_cloudwatch_event_rule.lambda_schedule.name
  arn  = aws_lambda_function.remind_stack_deployed.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.remind_stack_deployed.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}
