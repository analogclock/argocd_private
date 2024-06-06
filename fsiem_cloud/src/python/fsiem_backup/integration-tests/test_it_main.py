from main import parse_args, main

args = [
    '--serial_number', 'FSMCLD0000000154',
    '--region', 'us-east-1',
    '--dynamodb_backup_table', 'fsiem_clickhouse_backup_playground',
    '--dynamodb_backup_options_table', 'fsiem_backup_options_playground',
    '--dynamodb_region', 'us-east-1',
    '--dynamodb_activation_table', 'fsiem_activation_table_playground',
    '--s3_bucket', 'fsiem-clickhouse-backups-us-east-1-playground',
    '--s3_path', 'FSMCLD0000000155',
    '--remote_storage', 's3',
    '--log_level', 'WARN',
    '--s3_compression_level', '1',
    '--s3_compression_format', 'tar',
    '--s3_use_custom_storage_class', 'false',
    '--s3_storage_class', 'STANDARD',
    '--s3_concurrency', '1',
    '--s3_debug', 'false',
    '--max_backups_in_chain', '3']


def test_main_backup():
    config = parse_args(args)
    main(vars(config))
