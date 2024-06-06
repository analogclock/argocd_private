/*
 Create log group for Cloudwatch
 Name of the required log group and days to retain the logs is passed as
 a variable from root module
*/

resource "aws_cloudwatch_log_group" "cw_log_group" {
  name              = var.name
  retention_in_days = var.retention_in_days
}

/*
 Create resource policy for cloudwatch logs.
 If the resource policy is not explicitly created ,
 then AWS will internally create a default resource policy
 named 'AWSLogDeliveryWrite20150319' in all regions supported.
*/
data "aws_iam_policy_document" "cloudwatch-log-publishing-policy" {
  statement {
    sid = "AWSLogDeliveryWrite"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*"]
    principals {
      identifiers = ["delivery.logs.amazonaws.com"]
      type        = "Service"
    }
  }
}
/*
CloudWatch logs resource policy doesn't actually get attached to a resource
and appears to be a service-level access policy for cloudWatch logs.
The only reference to it is the API call or CLI command.
*/
resource "aws_cloudwatch_log_resource_policy" "cloudwatch-log-log-publishing-policy" {
  policy_document = data.aws_iam_policy_document.cloudwatch-log-publishing-policy.json
  policy_name     = "cloudwatch-log-publishing-policy"
}
