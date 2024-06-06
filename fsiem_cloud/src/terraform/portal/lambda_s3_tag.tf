# Creates the lambda function for S3 objects tagging along with
# its logging, and IAM  permissions.

resource "aws_lambda_function" "fsiem_s3_tag" {
  function_name    = "fsiem_s3_tag_${var.environment}"
  filename         = var.s3_tag_zip
  source_code_hash = filebase64sha256(var.s3_tag_zip)
  role             = aws_iam_role.iam_for_lambda_fsiem_s3_tag.arn
  runtime          = local.runtime_python_lambda
  handler          = "main.main"
  layers           = [aws_lambda_layer_version.layer_fsiem_api_client.arn]
  memory_size      = 1024
  timeout          = 900 # 15 mins (which is max allowed) in seconds
}

resource "aws_cloudwatch_log_group" "fsiem_s3_tag" {
  name              = "/aws/lambda/${aws_lambda_function.fsiem_s3_tag.function_name}"
  retention_in_days = local.log_persistance_days_short
}

# Assume requires to call lambda and to create batch S3 job
data "aws_iam_policy_document" "lambda_fsiem_s3_tag_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
        "batchoperations.s3.amazonaws.com"
      ]
    }
  }
}

locals {
  s3_tagging_role_name = "lambda-fsiem-s3-tag-${var.environment}"
}

data "aws_iam_policy_document" "lambda_fsiem_s3_tag_policy" {
  # S3 batch job manifest bucket: allow S3 writes to create tagging manifests
  statement {
    actions = [
      "s3:PutObject",
      "s3:PutObjectTagging",
      "s3:PutObjectAcl",
      "s3:GetObject",
      "s3:GetObjectAttributes",
      "s3:AbortMultipartUpload",
      "s3:ListBucketMultipartUploads",
      "s3:ListMultipartUploadParts",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.fsiem_s3_job.arn,
      "${aws_s3_bucket.fsiem_s3_job.arn}/*",
    ]
  }
  # Needed to run s3 batch tagging job
  statement {
    actions   = ["iam:PassRole"]
    resources = ["arn:aws:iam::${local.account_id}:role/${local.s3_tagging_role_name}"]
  }
  # There doesn't seem to be a way to limit this to a particular resource :/
  statement {
    actions = [
      "s3:CreateJob",
      "s3:UpdateJobStatus",
      "s3:DescribeJob",
    ]
    # This needs to be a *, even arn:aws:s3:::* doesn't work
    resources = ["*"]
  }
  # Read access and put_tags access to all the clickhouse buckets and objects
  # We need "read" to get all the keys
  # Which will then be tagged by a batch job
  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
      "s3:PutObjectTagging",
    ]
    resources = [
      # Archive buckets and objects
      "arn:aws:s3:::${local.clickhouse_archive_data_prefix}-*-${var.environment}",
      "arn:aws:s3:::${local.clickhouse_archive_data_prefix}-*-${var.environment}/*",

      # Backup buckets and objects
      "arn:aws:s3:::${local.clickhouse_backup_prefix}-*-${var.environment}",
      "arn:aws:s3:::${local.clickhouse_backup_prefix}-*-${var.environment}/*",
    ]
  }
}

resource "aws_iam_role" "iam_for_lambda_fsiem_s3_tag" {
  name               = local.s3_tagging_role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_fsiem_s3_tag_assume_role.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
  ]
  inline_policy {
    name   = "lambda_fsiem_s3_tag_policy"
    policy = data.aws_iam_policy_document.lambda_fsiem_s3_tag_policy.json
  }
}
