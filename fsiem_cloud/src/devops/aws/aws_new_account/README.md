# Setup new AWS account

This is a guide to setup a new AWS for FortiSiem SaaS platform

## Prerequisites

### User account
Log in to [Fortinet AWS account](https://aws.corp.fortinet.com/)
- Dev/Playground account# `023941436530`
- Prod account# `327332988639`

Create [user account](https://us-east-1.console.aws.amazon.com/iamv2/home#/users)
with the name `terraform-deploy` with programmatic access

Add the following policies to the user:
```
AmazonEC2FullAccess
SecretsManagerReadWrite
IAMFullAccess
AmazonS3FullAccess
CloudWatchFullAccess
CloudFrontFullAccess
AmazonAPIGatewayAdministrator
AmazonVPCFullAccess
AWSLambda_FullAccess
```

Create and attach policies from `FsiemSaasMisc.json` manually to this user.
When required update AWS account IDs in the policies.

### S3 bucket

Manually create S3 bucket `fsiem-terraform-ftn` and update `deployment_bucket` and
`deployment_bucket_region` in the environment's .hcl file.

Update S3 bucket in the override file:
`env/$CI_ENVIRONMENT_NAME/terragrunt.var.overrides.yaml`

This bucked will be used to store terragrunt state and other useful things.
Terragrunt cannot create this bucket, because this is a circular dependency.
