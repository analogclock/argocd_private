import sys
from dataclasses import dataclass
from argparse import ArgumentParser
from fsiem_api_client import ActivationTable
from fsiem_api_client.aws.ses import Ses
from fsiem_api_client.aws.ssm_ops import SsmOps
from fsiem_api_client.clickhouse_backup_table import BackupInfoHistory
from backup import delete_backups, get_backup_options_table, \
    get_backup_table, run_backup


START_SEQUENCE_NUMBER = 1


@dataclass
class PermissionToRun:
    can_run: bool   # Do we have permissions to run
    reason: str     # Explanation for the decision


def should_run(status: str, is_backup_running: bool, is_restore_running: bool,
               backup_enabled: bool) -> PermissionToRun:
    """Check if backup should run, a logical decision tree.

    To allow running we need all of these to be true:
    - Stack status is Complete
    - No other backups or restores are currently running
    - The previous backup happened more than 24 hours ago

    Parameters
    ----------
    status : str
        Stack status from the activation table
    is_backup_running : bool
        A bool value from the activation table, is another backup running
    is_restore_running : bool
        A bool value from the activation table, is another restore running
    backup_enabled: bool
        A flag to indicate if backups are enabled or not

    Returns
    -------
    PermissionToRun
        Decision of whether to allow backup to run or not. Also contains
        text explanation for the decision.
    """
    # Current status must be Complete
    if status != ActivationTable.complete:
        return PermissionToRun(False, f'Do not run when status is {status}')

    # Check if another backup is running
    if is_backup_running:
        return PermissionToRun(False, 'Another backup is running')

    # Check if another restore is running
    if is_restore_running:
        return PermissionToRun(False, 'Another restore is running')

    if not backup_enabled:
        return PermissionToRun(
            False, 'isBackupEnabled flag is False or not present in DynamoDB')

    return PermissionToRun(True, None)


def check_if_execution_allowed(db: ActivationTable, options: dict,
                               history: BackupInfoHistory | None):
    """Check status of the stack.

       We will only run when status is _complete_, for any other status
       we exit the current application with exit code 0.
       """

    sn = options['serial_number']
    status = db.get_status(sn)
    is_backup_running = db.get_is_backup_running(sn)
    is_restore_running = db.get_is_restore_running(sn)

    # By default, run the backup if this value is not present in the database,
    # assume it is True.
    is_backup_enabled = db.get_is_backup_enabled(sn) or True
    decision = should_run(status, is_backup_running, is_restore_running,
                          is_backup_enabled)
    if not decision.can_run:
        print(decision.reason)
        print('Exiting...')
        exit(0)


def main(options: dict):
    """Runs ClickHouse backup command"""
    sn = options['serial_number']
    activation_table = ActivationTable(
        options['dynamodb_activation_table'],
        options['dynamodb_region'])

    ssm_ops = SsmOps(options['region'], sn)
    backup_table = get_backup_table(options)

    backup_options_table = get_backup_options_table(options)

    print('Pull the history of previous backups')
    history = backup_table.get_backup_history(sn)

    check_if_execution_allowed(activation_table, options, history)

    # Ses requires some setup, we only did it for one region us-east-1
    ses = Ses('us-east-1')

    try:
        print('Set backup is running to true in activation table')
        activation_table.set_is_backup_running(sn, True)

        print('Starting a backup')
        run_backup(history, backup_table, backup_options_table,
                   ssm_ops, options, ses)

        print('Delete previous old backups')
        # Get new history, we just ran a new backup
        history = backup_table.get_backup_history(sn)
        delete_backups(history, backup_table, ssm_ops, options)
    except Exception as err:
        print(f'Error: backup failed {err}')
        desc = f'''
        SSM task to execute backup.
        Options: {str(options)}
        '''
        ses.send_email_task_failed(f'main backup {options["serial_number"]}',
                                   desc, err,
                                   options['email_from_addr'],
                                   options['email_to_addr'])
    finally:
        print('Set backup is running to false in activation table')
        activation_table.set_is_backup_running(sn, False)


def parse_args(args) -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Retrieves a license and inserts it into the fsiem super')
    parser = ArgumentParser(description=description)
    parser.add_argument('--serial_number', type=str, required=True,
                        help='The serial number of this deployment')
    parser.add_argument('--region', type=str, required=True,
                        help='The deployment region of the stack')
    parser.add_argument('--dynamodb_region', type=str, required=True,
                        help='The region of the dynamodb tables')
    parser.add_argument('--dynamodb_backup_table', type=str, required=True,
                        help='The name of the dynamodb table')
    parser.add_argument('--dynamodb_backup_options_table', type=str,
                        required=True,
                        help='The name of the dynamodb backup options table')
    parser.add_argument('--dynamodb_activation_table', type=str, required=True,
                        help='The name of the dynamodb activation table')
    parser.add_argument('--s3_bucket', type=str, required=True,
                        help='S3 bucket')
    parser.add_argument('--s3_path', type=str, required=True,
                        help='S3 folder(s) inside the bucket')
    parser.add_argument('--remote_storage', type=str, required=False,
                        help='Type of remote storage', default="s3")
    parser.add_argument('--log_level', type=str, required=False,
                        help='ClickHouse log level', default="warn")
    parser.add_argument('--s3_compression_level', type=str, required=False,
                        help='How much to compress data, 1 - no compression',
                        default="1")
    parser.add_argument('--s3_compression_format', type=str, required=False,
                        help='Compression algorithm, e.g. tar', default="tar")
    parser.add_argument('--s3_use_custom_storage_class', type=str,
                        required=False, default="false",
                        help='Use a custom storage class')
    parser.add_argument('--s3_storage_class', type=str, required=False,
                        help='S3 storage class', default="STANDARD")
    parser.add_argument('--s3_concurrency', type=str, required=False,
                        help='Number of concurrent processes', default="1")
    parser.add_argument('--s3_debug', type=str, required=False,
                        help='Print out requests and responses for S3 calls',
                        default="false")
    parser.add_argument('--max_backups_in_chain', type=int, required=False,
                        help='Count of full and incremental backups',
                        default=3)
    parser.add_argument('--email_from_addr', type=str, required=False,
                        help='The FROM email address for email notifications')
    parser.add_argument('--email_to_addr', type=str, required=False,
                        help='The TO email address for email notifications')
    return parser.parse_args(args)


if __name__ == '__main__':
    # Usage: python3 main.py --serial_number 123 <plus other args>
    # See unit and integration tests for working examples
    config = parse_args(sys.argv[1:])
    print(f'Running backup, with args: {str(config)}')
    main(vars(config))
    print('Done')
