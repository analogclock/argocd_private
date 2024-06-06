/*
  S3 bucket to store manifests for S3 jobs
*/

resource "aws_s3_bucket" "fsiem_s3_job" {
  bucket = "fsiem-s3-job-${var.environment}"
  lifecycle {
    # Any Terraform plan that includes a destroy of this resource will succeed.
    prevent_destroy = false
  }
}

resource "aws_s3_bucket_ownership_controls" "fsiem_s3_job" {
  bucket = aws_s3_bucket.fsiem_s3_job.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "fsiem_s3_job" {
  bucket = aws_s3_bucket.fsiem_s3_job.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "fsiem_s3_job" {
  bucket = aws_s3_bucket.fsiem_s3_job.id
  versioning_configuration {
    status = "Disabled"
  }
}

# forcibly block public access settings
resource "aws_s3_bucket_public_access_block" "fsiem_s3_job" {
  bucket                  = aws_s3_bucket.fsiem_s3_job.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}



resource "aws_s3_bucket_server_side_encryption_configuration" "fsiem_s3_job" {
  bucket = aws_s3_bucket.fsiem_s3_job.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "fsiem_s3_job" {
  bucket = aws_s3_bucket.fsiem_s3_job.id

  # delete old versions
  rule {
    id     = "Expire old previous versions"
    status = "Enabled"
    noncurrent_version_expiration {
      noncurrent_days = 1
    }
    expiration {
      expired_object_delete_marker = true
    }
  }

  # delete partial incomplete uploads
  rule {
    id     = "Delete old incomplete multi-part uploads"
    status = "Enabled"
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}
