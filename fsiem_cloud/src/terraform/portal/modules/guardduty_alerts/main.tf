/*
  SNS topics,policies,subscriptions & Eventbridge rules to notify on GuardDuty findings above severity 4 (Medium & High)
*/

resource "aws_sns_topic" "gd_sns_topic" {
  name         = "fsiem-guardduty-${var.gdsns_env}"
  display_name = "fsiem-guardduty-${var.gdsns_env}"
}

resource "aws_sns_topic_policy" "gd_sns_topic_policy" {
  arn    = aws_sns_topic.gd_sns_topic.arn
  policy = data.aws_iam_policy_document.gd_sns_policy.json
}

/*
This sns access policy id should not be modified
All parameters should be exactly as below for sns topic and event rule to work fine
*/

data "aws_iam_policy_document" "gd_sns_policy" {
  policy_id = "gd_sns_policy_ID_${var.gdsns_env}"

  statement {
    actions = [
      "SNS:Subscribe",
      "SNS:SetTopicAttributes",
      "SNS:RemovePermission",
      "SNS:Receive",
      "SNS:Publish",
      "SNS:ListSubscriptionsByTopic",
      "SNS:GetTopicAttributes",
      "SNS:DeleteTopic",
      "SNS:AddPermission",
    ]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceOwner"

      values = [
        "${data.aws_caller_identity.current.account_id}",
      ]
    }

    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    resources = [
      "${aws_sns_topic.gd_sns_topic.arn}",
    ]

    sid = "gd_sns_sid_${var.gdsns_env}"
  }
  statement {
    effect  = "Allow"
    actions = ["SNS:Publish"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    resources = [aws_sns_topic.gd_sns_topic.arn]

  }
}

resource "aws_sns_topic_subscription" "gd_sns_topic_sub" {
  topic_arn = aws_sns_topic.gd_sns_topic.arn
  protocol  = "email"
  endpoint  = var.notify_email
}

resource "aws_cloudwatch_event_rule" "gd_eventbridge_rule" {
  name        = "fsiem-guardduty-eb-rule-${var.gdsns_env}"
  description = "guardduty-rule-${var.gdsns_env}"

  event_pattern = <<EOF
{
  "source": ["aws.guardduty"],
  "detail-type": ["GuardDuty Finding"],
  "detail": {
    "severity": [4,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5,5.0,5.1,5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,
      6,6.0,6.1,6.2,6.3,6.4,6.5,6.6,6.7,6.8,6.9,
      7, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9]
  }
}
EOF
}

resource "aws_cloudwatch_event_target" "gd_eventbridge_rule_target" {
  rule      = aws_cloudwatch_event_rule.gd_eventbridge_rule.name
  target_id = "fsiem-guardduty-${var.gdsns_env}"
  arn       = aws_sns_topic.gd_sns_topic.arn

  input_transformer {
    input_paths = {
      "Account_ID" : "$.detail.accountId",
      "Finding_ID" : "$.detail.id",
      "Finding_Type" : "$.detail.type",
      "Finding_description" : "$.detail.description",
      "region" : "$.region",
      "severity" : "$.detail.severity"
    }

    input_template = "\"AWS <Account_ID> has a severity <severity> GuardDuty finding type <Finding_Type> in the <region> region.Finding Description: <Finding_description>.For more details open the GuardDuty console at https://console.aws.amazon.com/guardduty/home?region=<region>#/findings?search=id=<Finding_ID>\""

  }
}

data "aws_caller_identity" "current" {}
