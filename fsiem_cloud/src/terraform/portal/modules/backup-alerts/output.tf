/*
Terraform backup alerts module output
*/
output "arn" {
  value       = aws_sns_topic.bkupfail_sns_topic.arn
  description = "The ARN of the SNS topic."
}

output "backupvaultout" {
  value       = aws_backup_vault_notifications.bkupfail_vault_notify.backup_vault_events
  description = "backupvaultevents"
}
