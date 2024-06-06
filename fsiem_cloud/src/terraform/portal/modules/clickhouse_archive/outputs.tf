output "bucket_arn" {
  value = aws_s3_bucket.clickhouse_archive_data.arn
}

output "bucket_id" {
  value = aws_s3_bucket.clickhouse_archive_data.id
}
