# fsiem_backup

Backup ClickHouse data to AWS S3 using `clickhouse-backup` tool

```bash
# Backup settings are controlled via ENV variables
export REMOTE_STORAGE="s3"
export LOG_LEVEL="info"
export S3_REGION="us-east-1"
export S3_BUCKET="fsiem-clickhouse-backups-us-east-1-playground"
export S3_PATH="FSMCLD0000000154"
export S3_COMPRESSION_LEVEL="1"
export S3_COMPRESSION_FORMAT="tar"
export S3_USE_CUSTOM_STORAGE_CLASS="false"
export S3_STORAGE_CLASS="STANDARD"
export S3_CONCURRENCY="1"
export S3_DEBUG="true"

DATE=$(date --utc --rfc-3339=date)
FULL_BACKUP_NAME="$DATE-full"
INC_BACKUP_NAME="$DATE-inc"

# We need to call clickhouse-backup with sudo and -E flag, to pass env variables.
# Main testing sequence, create full backup, then incremental backup
sudo -E clickhouse-backup create_remote $FULL_BACKUP_NAME
sudo -E clickhouse-backup create_remote --diff-from-remote $FULL_BACKUP_NAME $INC_BACKUP_NAME
sudo -E clickhouse-backup delete local $FULL_BACKUP_NAME
sudo -E clickhouse-backup delete local $INC_BACKUP_NAME
```

## Clean and misc tasks

```bash
sudo -E clickhouse-backup clean
sudo -E clickhouse-backup clean_remote_broken
```

## Restore

```bash
# Example queries to drop tables
# DROP TABLE IF EXISTS fsiem.events_all SYNC
# DROP TABLE IF EXISTS fsiem.events_replicated SYNC
sudo -E clickhouse-backup restore backup_name1
sudo -E clickhouse-backup list all
```
