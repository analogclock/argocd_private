/*
  SNS Topics,Policy to notify on AWS Backup failures
*/

resource "aws_sns_topic" "bkupfail_sns_topic" {
  name         = "fsiem-bkupfail-${var.bkupsns_env}"
  display_name = "fsiem-bkupfail-${var.bkupsns_env}"
}

resource "aws_sns_topic_policy" "bkupfail_sns_topic_policy" {
  arn    = aws_sns_topic.bkupfail_sns_topic.arn
  policy = data.aws_iam_policy_document.bkupfail_sns_policy.json
}

/*
This sns access policy id should not be modified
All parameters should be exactly as below for sns topic and event rule to work fine
*/

data "aws_iam_policy_document" "bkupfail_sns_policy" {
  policy_id = "bkupfail_sns_policy_ID_${var.bkupsns_env}"

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
      "${aws_sns_topic.bkupfail_sns_topic.arn}",
    ]

    sid = "bkupfail_sns_statement_ID_${var.bkupsns_env}"
  }
  statement {
    effect  = "Allow"
    actions = ["SNS:Publish"]

    principals {
      type        = "Service"
      identifiers = ["backup.amazonaws.com"]
    }

    resources = [aws_sns_topic.bkupfail_sns_topic.arn]

  }
}

resource "aws_sns_topic_subscription" "bkupfail_sns_topic_sub" {
  topic_arn = aws_sns_topic.bkupfail_sns_topic.arn
  protocol  = "email"
  endpoint  = var.notify_email

  filter_policy = <<EOF
  {
  "State": [
    {
      "anything-but": "COMPLETED"
    }
  ]
  }
   EOF
}
resource "aws_backup_vault_notifications" "bkupfail_vault_notify" {
  backup_vault_name   = "${var.bkupsns_env}-vault"
  sns_topic_arn       = aws_sns_topic.bkupfail_sns_topic.arn
  backup_vault_events = ["BACKUP_JOB_COMPLETED"]
}

data "aws_caller_identity" "current" {}
