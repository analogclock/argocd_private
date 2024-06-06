/*
  Creates a dynamodb table to store information on deployments
*/

locals {
  docs_link = "https://docs.fortinet.com/document/fortisiem/7.1.5/release-notes/46171/whats-new-in-7-1-5"
  zip_name  = "FSM_Upgrade_All_7.1.5_build0181.zip"
}

# Ignoring these as we will need to update the client side (portal) as well.
# DO NOT enable encryption without a managed key, AWS will create a key in the background
# that is unmanaged by terraform and will lead to terrible problems later.
#tfsec:ignore:aws-dynamodb-table-customer-key tfsec:ignore:aws-dynamodb-enable-at-rest-encryption
resource "aws_dynamodb_table" "fsiem_activation_table" {
  name             = local.dynamodb_activation_table
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "serialNumber"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "serialNumber"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

# Stores information on the different upgrade paths
resource "aws_dynamodb_table" "fsiem_upgrades_table" {
  name         = local.dynamodb_upgrades_table
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "upgradePath"

  attribute {
    name = "upgradePath"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

resource "aws_dynamodb_table_item" "upgrade_711_715" {
  table_name = aws_dynamodb_table.fsiem_upgrades_table.name
  hash_key   = aws_dynamodb_table.fsiem_upgrades_table.hash_key
  item       = <<ITEM
{
  "upgradePath": {"S": "7.1.1_7.1.5"},
  "currentVersion": {"S": "7.1.1"},
  "newVersion": {"S": "7.1.5"},
  "zipName": {"S": "${local.zip_name}"},
  "ssmDocName": {"S": "${aws_ssm_document.fsiem_upgrade.name}"},
  "docsLink": {"S": "${local.docs_link}"}
}
ITEM
}

resource "aws_dynamodb_table_item" "upgrade_714_715" {
  table_name = aws_dynamodb_table.fsiem_upgrades_table.name
  hash_key   = aws_dynamodb_table.fsiem_upgrades_table.hash_key
  item       = <<ITEM
{
  "upgradePath": {"S": "7.1.4_7.1.5"},
  "currentVersion": {"S": "7.1.4"},
  "newVersion": {"S": "7.1.5"},
  "zipName": {"S": "${local.zip_name}"},
  "ssmDocName": {"S": "${aws_ssm_document.fsiem_upgrade.name}"},
  "docsLink": {"S": "${local.docs_link}"}
}
ITEM
}

# Stores information on scheduled customer upgrades
# Items will be added/removed through the portal
resource "aws_dynamodb_table" "fsiem_scheduled_upgrades_table" {
  name             = local.dynamodb_scheduled_upgrades_table
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "serialNumber"
  range_key        = "upgradePath"
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"

  attribute {
    name = "serialNumber"
    type = "S"
  }
  attribute {
    name = "upgradePath"
    type = "S"
  }

  # For future reference
  # attribute {
  #   name = "scheduled"
  #   type = "S"
  # }
  # attribute {
  #   name = "status"
  #   type = "S"
  # }

  point_in_time_recovery {
    enabled = true
  }
}

# For future reference
# resource "aws_dynamodb_table_item" "scheduled_upgrade" {
#   table_name = aws_dynamodb_table.fsiem_scheduled_upgrades_table.name
#   hash_key   = aws_dynamodb_table.fsiem_scheduled_upgrades_table.hash_key
#   item       = <<ITEM
# {
#   "serialNumber": {"S": "fsiem-mszymosz-1"},
#   "upgradePath": {"S": "6.4.0_6.5.0"},
#   "scheduled": {"S": "2022-06-07T00:00:00"},
#   "status": {"S": "Pending"}
# }
# ITEM
# }

# Stores information on scheduled customer upgrades
# Items will be added/removed through the portal
resource "aws_dynamodb_table" "fsiem_poc_approval_table" {
  name             = local.dynamodb_poc_approval_table
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "serialNumber"
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"

  attribute {
    name = "serialNumber"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

# A list of emails that have either bounced or returned a complaint
# therefore we should not send emails to
resource "aws_dynamodb_table" "fsiem_email_block_table" {
  name             = local.dynamodb_email_block_table
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "email"
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"

  attribute {
    name = "email"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

# Table to store backups
# This table has serial number as a primary key and backup name as a range key.
# This allows to store several backup entries for one serial number.
#
# +--------------+-----------------------+--------------------+
# | serialNumber |         name          |        ...         |
# +--------------+-----------------------+--------------------+
# |         001  | 2023-03-28T23:00:00Z  | other dynamic data |
# |         001  | 2023-03-29T23:00:00Z  |                    |
# |         002  | 2023-03-28T23:00:00Z  |                    |
# +--------------+-----------------------+--------------------+
resource "aws_dynamodb_table" "fsiem_clickhouse_backup_table" {
  name             = local.dynamodb_backup_table
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "serialNumber"
  range_key        = "name"
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"
  attribute {
    name = "serialNumber"
    type = "S"
  }
  attribute {
    name = "name"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
}

# Table to store clickhouse restores
# This table has serial number as a primary key and restore name as a range key.
# This allows to store several restore entries for one serial number.
#
# +--------------+-----------------------+--------------------+
# | serialNumber |         name          |        ...         |
# +--------------+-----------------------+--------------------+
# |         001  | 2023-03-28T23:00:00Z  | other dynamic data |
# |         001  | 2023-03-29T23:00:00Z  |                    |
# |         002  | 2023-03-28T23:00:00Z  |                    |
# +--------------+-----------------------+--------------------+
resource "aws_dynamodb_table" "fsiem_clickhouse_restore_table" {
  name             = local.dynamodb_restore_table
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "serialNumber"
  range_key        = "name"
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"
  attribute {
    name = "serialNumber"
    type = "S"
  }
  attribute {
    name = "name"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
}

# Table to store and manage compute overrides
# This table has serial number as a primary key. All other columns are optional.
# They should have the same name as the fields generated by fsiem_resource_calc i.e. cmdb_throughput.
# They should also use the same types, for instance cmdbThroughput will be type N, superInstanceTypes will be SS.
# If the type does not exists in the table it simply wont be overwritten and preserve the
# value generated by fsiem_resource_calc.
#
# +--------------+----------------------+--------------------+
# | serialNumber | super_instance_types |        ...         |
# +--------------+----------------------+--------------------+
# |         001  | ["m6i.xlarge"]       | other dynamic data |
# +--------------+----------------------+--------------------+
resource "aws_dynamodb_table" "fsiem_compute_override_table" {
  name         = local.dynamodb_compute_override_table
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "serialNumber"
  attribute {
    name = "serialNumber"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
}

# Stores requests from customers to lower their storage
# Items will be added through the portal
resource "aws_dynamodb_table" "fsiem_storage_approval_table" {
  name             = local.dynamodb_storage_approval_table
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "serialNumber"
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"

  attribute {
    name = "serialNumber"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}


# Table to store machine-to-machine credentials
#
# +--------------+-----------------------+
# | serialNumber | backup_options        |
# +--------------+-----------------------+
# |       00000  | "json string"         |
# +--------------+-----------------------+
resource "aws_dynamodb_table" "fsiem_backup_options" {
  name         = local.dynamodb_backup_options_table
  hash_key     = "serialNumber"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "serialNumber"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
}

# Insert example configuration for demo purposes in playground/dev.
# Put any environmental variable supported by the tool:
# https://github.com/Altinity/clickhouse-backup.
resource "aws_dynamodb_table_item" "fsiem_backup_options_example" {
  count      = local.is_dev_or_playground ? 1 : 0
  table_name = aws_dynamodb_table.fsiem_backup_options.name
  hash_key   = aws_dynamodb_table.fsiem_backup_options.hash_key
  item       = <<ITEM
  {
    "serialNumber": {"S": "00000"},
    "backupOptions": {"S": "[{\"S3_COMPRESSION_LEVEL\": \"1\"}, {\"S3_COMPRESSION_FORMAT\": \"tar\"}, {\"S3_USE_CUSTOM_STORAGE_CLASS\": \"false\"}]"}
  }
  ITEM
}

# Table to store external storage details
resource "aws_dynamodb_table" "fsiem_external_storage_table" {
  name             = local.dynamodb_ext_storage_table
  hash_key         = "serialNumber"
  range_key        = "organizationId"
  billing_mode     = "PAY_PER_REQUEST"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  attribute {
    name = "serialNumber"
    type = "S"
  }
  attribute {
    name = "organizationId"
    type = "N"
  }
  point_in_time_recovery {
    enabled = true
  }
}

# resource "aws_dynamodb_table_item" "fsiem_external_storage_table_item" {
#   table_name = aws_dynamodb_table.fsiem_external_storage_table.name
#   hash_key   = aws_dynamodb_table.fsiem_external_storage_table.hash_key
#   item       = <<ITEM
#   {
#     "serialNumber": {"S": "00000"},
#     "organizationID": {"S": "ALL"},
#     "externalStorageDest": {"S": "test-ssm-alt-region"}
#   }
#   ITEM
# }

# Table to store Clickhouse partitions data sizes
resource "aws_dynamodb_table" "fsiem_metrics_storage_table" {
  name         = local.dynamodb_metrics_storage_table
  hash_key     = "serialNumber"
  billing_mode = "PAY_PER_REQUEST"
  attribute {
    name = "serialNumber"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
}

resource "aws_dynamodb_table" "fsiem_external_storage_status_table" {
  name             = local.dynamodb_ext_storage_status_table
  hash_key         = "serialNumber"
  range_key        = "startDateTime"
  billing_mode     = "PAY_PER_REQUEST"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  attribute {
    name = "serialNumber"
    type = "S"
  }
  attribute {
    name = "startDateTime"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

