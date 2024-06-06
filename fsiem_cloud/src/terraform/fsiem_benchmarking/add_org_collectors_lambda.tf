data "archive_file" "python_lambda_package" {
  type        = "zip"
  source_dir  = "python/fsiem_collector_config"
  output_path = "python/fsiem_collector_config/artifacts/ssm_collectors_lambda.zip"
}

resource "aws_lambda_layer_version" "collector_custom_layer" {
  filename            = "python/lambda_layers/python_modules.zip"
  layer_name          = "collectors_customLayer_${var.environment}"
  source_code_hash    = filebase64sha256("python/lambda_layers/python_modules.zip")
  compatible_runtimes = ["python3.11"]
}

resource "aws_lambda_function" "python_lambda_function" {
  function_name    = "lambda_ssm_collectors_auto_${var.environment}"
  filename         = "python/fsiem_collector_config/artifacts/ssm_collectors_lambda.zip"
  source_code_hash = data.archive_file.python_lambda_package.output_base64sha256
  role             = aws_iam_role.fsiem_bm_lambda_ssm_role.arn
  runtime          = "python3.11"
  handler          = "main.lambda_handler"
  layers           = [aws_lambda_layer_version.collector_custom_layer.arn]
  timeout          = 300
}

resource "aws_cloudwatch_log_group" "python_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.python_lambda_function.function_name}"
  retention_in_days = var.log_persistance_days_short
}
