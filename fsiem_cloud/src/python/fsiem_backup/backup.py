from string import Template
from datetime import datetime
from botocore.exceptions import WaiterError
from fsiem_api_client.aws.ses import Ses
from fsiem_api_client.aws.ssm_ops import SsmOps
from fsiem_api_client.backup_options_table import BackupOptionsTable
from fsiem_api_client.clickhouse_backup_table import (
    BackupInfo, BackupInfoHistory, BackupStatus, ClickhouseBackupTable)
from fsiem_api_client.const import BackupType
from fsiem_api_client.exceptions import ExceptionInfo


NAME_TEMPLATE = "$date-$total_seq_number-$type"


def get_backup_info(history: BackupInfoHistory | None,
                    options: dict) -> BackupInfo:
    """Create backup info based on the history and options

    Parameters
    ----------
    history : BackupInfoHistory | None
        history of the previous backups or None for the first run
    options : dict
        backup options
    """
    # First time running this OR the modulo operator of count is 0.
    # For example: 3 % 3 = 0, 9 % 3 = 0. This means we need to  run a new full
    # backup when we reach the  max_backups_in_chain counter.
    type: BackupType
    if not history or \
       len(history.all) % int(options['max_backups_in_chain']) == 0:
        type = BackupType.FULL
    else:
        type = BackupType.INCREMENTAL

    # Counter for how many backups it total we ran, 1 for the first time,
    # or a previous value + 1
    total = 1 if not history else history.all[-1].total_seq_number + 1

    # Name
    template = Template(NAME_TEMPLATE)
    # Example: 2023-04-07-21-full or 2023-04-07-28-incremental
    name = template.substitute(
        date=datetime.utcnow().date().isoformat(),
        type=type.value,
        total_seq_number=total)

    # Counter for the backup number in the current backup chain.
    # 1 for the first time, or a previous value + 1
    current = 1 if not history else history.all[-1].current_seq_number + 1
    # If we have previous history, but this backup is a full backup
    # Then we set the current sequence number to 1
    if history and type == BackupType.FULL:
        current = 1

    # Link to the previous backup.
    # Empty for the first time, or a previous backup name
    prev_name = '' if not history else history.all[-1].name

    # If we have previous history, but this backup is a full backup
    # Then we don't need to link to the previous backup name
    if history and type == BackupType.FULL:
        prev_name = ''

    # S3 location for the data
    s3_location = f's3://{options["s3_bucket"]}/{options["s3_path"]}'

    info = BackupInfo(serial_number=options['serial_number'],
                      name=name,
                      start_date=datetime.utcnow().isoformat(),
                      stop_date='',
                      status=BackupStatus.backup_in_progress,
                      failed_reason='',
                      previous_backup_name=prev_name,
                      type=type.value,
                      current_seq_number=current,
                      total_seq_number=total,
                      s3_location=s3_location,
                      backup_options='')
    print(f'Backup object: {info}')
    return info


def get_backup_table(options: dict):
    return ClickhouseBackupTable(
        options['dynamodb_backup_table'],
        options['dynamodb_region'])


def get_backup_options_table(options: dict):
    return BackupOptionsTable(
        options['dynamodb_backup_options_table'],
        options['dynamodb_region'])


def run_backup(history: BackupInfoHistory, ch_table: ClickhouseBackupTable,
               options_table: BackupOptionsTable,
               ssm_ops: SsmOps, options: dict, ses: Ses):
    """Run full or incremental backup

    Parameters
    ----------
    history : BackupInfoHistory
        history of backups
    ch_table : ClickhouseBackupTable
        DynamoDb table
    options_table: BackupOptionsTable
        DynamoDb table with override options
    ssm_ops : SsmOps
        instance of ssm operations
    options : dict
        backup options
    ses: Ses
        Email client used for notification of failed backups
    """
    info = get_backup_info(history, options)

    backup_options = options_table.get(info.serial_number)
    if backup_options:
        print(f'Additional backup options: {str(backup_options)}')
        info.backup_options = str(backup_options)

    print('Insert backup record into a database')
    ch_table.insert(info)

    try:
        print('==> Run clickhouse-backup command')
        resp = ssm_ops.clickhouse_backup_create(
            info.name, BackupType(info.type),
            info.previous_backup_name, options,
            backup_options)
        print(f'Response: {resp}')

        print('==> Delete local copy of the backup from the worker disk')
        resp = ssm_ops.clickhouse_backup_delete(info.name, 'local', options)
        print(f'Response: {resp}')

        print('==> Cleanup local backups')
        try:
            resp = ssm_ops.clickhouse_backup_cleanup(options)
            print(f'Response: {resp}')
        except Exception as err:
            msg = ExceptionInfo.format(err)
            if "shadow: no such file or directory" in msg:
                # Swallow this exception, no need to raise.
                # Seems like we can ignore this error.
                # See https://stackoverflow.com/q/65629318/706456 and
                # https://dops-git106.fortinet-us.com/fsiem/fsiem_cloud/-/issues/521
                print('This warning may be ignored if it occurs infrequently')
                print(f'Warn: clickhouse cleanup did not succeed: {msg}')
            else:
                print(f'Error: clickhouse cleanup failed: {msg}')
                # Unexpected error, raise the original exception
                raise

        info.status = BackupStatus.backup_ok

    except Exception as err:
        print(f'ERROR: backup failed: {err}')
        info.failed_reason = ExceptionInfo.format(err)
        info.status = BackupStatus.backup_failed
        desc = f'''
        SSM task to execute clickhouse-backup.
        Options: {str(options)}
        Backup name: {info.name}
        Backup type: {info.type}
        Previous backup: {info.previous_backup_name}
        '''
        ses.send_email_task_failed(f'run_backup {options["serial_number"]}',
                                   desc, err,
                                   options['email_from_addr'],
                                   options['email_to_addr'])

    print(f'Backup has finished with status: {info.status}')
    info.stop_date = datetime.utcnow().isoformat()
    print('Update backup record in the database')
    ch_table.update(info)


