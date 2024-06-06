

# IAM role for fsiem ssm task
data "aws_iam_policy_document" "fsiem_bm_ssm_role_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "ec2.amazonaws.com",
        "ssm.amazonaws.com"
      ]
    }
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
}

resource "aws_iam_role" "fsiem_bm_ssm_role" {
  name        = "fsiem-bm-ssm-role-${var.environment}"
  description = "Role for fsiem bm ssm automation on ${var.environment}"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonSSMAutomationRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
  assume_role_policy = data.aws_iam_policy_document.fsiem_bm_ssm_role_assume_role_policy.json
}


# IAM policy to support steps to add collectors to fsiem super for benchmarking
data "aws_iam_policy_document" "fsiem_bm_ssm_policy" {
  statement {
    actions = [
      "ec2:DescribeInstances",
      "ec2:StopInstances",
      "ec2:StartInstances",
      "ec2:DescribeInstanceStatus",
    ]
    resources = ["*"]
  }
  statement {
    actions = [
      "ssm:StartAutomationExecution",
      "ssm:DescribeAutomationExecutions",
      "ssm:DescribeInstanceInformation",
      "ssm:SendCommand",
      "ssm:ListCommands",
      "ssm:ListCommandInvocations"
    ]
    resources = ["*"]
  }

  statement {
    actions   = ["sts:AssumeRole"]
    resources = [aws_iam_role.fsiem_bm_ssm_role.arn]
  }
  statement {
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.fsiem_bm_ssm_role.arn]
  }
}

resource "aws_iam_role_policy" "fsiem_bm_ssm_role_policy" {
  role   = aws_iam_role.fsiem_bm_ssm_role.id
  policy = data.aws_iam_policy_document.fsiem_bm_ssm_policy.json
}

/* Iam role for ssm documents to execute the fsiem collector lambda functions
*/

data "aws_iam_policy_document" "fsiem_bm_lambda_ssm_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "fsiem_bm_lambda_ssm_policy" {

  statement {
    actions = [
      "elasticloadbalancing:*",
      "ec2:DescribeInstances",
      "ec2:StopInstances",
      "ec2:StartInstances",
      "ec2:DescribeInstanceStatus"
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "ssm:SendCommand",
      "ssm:GetCommandInvocation"
    ]
    resources = ["*"]
  }

}

resource "aws_iam_role" "fsiem_bm_lambda_ssm_role" {
  name               = "fsiem-bm-lambda-ssm-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.fsiem_bm_lambda_ssm_assume_role_policy.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}

resource "aws_iam_role_policy" "fsiem_bm_lambda_ssm_role_policy" {
  role   = aws_iam_role.fsiem_bm_lambda_ssm_role.id
  policy = data.aws_iam_policy_document.fsiem_bm_lambda_ssm_policy.json

}
