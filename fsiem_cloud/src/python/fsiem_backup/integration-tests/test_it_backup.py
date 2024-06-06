from datetime import datetime
from fsiem_api_client.aws.ssm_ops import SsmOps
from fsiem_api_client.clickhouse_backup_table import (
    BackupInfo, BackupStatus, ClickhouseBackupTable)
from backup import delete_backups, run_backup

sn = 'FSMCLD0000000154'
region = 'us-east-1'
s3_bucket = 'fsiem-clickhouse-backups-us-east-1-playground'
s3_path = sn
full = BackupInfo(serial_number='FSMCLD0000000154',
                  name='2023-03-31-full-0000',
                  start_date=datetime.utcnow().isoformat(),
                  stop_date=datetime.utcnow().isoformat(),
                  status=BackupStatus.backup_in_progress,
                  failed_reason='',
                  previous_backup_name='none',
                  type='full',
                  current_seq_number=1,
                  total_seq_number=1,
                  s3_location=f'{s3_bucket}/{s3_path}',
                  backup_options='')

table = ClickhouseBackupTable('fsiem_clickhouse_backup_playground', region)
ssm_ops = SsmOps(region, sn)
backup_options = {
    'serial_number': sn,
    'region': region,
    'remote_storage': 's3',
    'log_level': 'WARN',
    's3_bucket': s3_bucket,
    's3_path': s3_path,
    's3_compression_level': '1',
    's3_compression_format': 'tar',
    's3_use_custom_storage_class': 'false',
    's3_storage_class': 'STANDARD',
    's3_concurrency': '1',
    's3_debug': 'false',
    'max_backups_in_chain': '3'
}


def test_run_backup():
    history = table.get_backup_history(sn)
    run_backup(history, table, ssm_ops, backup_options)


def test_delete_backups():
    history = table.get_backup_history(sn)
    delete_backups(history, table, ssm_ops, backup_options)
