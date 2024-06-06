/*
  Add SES domain to allow sending emails
  https://dev.to/mxro/sending-emails-with-ses-terraform-and-typescript-5ca
*/

data "aws_route53_zone" "fortisiem_cloud" {
  name         = var.hosted_zone_name[var.environment]
  private_zone = false
}

resource "aws_ses_domain_identity" "fortisiem_cloud" {
  domain = var.hosted_zone_name[var.environment]
}

resource "aws_ses_domain_mail_from" "fortisiem_cloud" {
  domain           = aws_ses_domain_identity.fortisiem_cloud.domain
  mail_from_domain = "mail.${var.hosted_zone_name[var.environment]}"
}

resource "aws_route53_record" "amazonses_verification_record" {
  zone_id = data.aws_route53_zone.fortisiem_cloud.zone_id
  name    = "_amazonses.${var.hosted_zone_name[var.environment]}"
  type    = "TXT"
  ttl     = "600"
  records = [join("", aws_ses_domain_identity.fortisiem_cloud.*.verification_token)]
}

resource "aws_ses_domain_dkim" "ses_domain_dkim" {
  domain = join("", aws_ses_domain_identity.fortisiem_cloud.*.domain)
}

resource "aws_route53_record" "amazonses_dkim_record" {
  count   = 3
  zone_id = data.aws_route53_zone.fortisiem_cloud.zone_id
  name    = "${element(aws_ses_domain_dkim.ses_domain_dkim.dkim_tokens, count.index)}._domainkey.${var.hosted_zone_name[var.environment]}"
  type    = "CNAME"
  ttl     = "600"
  records = ["${element(aws_ses_domain_dkim.ses_domain_dkim.dkim_tokens, count.index)}.dkim.amazonses.com"]
}

resource "aws_route53_record" "spf_mail_from" {
  zone_id = data.aws_route53_zone.fortisiem_cloud.zone_id
  name    = aws_ses_domain_mail_from.fortisiem_cloud.mail_from_domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}

resource "aws_route53_record" "mx_record" {
  zone_id = data.aws_route53_zone.fortisiem_cloud.zone_id
  name    = aws_ses_domain_mail_from.fortisiem_cloud.mail_from_domain
  type    = "MX"
  ttl     = "600"
  records = ["10 feedback-smtp.us-east-1.amazonses.com"]
}

resource "aws_route53_record" "spf_domain" {
  zone_id = data.aws_route53_zone.fortisiem_cloud.zone_id
  name    = var.hosted_zone_name[var.environment]
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}

# SNS Topics for Bounces and Complaints
resource "aws_sns_topic" "bounce" {
  name = "ses-bounce-${var.environment}"
}

resource "aws_sns_topic" "complaint" {
  name = "ses-complaint-${var.environment}"
}

resource "aws_ses_identity_notification_topic" "bounce" {
  topic_arn                = aws_sns_topic.bounce.arn
  notification_type        = "Bounce"
  identity                 = aws_ses_domain_identity.fortisiem_cloud.domain
  include_original_headers = true # This should possibly be false
}

resource "aws_ses_identity_notification_topic" "complaint" {
  topic_arn                = aws_sns_topic.complaint.arn
  notification_type        = "Complaint"
  identity                 = aws_ses_domain_identity.fortisiem_cloud.domain
  include_original_headers = true # This should possibly be false
}
