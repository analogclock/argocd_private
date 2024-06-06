from argparse import ArgumentParser
from fsiem_api_client.aws.ssm_ops import SsmOps
from datetime import datetime
from fsiem_api_client.validator import Validator
from fsiem_api_client.external_storage_table import ExternalStorageTable
from fsiem_api_client.external_storage_status_table \
    import ExternalStorageStatusTable
from constants import FAILED_STATUS, PASSED_STATUS, IN_PROGRESS_STATUS
from botocore.exceptions import WaiterError


def get_current_datetime():
    # Get the current date and time
    datetime_string = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    return datetime_string


def get_cleanup_size(size_limit: int, cur_size: int, buffer: int) -> int:
    """The size of the data to be cleaned up

    Parameters
    ----------
    size_limit : int
        The max size we want to be stored
    cur_size     : int
        The current used size
    buffer : int
        Additional buffer to added to calculation so we do not start deleted as
        soon as limit is breached, but instead wait a little longer

    Returns
    -------
    int
        The amount of data that needs to be deleted. Positive if we need to
        delete data, negative, if there is still free space and no need to
        delete data
    """
    # Example:
    # size_limit: 500
    # buffer: 20
    # size: 571

    # 520 = 500 + 20
    buffered_size = size_limit + buffer

    # 51 = 571 - 520
    cleanup_size = cur_size - buffered_size

    # 51
    return cleanup_size


def parse_error_msg(input_str: str) -> str:
    # Find the index of "An error occurred" and "failed to run commands"
    start_index = input_str.find("An error occurred")
    end_index = input_str.find("failed to run commands")

    # Extract the error message
    error_message = input_str[start_index:end_index].strip()

    # Print the extracted error message
    print("Error message after parsing:", error_message)

    # Check if error_message is None
    if error_message is None:
        error_message = 'Data transfer failed for unknown reason'

    return error_message


def clickhouse_find_deletable_items(partition_dict: dict[str:int],
                                    cleanup_size: int) -> list[str]:
    """Return items that we need to delete.

    Given needed cleanup size, this method iterates over available sorted
    partition dictionary and calculates which partitions we need to delete.

    Parameters
    ----------
    partition_dict : dict[str:int]
        Dictionary partition name -> partition size.
    cleanup_size : int
        Size in bytes required to be deleted

    Returns
    -------
    int
        List of partition names we need to delete. For example, given 10 items
        in a dictionary, we can delete the oldest 3 to free the desired size.
    """
    max = 0
    result = []
    for key in sorted(partition_dict):
        result.append(key)
        max += partition_dict[key]
        if max > cleanup_size:
            break
    return result


def is_valid_external_storage(external_storage_dest: str) -> bool:
    """Check if the s3 bucket name used for external storage is valid

    Parameters
    ----------
    external_storage_dest : str
        s3 bucket name for external storage

    Returns
    -------
    bool
        True or False base on the validity of the s3 bucket name
    """
    print(external_storage_dest)
    validate = Validator()

    if (validate.is_valid_s3_bucket_prefix(external_storage_dest)):
        # Split the path into bucket name and bucket prefix
        result = external_storage_dest.split('/', 1)
        bucket_name = result[0]
        if (validate.is_valid_s3_bucket_name(bucket_name)):
            return True
    return False


