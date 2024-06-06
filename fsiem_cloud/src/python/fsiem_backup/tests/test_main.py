from fsiem_api_client import ActivationTable
from main import parse_args, should_run

args = {
    'serial_number': 'FSMCLD0000000155',
    'action': 'backup',
    'region': 'us-east-1',
    'dynamodb_region': 'us-east-1',
    'dynamodb_backup_table': 'fsiem_backup_table_playground',
    'dynamodb_backup_options_table': 'fsiem_backup_options_playground',
    'dynamodb_activation_table': 'fsiem_activation_table_playground',
    'dynamodb_restore_table': 'fsiem_restore_table_playground',
    's3_bucket': 'fsiem-clickhouse-backups-us-east-1-playground',
    's3_path': 'FSMCLD0000000155',
    'remote_storage': 's3',
    'log_level': 'WARN',
    's3_compression_level': '1',
    's3_compression_format': 'tar',
    's3_use_custom_storage_class': 'false',
    's3_storage_class': 'STANDARD',
    's3_concurrency': '1',
    's3_debug': 'false',
    'max_backups_in_chain': '3'
}


def test_parse_args():
    parser = parse_args([
        '--serial_number', args['serial_number'],
        '--region', args['region'],
        '--dynamodb_region', args['dynamodb_region'],
        '--dynamodb_backup_table', args['dynamodb_backup_table'],
        '--dynamodb_backup_options_table', args['dynamodb_backup_options_table'], # noqa
        '--dynamodb_activation_table', args['dynamodb_activation_table'],
        '--s3_bucket', args['s3_bucket'],
        '--s3_path', args['s3_path'],
        '--remote_storage', args['remote_storage'],
        '--log_level', args['log_level'],
        '--s3_compression_level', args['s3_compression_level'],
        '--s3_compression_format', args['s3_compression_format'],
        '--s3_use_custom_storage_class', args['s3_use_custom_storage_class'], # noqa
        '--s3_storage_class', args['s3_storage_class'],
        '--s3_concurrency', args['s3_concurrency'],
        '--s3_debug', args['s3_debug'],
        '--max_backups_in_chain', args['max_backups_in_chain']])
    assert parser.serial_number == args['serial_number']


def test_should_run():

    res = should_run('incorrect_status', False, False, True)
    assert not res.can_run
    assert res.reason

    res = should_run(ActivationTable.complete, True, False, True)
    assert not res.can_run
    assert res.reason

    res = should_run(ActivationTable.complete, False, True, True)
    assert not res.can_run
    assert res.reason

    res = should_run(ActivationTable.complete, False, False, False)
    assert not res.can_run
    assert res.reason

    res = should_run(ActivationTable.complete, False, False, True)
    assert res.can_run
    assert not res.reason
