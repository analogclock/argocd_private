output "provisioning_api" {
  value = format("%s%s%s",
    aws_api_gateway_deployment.deployment.invoke_url,
    aws_api_gateway_stage.stage.stage_name,
  "/api")
  description = "The API Gateway URL for the portal API, this is used in UI env file(s)"
}

output "cloudfront_url" {
  value       = aws_cloudfront_distribution.portal_distribution.domain_name
  description = "The Cloudfront distribution URL for the portal UI"
}

output "user_pool_id" {
  value       = aws_cognito_user_pool.forticloud.id
  description = "The Cognito user pool id"
}

output "forticloud_client_id" {
  value       = aws_cognito_user_pool_client.forticloud.id
  description = "Id of the client from 'AWS Cognito > App Integration' to use with SSO, aka FortinetOneClientId in API and UI"
}

output "ui_url" {
  value       = "https://${var.domain_name}"
  description = "Portal UI URL, a user-friendly alias for CloudFront URL"
}

output "environment" {
  value       = var.environment
  description = "The name of the deployed environment"
}

output "region" {
  value       = var.region
  description = "AWS region that hosts deployed portal"
}

output "cognito_url" {
  value       = "https://${aws_cognito_user_pool.forticloud.domain}.auth.${var.region}.amazoncognito.com"
  description = "The url of the cognito user pool"
}

output "vpc_nat_public_ips" {
  value       = module.vpc.nat_public_ips
  description = "List of public Elastic IPs created for AWS NAT Gateway"
}

output "cognito_auth_url" {
  value = format("%s%s%s%s%s",
    "https://${aws_cognito_user_pool.forticloud.domain}.auth.${var.region}.amazoncognito.com",
    "/oauth2/authorize?identity_provider=FortiCloud",
    "&redirect_uri=https://localhost:4201/login&response_type=TOKEN",
    "&client_id=${aws_cognito_user_pool_client.forticloud.id}",
    "&scope=aws.cognito.signin.user.admin> openid"
  )
  description = "You can use this URL for testing SSO"
}

# This is used for pasting values into terragrunt.hcl file.
# For prod env, we do NOT want to have localhost links, but for other env it's fine.
# Remove empty URLs for prod env when copying this into the prod terragrunt.hcl file.
output "callback_urls" {
  value = format("[\n    \"%s\",\n    \"%s\",\n    \"%s\"\n]",
    var.environment == "prod" ? "" : "https://localhost:4201/login",
    format("https://%s/login", aws_cloudfront_distribution.portal_distribution.domain_name),
    format("https://%s/login", var.domain_name),
  )
  description = ".hcl file input overrides for 'callback_urls'"
}

# Remove empty URLs for prod env when copying this into the prod terragrunt.hcl file.
output "logout_urls" {
  value = format("[\n    \"%s\",\n    \"%s\",\n    \"%s\",\n    \"%s\",\n    \"%s\",\n    \"%s\"\n]",
    var.environment == "prod" ? "" : "https://localhost:4201/logout",
    var.environment == "prod" ? "" : "https://localhost:4201/product-information",
    format("https://%s/logout", aws_cloudfront_distribution.portal_distribution.domain_name),
    format("https://%s/product-information", aws_cloudfront_distribution.portal_distribution.domain_name),
    format("https://%s/logout", var.domain_name),
    format("https://%s/product-information", var.domain_name),
  )
  description = ".hcl file input overrides for 'logout_urls'"
}