def copy_data_org_id_ext_storage(sn: str, region: str, org_id: int,
                                 ext_storage: str, ssm_ops: SsmOps,
                                 items: list[str], db: ExternalStorageTable,
                                 external_storage_table: str,
                                 dynamodb_region: str,
                                 dbs: ExternalStorageStatusTable,
                                 external_storage_status_table: str):
    """Copy the data to an external storage

    Parameters
    ----------
    sn : str
        serial number of the stack
    region : str
        region where stack is deployed
    org_id : int
        organization id
    ext_storage : str
        s3 bucket name for external storage
    ssm_ops : SsmOps
        instance of ssm operations
    items : list[str]
        list of partitions from which data is copied
    db : ExternalStorageTable
        instance of external storage table
    external_storage_table : str
        name of the dynamodb table for external_storage
    dynamodb_region : str
        name of the dynamodb region where external_storage table is present
    dbs : ExternalStorageStatusTable
        instance of external storage status table
    external_storage_status_table : str
        name of the dynamodb table for external_storage status
    """

    # Check if the s3 bucket prefix and bucket name are valid
    if (is_valid_external_storage(ext_storage)):
        # Clickhouse query to move the archive data to customers s3 bucket
        ssm_ops = SsmOps(region, sn)
        # Calculate the no of records in events replicated table for
        # the given customer_id
        resp = ssm_ops.clickhouse_count_external_storage_records(
            org_id, items)
        count = int(resp.output)
        error_message1 = resp.error
        if error_message1:
            print(f'Error in getting record count: {error_message1}')
            return
        print(f'No of records in the events replicated table for '
              f'org_id {org_id}, count is {count}')
        if count == 0:
            # Copy clickhouse archive data to external storage is successful
            print('No records available to copy to external storage')

            return
        print(f'External storage destination: '
              f'{org_id} : {ext_storage}')
        db = ExternalStorageTable(external_storage_table, dynamodb_region)
        dbs = ExternalStorageStatusTable(external_storage_status_table,
                                         dynamodb_region)
        last_update = get_current_datetime()
        last_status = IN_PROGRESS_STATUS
        status_message = "Data transfer is in progress"
        data_transferred = 0
        db.update_external_storage_table(sn, org_id, last_update, last_status,
                                         status_message, data_transferred)
        try:
            start_datetime = get_current_datetime()
            total_bytes_copied = 0
            i = 0
            # Iterate over each partition
            for item in items:
                i += 1
                print(f"Each item in the partition: {item}")
                file_format = 'Parquet'
                file_name = f"{sn}_{get_current_datetime()}_part{i}"
                print(f'File to be copied to external_storage: '
                      f'{file_name}')
                result = ssm_ops.clickhouse_copy_to_external_storage(
                    org_id, ext_storage, item, file_name, file_format)
                response_code = result[0].response_code
                # output of the pipeline viewer (pv) command is the amount of
                # data transferred to s3 bucket and it will be available in
                # the standard error from ssm send command
                error_message2 = result[0].error
                bytes_copied = error_message2
                print(f'Response code: {response_code}')
                print(f'Bytes copied (from std error): {error_message2}')
                # In case copy clickhouse archive data to external storage
                # fails, status will be updated as failed

                # checking response code from ssm execution to make sure
                # there is a failure as we will always have a value
                # for error message with bytes transferred
                if (response_code != 0):
                    print(f'Clickhouse data copy to external storage failed: '
                          f'{error_message2}')
                    last_update = get_current_datetime()
                    last_status = FAILED_STATUS
                    data_transferred = 0
                    print(f'Updating external storage table: {sn}, {org_id},'
                          f'{last_update}, {last_status}, {error_message2},'
                          f'{data_transferred}')
                    db.update_external_storage_table(sn, org_id,
                                                     last_update,
                                                     last_status,
                                                     error_message2,
                                                     data_transferred)
                    return
                # Copy clickhouse archive data to external storage is
                # successful
                print('Successfully copied clickhouse data to \
                       external storage')
                last_update = get_current_datetime()
                last_status = PASSED_STATUS
                status_message = "Data transfer complete"
                print(f'Updating external storage table: {sn}, {org_id},'
                      f'{last_update}, {last_status}, {status_message},'
                      f'{bytes_copied}')
                total_bytes_copied += int(bytes_copied)
                db.update_external_storage_table(sn, org_id, last_update,
                                                 last_status, status_message,
                                                 total_bytes_copied)
                print(f'Updating external storage status table: {sn}, {org_id}'
                      f'{start_datetime}, {last_update}, {bytes_copied}')
                dbs.update_external_storage_status_table(sn, org_id,
                                                         start_datetime,
                                                         last_update,
                                                         total_bytes_copied)
        except WaiterError as e:
            # Handle other exceptions like WaiterError
            print(f'An error occurred during copy to external_storage: {e}')
            last_update = get_current_datetime()
            last_status = FAILED_STATUS
            data_transferred = 0
            error_response = e.last_response
            if 'StandardErrorContent' in error_response:
                standard_error_content_str =  \
                    error_response['StandardErrorContent']
                status_message = parse_error_msg(standard_error_content_str)
            else:
                print("No 'StandardErrorContent' found in error response")
                status_message = 'Data transfer failed due to unknown reason'

            print(f'Updating external storage table: {sn}, {org_id}'
                  f'{last_update}, {last_status}, {status_message},'
                  f'{data_transferred}')
            db.update_external_storage_table(sn, org_id, last_update,
                                             last_status, status_message,
                                             data_transferred)

            return
    else:
        print(f"Not a valid external storage : {ext_storage}")


def external_storage_copy_all(sn: str, region: str,
                              external_storage_dests: dict,
                              ssm_ops: SsmOps, items: list[str],
                              db: ExternalStorageTable,
                              external_storage_table: str,
                              dynamodb_region: str,
                              dbs: ExternalStorageStatusTable,
                              external_storage_status_table: str):
    """Copy the data to all external storages defined in a stack

    Parameters
    ----------
    sn : str
        serial number of the stack
    region : str
        region where stack is deployed
    external_storage_dests :  dict
        dictionary of organization id's and external storage names
    ssm_ops : SsmOps
        instance of ssm operations
    items : list[str]
        list of partitions from which data is copied
    db : ExternalStorageTable
        instance of external storage table
    external_storage_table : str
        name of the dynamodb table for external_storage
    dynamodb_region : str
        name of the dynamodb region where external_storage table is present
    dbs : ExternalStorageStatusTable
        instance of external storage status table
    external_storage_status_table : str
        name of the dynamodb table for external_storage status
    """

    for item in external_storage_dests:
        external_storage_dest = item.get('externalStorageDest', {}).get('S')
        organization_id = int(item.get('organizationId', {}).get('N', 0))
        print(f"External Storage Destination: "
              f"{external_storage_dest}, Organization ID: {organization_id}")
        copy_data_org_id_ext_storage(sn, region, organization_id,
                                     external_storage_dest, ssm_ops, items,
                                     db, external_storage_table,
                                     dynamodb_region, dbs,
                                     external_storage_status_table)


