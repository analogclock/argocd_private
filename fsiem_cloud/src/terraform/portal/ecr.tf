/*
  ECR repos to store docker images
*/

# Ignored as current deployment always uses the latest tag
#tfsec:ignore:aws-ecr-enforce-immutable-repository
resource "aws_ecr_repository" "fsiem-deploy" {
  name                 = local.ecs_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.key.arn
  }
}

# Ignored as current deployment always uses the latest tag
#tfsec:ignore:aws-ecr-enforce-immutable-repository
resource "aws_ecr_repository" "fsiem_daily_job" {
  name                 = "fsiem-daily-job-${var.environment}"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.key.arn
  }
}

# Ignored as current deployment always uses the latest tag
#tfsec:ignore:aws-ecr-enforce-immutable-repository
resource "aws_ecr_repository" "fsiem_terraform_updater" {
  name                 = "fsiem-terraform-updater-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.key.arn
  }
}

# Ignored as current deployment always uses the latest tag
#tfsec:ignore:aws-ecr-enforce-immutable-repository
resource "aws_ecr_repository" "fsiem_scheduled_upgrade" {
  name                 = "fsiem-scheduled-upgrade-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.key.arn
  }
}

# Ignored as current deployment always uses the latest tag
#tfsec:ignore:aws-ecr-enforce-immutable-repository
resource "aws_ecr_repository" "fsiem_expiry_notification" {
  name                 = "fsiem-expiry-notification-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.key.arn
  }
}
