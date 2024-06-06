# Add support for all regions and clickhouse S3 backup data
# Note: you must define each region and aws provider in a separate module
# you cannot loop providers easily.

# Note: this matches our EC2 deployments configuration, deployments expect these
# buckets to be present to store and backup data

# empty provider will use our default
module "clickhouse-backup-us-east-1" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-us-east-1-${var.environment}"
}

module "clickhouse-backup-eu-central-1" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-eu-central-1-${var.environment}"
  providers   = { aws = aws.eu-central-1 }
}

module "clickhouse-backup-eu-west-1" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-eu-west-1-${var.environment}"
  providers   = { aws = aws.eu-west-1 }
}

module "clickhouse-backup-eu-west-2" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-eu-west-2-${var.environment}"
  providers   = { aws = aws.eu-west-2 }
}

module "clickhouse-backup-eu-west-3" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-eu-west-3-${var.environment}"
  providers   = { aws = aws.eu-west-3 }
}

module "clickhouse-backup-eu-north-1" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-eu-north-1-${var.environment}"
  providers   = { aws = aws.eu-north-1 }
}

module "clickhouse-backup-us-east-2" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-us-east-2-${var.environment}"
  providers   = { aws = aws.us-east-2 }
}

module "clickhouse-backup-us-west-2" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-us-west-2-${var.environment}"
  providers   = { aws = aws.us-west-2 }
}

module "clickhouse-backup-ca-central-1" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-ca-central-1-${var.environment}"
  providers   = { aws = aws.ca-central-1 }
}

module "clickhouse-backup-ap-south-1" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-ap-south-1-${var.environment}"
  providers   = { aws = aws.ap-south-1 }
}

module "clickhouse-backup-ap-southeast-1" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-ap-southeast-1-${var.environment}"
  providers   = { aws = aws.ap-southeast-1 }
}

module "clickhouse-backup-ap-southeast-2" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-ap-southeast-2-${var.environment}"
  providers   = { aws = aws.ap-southeast-2 }
}

module "clickhouse-backup-me-south-1" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-me-south-1-${var.environment}"
  providers   = { aws = aws.me-south-1 }
}

module "clickhouse-backup-ap-east-1" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-ap-east-1-${var.environment}"
  providers   = { aws = aws.ap-east-1 }
}

module "clickhouse-backup-af-south-1" {
  source      = "./modules/clickhouse_archive"
  bucket_name = "${local.clickhouse_backup_prefix}-af-south-1-${var.environment}"
  providers   = { aws = aws.af-south-1 }
}
