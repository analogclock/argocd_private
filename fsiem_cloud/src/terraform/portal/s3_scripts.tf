#
# S3 bucket to store scripts and allow download from fsiem instances
#

# TODO: add logging bucket and logging config
# TODO: add event notifications for any WRITEs to the bucket


#
# scripts_bucket
#

# Bucket to store VM scripts
# Ignored as ec2 instances currently access this bucket publicly
#tfsec:ignore:aws-s3-block-public-acls tfsec:ignore:aws-s3-block-public-policy tfsec:ignore:aws-s3-ignore-public-acls tfsec:ignore:aws-s3-no-public-buckets
resource "aws_s3_bucket" "scripts_bucket" {
  bucket = local.s3_scripts_bucket
  lifecycle {
    # Any Terraform plan that includes a destroy of this resource will succeed.
    # We have versioning and allow manual modifications in this bucket, thus
    # deletion could fail without this.
    prevent_destroy = false
  }
}

resource "aws_s3_bucket_versioning" "scripts_bucket" {
  bucket = aws_s3_bucket.scripts_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "scripts_bucket" {
  bucket = aws_s3_bucket.scripts_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_acl" "scripts_bucket" {
  bucket = aws_s3_bucket.scripts_bucket.id
  acl    = "private"
}


# upload cloud-init startup scripts to s3
resource "aws_s3_object" "scripts" {
  # all files in the scripts folder, but not ".terragrunt-source-manifest"
  # file, which is some temp terragrunt artifact created automatically
  for_each = setsubtract(fileset("scripts", "*"), [".terragrunt-source-manifest"])
  bucket   = aws_s3_bucket.scripts_bucket.id
  key      = each.key
  content = templatefile("scripts/${each.key}",
    {
      cognito_url = "https://cognito-idp.${var.region}.amazonaws.com/${aws_cognito_user_pool.forticloud.id}/.well-known/openid-configuration"
    }
  )
  content_type = "text/plain"
  etag         = filemd5("scripts/${each.key}")
}

resource "aws_s3_object" "fsiem_monitor" {
  bucket       = aws_s3_bucket.scripts_bucket.id
  source       = var.fortimonitor_script
  key          = "fsiem.py"
  content_type = "text/plain"
  etag         = filemd5(var.fortimonitor_script)
}

resource "aws_s3_object" "fsiem_api_monitor" {
  bucket       = aws_s3_bucket.scripts_bucket.id
  source       = var.fortimonitor_api_script
  key          = "fsiem_api.py"
  content_type = "text/plain"
  etag         = filemd5(var.fortimonitor_script)
}

# Add logging bucket for tac and upload to taclogs_bucket

#
# taclogs_bucket
#

resource "aws_s3_bucket" "taclogs_bucket" {
  bucket = local.s3_taclogs_bucket
  lifecycle {
    # Any Terraform plan that includes a destroy of this resource will succeed.
    # We have versioning and allow manual modifications in this bucket, thus
    # deletion could fail without this.
    prevent_destroy = false
  }
}

resource "aws_s3_bucket_versioning" "taclogs_bucket" {
  bucket = aws_s3_bucket.taclogs_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "taclogs_bucket" {
  bucket = aws_s3_bucket.taclogs_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_acl" "taclogs_bucket" {
  bucket = aws_s3_bucket.taclogs_bucket.id
  acl    = "private"
}

# Lifecycle configuration for taclogs_bucket
resource "aws_s3_bucket_lifecycle_configuration" "tac_logs_lifecycle_config" {
  bucket = aws_s3_bucket.taclogs_bucket.id
  rule {
    id = "taclogslifecyclerule1"
    # the objects in S3 taclogs buckets will be removed after 14 days
    expiration {
      days = 14
    }
    status = "Enabled"
  }
}

# Bucket to store and retrieve the FSIEM upgrade packages
resource "aws_s3_bucket" "upgrade_package_bucket" {
  bucket = local.s3_upgrade_packages_bucket
}

resource "aws_s3_bucket_acl" "upgrade_package_bucket" {
  bucket = aws_s3_bucket.upgrade_package_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "upgrade_package_bucket" {
  bucket = aws_s3_bucket.upgrade_package_bucket.bucket
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
