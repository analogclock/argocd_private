data "aws_acm_certificate" "wildcard_environment" {
  domain      = "*.${var.cert_domain}"
  types       = ["AMAZON_ISSUED"]
  statuses    = ["ISSUED"]
  most_recent = true
  key_types   = ["RSA_2048"]
}

resource "aws_cloudwatch_metric_alarm" "cert_expiry_alarm" {
  alarm_name          = "cert_expiry_alarm_${var.gdsns_env}"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "DaysToExpiry"
  dimensions = {
    CertificateArn = data.aws_acm_certificate.wildcard_environment.arn
  }
  namespace         = "AWS/CertificateManager"
  period            = 86400
  statistic         = "Average"
  threshold         = 30
  alarm_description = "Alarms when ACM certs are close to expiry"
  alarm_actions     = [aws_sns_topic.gd_sns_topic.arn]
}
