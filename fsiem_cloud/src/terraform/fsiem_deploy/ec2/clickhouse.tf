# S3 directory to store Clickhouse archive data
resource "aws_s3_object" "clickhouse_data_directory" {
  bucket       = local.clickhouse_data_bucket
  acl          = "private"
  key          = "${local.clickhouse_archive_dir_name}/"
  content_type = "application/x-directory"
}


# S3 directory to store Clickhouse backup data
resource "aws_s3_object" "clickhouse_backup_directory" {
  bucket       = local.clickhouse_backup_bucket
  acl          = "private"
  key          = "${local.clickhouse_backup_dir_name}/"
  content_type = "application/x-directory"
}