def main(sn: str, region: str, size_limit_gb: int, buffer_gb: int,
         external_storage_table: str, dynamodb_region: str,
         external_storage_status_table: str):
    """Gets size of EFS or ClickHouse data and delete (oldest first),
    until the size is once again beneath the limit

    Parameters
    ----------
    sn : str
        Serial number of the deployment
    region : str
        The AWS region the deployment is located in
    size_limit_gb : int
        The max size we want to be stored
    buffer_gb : int
        Additional buffer to added to calculation so we do not start deleting
        as soon as limit is breached, but instead wait a little longer
    external_storage_table : str
        name of the dynamodb table for external_storage
    dynamodb_region : str
        name of the dynamodb region where external_storage table is present
    external_storage_status_table : str
        name of the dynamodb table for external_storage status
    """
    # clickhouse_cleanup(sn, region, size_limit_gb, buffer_gb)
    size_limit = size_limit_gb * 1024 * 1024 * 1024
    buffer = buffer_gb * 1024 * 1024 * 1024
    # Retrieve external storage destination bucket names
    db = ExternalStorageTable(external_storage_table, dynamodb_region)
    dbs = ExternalStorageStatusTable(external_storage_status_table,
                                     dynamodb_region)
    external_storage_dests = db.get_external_storage_dests(sn)
    print(f'External storage: {external_storage_dests}')
    ssm_ops = SsmOps(region, sn)
    size = ssm_ops.clickhouse_archive_size()
    cleanup_size = get_cleanup_size(size_limit, size, buffer)

    print("How much storage did the customer buy?")
    print(f'Size limit (from command line): {size_limit_gb} GB ({size_limit} bytes)')  # noqa

    print("How much actual storage is used by Clickhouse on the disks?")
    print(f'Clickhouse archive size: {size / 1024 / 1024 / 1024} GB ({size} bytes)')  # noqa

    print("If we need to delete extra space, how much to delete?")
    print(f'Buffer (extra storage to clean up): {buffer_gb} GB ({buffer} bytes)')  # noqa

    # If we run cleanup, the algorithm is like this:
    # - Get total size they bought (say 500 GB)
    # - Add extra allowance to that size (20 GB)
    # - Get actual space used by clickhouse (say 571 GB)
    # - The cleanup size will become:
    #        500 + 20 = 520 GB (purchased size + buffer)
    #        571 - 520 = 51 GB (minimal space to clean up, could be more
    #                           if last deleted partition size is large)
    print(f'Cleanup size : {cleanup_size / 1024 / 1024 / 1024} GB ({cleanup_size} bytes)')  # noqa

    # if data does not exceed limit + buffer then exit
    if cleanup_size < 0:
        print(f'Current size of ClickHouse S3 archive ({size} bytes) '
              f'does not exceed the limit {cleanup_size}. Exiting.')
        return
    print('ClickHouse size exceeds the limit, will delete oldest data')
    partition_dict = ssm_ops.clickhouse_oldest_data()
    print(f'Candidate partition->size dictionary: {partition_dict}')
    items = clickhouse_find_deletable_items(partition_dict, cleanup_size)
    print(f'Partitions:{items}')
    if not items:
        print('There are no partitions to delete')
        return  # Return if the list is empty
    if external_storage_dests:
        # Copy clickhouse archive data to external storage failure
        # Delete items will not be done
        external_storage_copy_all(sn, region,
                                  external_storage_dests, ssm_ops, items,
                                  db, external_storage_table,
                                  dynamodb_region, dbs,
                                  external_storage_status_table)
    else:
        print('No storage provided by customer for copying data.')

    print(f'Deleting these partitions: {items}')
    ssm_ops.clickhouse_delete_partitions(items)
    print('Partitions were successfully deleted')


def parse_args() -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Trims data with respect to allocated licence')
    parser = ArgumentParser(description=description)
    parser.add_argument('--sn', type=str, required=False,
                        help='Serial number of the deployment')
    parser.add_argument('--region', type=str, required=False,
                        help='Deployment region')
    parser.add_argument('--size_limit_gb', type=int, required=True,
                        help='The size limit in bytes')
    parser.add_argument('--buffer_gb', type=int, required=True,
                        help=('The buffer over the size limit before deleting,'
                              ' in bytes'))
    parser.add_argument('--dynamodb_ext_st_table', type=str, required=True,
                        help='The name of the dynamodb external storage table')
    parser.add_argument('--dynamodb_region', type=str, required=True,
                        help='The region of the dynamodb table')
    parser.add_argument('--dynamodb_ext_st_status_table', type=str,
                        required=True, help='The region of the dynamodb table')
    return parser.parse_args()


if __name__ == '__main__':
    # Usage: python3 main.py
    print('Running storage enforcer')
    config = parse_args()
    print(f'Parsed arguments: {config}')
    main(config.sn, config.region, config.size_limit_gb, config.buffer_gb,
         config.dynamodb_ext_st_table, config.dynamodb_region,
         config.dynamodb_ext_st_status_table)
