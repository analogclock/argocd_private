data "archive_file" "python_lambda_package" {
  type        = var.type_lambda
  source_dir  = var.source_dir_lambda
  output_path = var.output_path_lambda
}

resource "aws_lambda_function" "python_lambda_function" {
  function_name    = var.function_name_lambda
  filename         = var.filename_lambda
  source_code_hash = data.archive_file.python_lambda_package.output_base64sha256
  role             = var.role_lambda
  runtime          = var.runtime_lambda
  handler          = var.handler_lambda
  layers           = var.lambdalayers_arn
  memory_size      = 1024
  timeout          = 900
  environment {
    variables = {
      SECRET_ARN    = var.secret_arn
      SECRET_REGION = var.secret_region
    }
  }
}

resource "aws_cloudwatch_log_group" "python_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.python_lambda_function.function_name}"
  retention_in_days = var.retention_in_days
}
