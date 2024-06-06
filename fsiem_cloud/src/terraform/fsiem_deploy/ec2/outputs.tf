/*
  Outputs of the deployment
*/
output "super_url" {
  value       = "https://${aws_route53_record.super.fqdn}"
  description = "FSIEM Super URL"
}

output "workers_url" {
  value       = "https://${aws_route53_record.worker.fqdn}"
  description = "FSIEM Workers URL"
}

output "external_storage" {
  value       = aws_iam_role.instance_role.arn
  description = "FSIEM instance iam role arn"
}
