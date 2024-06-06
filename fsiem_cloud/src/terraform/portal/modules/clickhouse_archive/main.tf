# Add clickhouse s3 bucket for storing data

# add clickhouse s3 archive bucket if we are deploying a clickhouse
# storage type
resource "aws_s3_bucket" "clickhouse_archive_data" {
  bucket = var.bucket_name

  lifecycle {

    # Any Terraform plan that includes a destroy of this resource will succeed.
    # We have versioning and allow manual modifications in this bucket, thus
    # deletion could fail without this.
    prevent_destroy = false
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encryption_clickhouse" {
  bucket = aws_s3_bucket.clickhouse_archive_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_acl" "acl_clickhouse" {
  bucket = aws_s3_bucket.clickhouse_archive_data.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "versioning_clickhouse" {
  bucket = aws_s3_bucket.clickhouse_archive_data.id
  versioning_configuration {
    status = "Suspended"
  }
}

# forcibly block public access settings for clickhouse
resource "aws_s3_bucket_public_access_block" "block_clickhouse_public" {
  bucket = aws_s3_bucket.clickhouse_archive_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "delete_prev_versions_clickhouse" {
  bucket = aws_s3_bucket.clickhouse_archive_data.id

  # delete old versions
  rule {
    id = "Expire old previous versions"
    # This was deployed as enabled. Once enabled versioning cannot be disabled,
    # only suspended.
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
      days_after_initiation = 2
    }
  }
}

resource "aws_s3_bucket_ownership_controls" "clickhouse_controls" {
  bucket = aws_s3_bucket.clickhouse_archive_data.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}
