resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}
resource "aws_iam_policy_attachment" "lambda_execution" {
  name       = "aws_devops_lambda_execution"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
data "aws_iam_policy_document" "devops" {
  statement {
    actions = [
      "dynamodb:Scan",
    ]
    resources = [
      "arn:aws:dynamodb:us-east-1:${local.account_id}:table/fsiem_activation_table_dev",
      "arn:aws:dynamodb:us-east-1:${local.account_id}:table/fsiem_activation_table_playground"
    ]
  }
  statement {
    actions   = ["ses:SendEmail"]
    resources = ["arn:aws:ses:us-east-1:${local.account_id}:identity/*"]
  }
  statement {
    actions = [
      "secretsmanager:GetResourcePolicy",
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecretVersionIds"
    ]
    resources = [
      "arn:aws:secretsmanager:us-east-1:${local.account_id}:secret:devops/giphy-api-key-??????",
    ]
  }
}
resource "aws_iam_policy" "devops" {
  name   = "devops"
  policy = data.aws_iam_policy_document.devops.json
}

resource "aws_iam_policy_attachment" "lambda_dynamodb_access" {
  name       = "lambda_dynamodb_access"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = aws_iam_policy.devops.arn
}