def get_deletable_backups(
        history: BackupInfoHistory,
        chain_size: int = 3) -> list[BackupInfo] | None:
    """Given history, select backups that can be deleted

    Parameters
    ----------
    history : BackupInfoHistory
        Backup history
    chain_size : int
        The chain size, defaults to 3 (full -> incremental -> incremental)

    Returns
    -------
    list[BackupInfo] | None
        A list of old backups that can be deleted, or None
    """
    # We don't have two full chains, cannot delete anything
    if len(history.all) < 2 * chain_size:
        return None

    # Start from most recent backups, look for the FULL backup AND
    # that its index + 1 is greater or equals to the chain size.
    # Return all backups that are older then the index + 1.
    # We use index + 1 because we want to avoid deleting the FULL backup.
    # Examples (where i - incremental, f - full), goes from newest .. oldest
    #
    # Return None, because we don't have 2 full chains
    # new ... old
    # f
    # i, f
    # i, i, f
    # f, i, i, f
    # i, f, i, i, f
    #
    # First 2 full backup chains, we can start deleting the older chain
    # new ... old
    # i, i, f,          [>>] i, i, f [<<]
    # f, i, i, f,       [>>] i, i, f [<<]
    # i, f, i, i, f,    [>>] i, i, f [<<]
    #
    # 3 full chains, e.g. if delete process didn't run before
    # This generally won't happen, as the backups will be deleted earlier
    # new ... old
    # i, i, f,          [>>] i, i, f, i, i, f [<<]
    # f, i, i, f,       [>>] i, i, f, i, i, f [<<]
    # i, f, i, i, f,    [>>] i, i, f, i, i, f [<<]

    # See unit tests for the process
    newest_backups_first = list(reversed(history.all))
    for index, backup in enumerate(newest_backups_first):
        if backup.type == BackupType.FULL.value and index + 1 >= chain_size:
            return list(newest_backups_first[index + 1:])

    # This shouldn't happen (we have 2 full chains), log error if it does
    print('ERROR: cannot find deletable backups')
    print('Check if backups are only incremental, we also need full backups')
    print(f'Backup size: {len(backup.all)}')
    return None


def delete_backups(history: BackupInfoHistory, table: ClickhouseBackupTable,
                   ssm_ops: SsmOps, options: dict):
    """Delete local and remote backups

    Parameters
    ----------
    backup : BackupInfo
        info about the backup
    backup : BackupInfoHistory
        history of backups
    table : ClickhouseBackupTable
        DynamoDb table
    ssm_ops : SsmOps
        instance of ssm operations
    options : dict
        backup options
    """
    # No history in the database - no need to do anything
    if not history or not history.all:
        return

    # Check if there are local backups that can be removed
    items = ssm_ops.clickhouse_backup_list(options)
    local_backups = list(filter(lambda x: x.location == 'local', items))
    if len(local_backups) > 0:
        print('==> Delete local backups')
        print(f'About to drop {len(local_backups)} local backups')
        for x in local_backups:
            print(f'Deleting (local): {x.name}')
            resp = ssm_ops.clickhouse_backup_delete(x.name, 'local', options)
            print(f'Resp: {resp}')
    else:
        print('No local backups can be deleted')

    # Check if there are remote backups that can be removed
    chain_size = int(options['max_backups_in_chain'])
    deletable = get_deletable_backups(history, chain_size)
    if not deletable:
        print('No remote backups can be deleted')
        return

    print('==> Delete remote backups')
    print(f'About to drop {len(deletable)} remote backups')
    for x in deletable:
        print(f'S3 delete: {x.name}')
        try:
            resp = ssm_ops.clickhouse_backup_delete(x.name, 'remote', options)
            print(f'Resp: {resp}')
        except WaiterError as err:
            # We have a record in DynamoDb, but there is no backup in S3
            # Let's ignore this, and delete the record from DynamoDb beneath
            if 'is not found on remote storage' in str(err.last_response):
                print('WARN: Backup exists in DynamoDb but not in S3')
                # Will be deleted from the database in the code below
            else:
                # Something else, we can't handle it
                raise err

        print(f'DynamoDb delete: {x.name}')
        resp = table.delete(x)
        print(f'Deleted: {resp}')

    print('==> Cleanup backups')
    try:
        resp = ssm_ops.clickhouse_backup_cleanup(options)
        print(f'Response: {resp}')
    except Exception as err:
        exception_msg = ExceptionInfo.format(err)
        if "shadow: no such file or directory" in exception_msg:
            # Swallow this exception, no need to raise.
            # Seems like we can ignore this error.
            # See https://stackoverflow.com/q/65629318/706456 and
            # https://dops-git106.fortinet-us.com/fsiem/fsiem_cloud/-/issues/521
            print('This warning may be ignored if it occurs infrequently')
            print(f'Warn: clickhouse cleanup did not succeed: {exception_msg}')
        else:
            print(f'Error: clickhouse cleanup failed: {exception_msg}')
            # Unexpected error, raise the original exception
            raise
