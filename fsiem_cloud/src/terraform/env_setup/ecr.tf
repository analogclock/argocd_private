/*
  ECR repos to store docker images
*/
# Ignored as current deployment always uses the latest tag
#tfsec:ignore:aws-ecr-enforce-immutable-repository
resource "aws_ecr_repository" "fsiem_backup" {
  name                 = "fsiem-backup-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.key.arn
  }
}
#tfsec:ignore:aws-ecr-enforce-immutable-repository
resource "aws_ecr_repository" "fsiem_setup" {
  name                 = "fsiem-setup-${var.environment}"
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
resource "aws_ecr_repository" "fsiem_storage_enforcer" {
  name                 = "fsiem-storage-enforcer-${var.environment}"
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
resource "aws_ecr_repository" "fsiem_license" {
  name                 = "fsiem-license-${var.environment}"
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
resource "aws_ecr_repository" "fsiem_metrics" {
  name                 = "fsiem-metrics-${var.environment}"
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
resource "aws_ecr_repository" "fsiem_monitor" {
  name                 = "fsiem-monitor-${var.environment}"
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
resource "aws_ecr_repository" "fsiem_worker_lifecycle" {
  name                 = "fsiem-worker-lifecycle-${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.key.arn
  }
}

resource "aws_ecr_replication_configuration" "replication" {
  replication_configuration {
    rule {
      dynamic "destination" {
        for_each = toset(var.additional_regions)
        content {
          region      = destination.key
          registry_id = data.aws_caller_identity.current.account_id
        }
      }
      repository_filter {
        filter      = "fsiem-backup-${var.environment}"
        filter_type = "PREFIX_MATCH"
      }
    }
    rule {
      dynamic "destination" {
        for_each = toset(var.additional_regions)
        content {
          region      = destination.key
          registry_id = data.aws_caller_identity.current.account_id
        }
      }
      repository_filter {
        filter      = "fsiem-setup-${var.environment}"
        filter_type = "PREFIX_MATCH"
      }
    }
    rule {
      dynamic "destination" {
        for_each = toset(var.additional_regions)
        content {
          region      = destination.key
          registry_id = data.aws_caller_identity.current.account_id
        }
      }
      repository_filter {
        filter      = "fsiem-storage-enforcer-${var.environment}"
        filter_type = "PREFIX_MATCH"
      }
    }
    rule {
      dynamic "destination" {
        for_each = toset(var.additional_regions)
        content {
          region      = destination.key
          registry_id = data.aws_caller_identity.current.account_id
        }
      }
      repository_filter {
        filter      = "fsiem-license-${var.environment}"
        filter_type = "PREFIX_MATCH"
      }
    }
    rule {
      dynamic "destination" {
        for_each = toset(var.additional_regions)
        content {
          region      = destination.key
          registry_id = data.aws_caller_identity.current.account_id
        }
      }
      repository_filter {
        filter      = "fsiem-metrics-${var.environment}"
        filter_type = "PREFIX_MATCH"
      }
    }
    rule {
      dynamic "destination" {
        for_each = toset(var.additional_regions)
        content {
          region      = destination.key
          registry_id = data.aws_caller_identity.current.account_id
        }
      }
      repository_filter {
        filter      = "fsiem-monitor-${var.environment}"
        filter_type = "PREFIX_MATCH"
      }
    }
    rule {
      dynamic "destination" {
        for_each = toset(var.additional_regions)
        content {
          region      = destination.key
          registry_id = data.aws_caller_identity.current.account_id
        }
      }
      repository_filter {
        filter      = "fsiem-worker-lifecycle-${var.environment}"
        filter_type = "PREFIX_MATCH"
      }
    }
  }
}
