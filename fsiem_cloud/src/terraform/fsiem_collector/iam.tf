/*
  This is the IAM role and profile for the all of the ec2 instances. Currently just basic permissions to run.
*/
data "aws_iam_policy_document" "instance_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}


data "aws_iam_policy_document" "instance_get_s3_scripts_policy" {
  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      local.s3_scripts_bucket_arn,
      "${local.s3_scripts_bucket_arn}/*"
    ]
  }
}

resource "aws_iam_role_policy" "instance_get_s3_scripts_policy" {
  role   = aws_iam_role.instance_role.id
  policy = data.aws_iam_policy_document.instance_get_s3_scripts_policy.json
}

data "aws_iam_policy_document" "ssm_session_manager_policy" {
  statement {
    actions = [
      "ssmmessages:CreateControlChannel",
      "ssmmessages:CreateDataChannel",
      "ssmmessages:OpenControlChannel",
      "ssmmessages:OpenDataChannel",
      "ssm:UpdateInstanceInformation",
      "s3:GetEncryptionConfiguration",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams"
    ]
    resources = [
      "*"
    ]
  }
  statement {
    actions = [
      "s3:PutObject"
    ]
    resources = [
      "${local.session_manager_bucket_arn}/*"
    ]
  }
}

resource "aws_iam_role_policy" "ssm_session_manager_policy" {
  role   = aws_iam_role.instance_role.id
  policy = data.aws_iam_policy_document.ssm_session_manager_policy.json
}

data "aws_iam_policy" "ssm_policy" {
  arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "ssm_policy" {
  policy = data.aws_iam_policy.ssm_policy.policy
  role   = aws_iam_role.instance_role.name
}

resource "aws_iam_role" "instance_role" {
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.instance_assume_role_policy.json
}

resource "aws_iam_instance_profile" "instance_profile" {
  role = aws_iam_role.instance_role.name
}
