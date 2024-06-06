/*
Terraform guardduty module output
*/
output "sns_arn" {
  value       = aws_sns_topic.gd_sns_topic.arn
  description = "The ARN of the SNS topic."
}
