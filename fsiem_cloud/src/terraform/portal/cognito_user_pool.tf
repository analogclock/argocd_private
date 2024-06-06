/*
  Create a user pool to act as the SP for FortiCloud SSO IDP
  Set up the defaults for the user pool to ensure that they
  aren't insecure values.
*/

resource "aws_cognito_user_pool" "forticloud" {
  name = "forticloud-fsiem-${var.environment}"

  # Add required SAML Attributes
  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "IAM_account_name"
    required                 = "false"

    string_attribute_constraints {
      max_length = "256"
      min_length = "1"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "IAM_username"
    required                 = "false"

    string_attribute_constraints {
      max_length = "256"
      min_length = "1"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "NameId"
    required                 = "false"

    string_attribute_constraints {
      max_length = "256"
      min_length = "1"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "IAM_account_alias"
    required                 = "false"

    string_attribute_constraints {
      max_length = "256"
      min_length = "1"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "auth_status"
    required                 = "false"

    string_attribute_constraints {
      max_length = "256"
      min_length = "1"
    }
  }

  /*
    The following is not used by the user_pool
    but are defaulted to ensure that they will
    not conflict with anything
  */

  admin_create_user_config {
    allow_admin_create_user_only = "true"

    invite_message_template {
      email_message = "Your username is {username} and temporary password is {####}. "
      email_subject = "Your temporary password"
      sms_message   = "Your username is {username} and temporary password is {####}. "
    }
  }

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  mfa_configuration = "OFF"
  password_policy {
    minimum_length                   = "6"
    require_lowercase                = "false"
    require_numbers                  = "false"
    require_symbols                  = "false"
    require_uppercase                = "false"
    temporary_password_validity_days = "7"
  }

  sms_authentication_message = "Your authentication code is {####}. "

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_message        = "Your verification code is {####}. "
    email_subject        = "Your verification code"
    sms_message          = "Your verification code is {####}. "
  }

  # ---
}

/*
  Add prefix domain for the user pool
  simplifies configuration and deployment
*/
resource "aws_cognito_user_pool_domain" "forticloud" {
  domain       = aws_cognito_user_pool.forticloud.name
  user_pool_id = aws_cognito_user_pool.forticloud.id
}
