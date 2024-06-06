# Creates secrets that the lambda function needs. Currently need to manually add the secrets values.
resource "aws_secretsmanager_secret" "certificate_key" {
  name                    = local.fortinet_one_certificate_key
  recovery_window_in_days = 0
  kms_key_id              = aws_kms_key.key.arn
}

resource "aws_secretsmanager_secret" "passphrase_key" {
  name                    = local.fortinet_one_passphrase_key
  recovery_window_in_days = 0
  kms_key_id              = aws_kms_key.key.arn
}

resource "aws_secretsmanager_secret" "licensing_certificate_key" {
  name                    = local.licensing_certificate_key
  recovery_window_in_days = 0
  kms_key_id              = aws_kms_key.key.arn
}

resource "aws_secretsmanager_secret" "licensing_passphrase_key" {
  name                    = local.licensing_passphrase_key
  recovery_window_in_days = 0
  kms_key_id              = aws_kms_key.key.arn
}

# Should be in format:
# {
#   "customer_key": "..."
# }
resource "aws_secretsmanager_secret" "fortimonitor_key" {
  name                    = "fortimonitor-${var.environment}"
  recovery_window_in_days = 0
  kms_key_id              = aws_kms_key.key.arn
  dynamic "replica" {
    for_each = toset(var.additional_regions)
    content {
      region = replica.key
    }
  }
}

# Should be in format:
# {
#   "api_key": "..."
# }
resource "aws_secretsmanager_secret" "fortimonitor_api_key" {
  name                    = local.fortimonitor_api_key
  recovery_window_in_days = 0
  kms_key_id              = aws_kms_key.key.arn
}

resource "aws_secretsmanager_secret" "fortimonitor_api_key_write" {
  name                    = local.fortimonitor_api_key_write
  recovery_window_in_days = 0
  kms_key_id              = aws_kms_key.key.arn
}

# Used for json encoding AWS Cognito secret id and secret
locals {
  # This is created and stored in clear text in a state file. This secret is stored
  # twice: once when created, once when referenced.
  licensing_credentials = {
    client_id     = aws_cognito_user_pool_client.licence_activation.id
    client_secret = aws_cognito_user_pool_client.licence_activation.client_secret
  }
  fsiem_vm_auth_credentials = {
    client_id     = aws_cognito_user_pool_client.fsiem_vm_auth_pool_client.id
    client_secret = aws_cognito_user_pool_client.fsiem_vm_auth_pool_client.client_secret
  }
}

# License API key
resource "aws_secretsmanager_secret" "licensing_credentials" {
  name                    = "licensing-creds-${var.environment}"
  recovery_window_in_days = 0
  dynamic "replica" {
    for_each = toset(var.additional_regions)
    content {
      region = replica.key
    }
  }
}

resource "aws_secretsmanager_secret_version" "licensing_credentials" {
  secret_id     = aws_secretsmanager_secret.licensing_credentials.id
  secret_string = jsonencode(local.licensing_credentials)
}

# AWS -> VM API (AppServer) authentication via JWT
resource "aws_secretsmanager_secret" "fsiem_vm_auth_credentials" {
  name                    = "fsiem-vm-auth-creds-${var.environment}"
  recovery_window_in_days = 0
  dynamic "replica" {
    for_each = toset(var.additional_regions)
    content {
      region = replica.key
    }
  }
}

resource "aws_secretsmanager_secret_version" "fsiem_vm_auth_credentials" {
  secret_id     = aws_secretsmanager_secret.fsiem_vm_auth_credentials.id
  secret_string = jsonencode(local.fsiem_vm_auth_credentials)
}
