
import logging
import sys
from json import loads
from time import sleep
from argparse import ArgumentParser
from net_ops import strip_https
from fsiem_api_client.const import (phmonitor_delay_sec, super_disk_sizes,
                                    worker_disk_sizes,
                                    keeper_disk_sizes)
from fsiem_api import (set_deployment_type_to_cloud,
                       event_query_worker_setup, set_version_db,
                       clickhouse_super_setup, clickhouse_worker_setup,
                       clickhouse_config, app_server_mem_setup,
                       clickhouse_archive_setup, clickhouse_has_new_workers)
from fsiem_api_client.aws.ec2 import Ec2
from fsiem_api_client import ActivationTable
from fsiem_api_client.util import get_client
from fsiem_api_client.services.worker_service import WORKER_TYPE
from fsiem_api_client.exceptions import UnauthorizedHttpError
from storage import expand_fs_worker_disks


# log to standard out, default log level is WARNING
logging.basicConfig(stream=sys.stdout, level=logging.WARN)


def main(super_addr: str, secret_vm_auth: str, cognito_url: str,
         clickhouse_s3_bucket: str, clickhouse_s3_region: str,
         new_password: str, worker_url: str, email: str, serial_no: str,
         dynamodb_table: str, dynamodb_region: str, app_server_mem_gb: int):
    """First time FSIEM setup for the storage, admin password, and workers

    Parameters
    ----------
    super_addr: str
        The address of the super node
    secret_vm_auth: str
        Credentials from secrets manager to authenticate with cognito for JWT
        auth
    cognito_url: str
        The URL of cognito
    new_password: str
        The new password for the default admin account
    worker_url: str
        The URL of the workers load balancer
    email: str
        The email address of the user/customer who triggered deployment
    serial_no: str
        The serial number of the deployment
    dynamodb_table: str
        The name of the dynamodb table that stores the status of deployments
    dynamodb_region: str
        The aws region the dynamodb table is located
    app_server_mem_gb: int
        The JVM memory to be assigned to the app server service, in GB
    """
    try:
        secret_vm_auth_dict = loads(secret_vm_auth)
        db = ActivationTable(dynamodb_table, dynamodb_region)
        current_status = db.get_status(serial_no)
        print(f'DynamoDb status for `{serial_no}` is `{current_status}`')

        region = db.get_deployment_region(serial_no)

        if current_status != db.setup_initializing:
            print(f'Do not run when status is `{current_status}`. Exiting.')
            return

        super_url = f'https://{super_addr}'
        print(f'==> Testing connection to FSIEM VM API: `{super_url}`')
        fsiem = get_client(super_url, secret_vm_auth_dict, cognito_url,
                           verify_tls=False)
        if not fsiem:
            print('Connection cannot be established to FSIEM API')
            return

        print(f'==> Updating status to: `{db.setup_in_progress}`')
        db.update_status(serial_no, db.setup_in_progress)

        print('Waiting for phMonitor to restart after license upload...')
        sleep(phmonitor_delay_sec)

        print('==> Getting the IP addresses of running workers')
        ec2 = Ec2(region=region)
        worker_ips = ec2.get_instance_ips(serial_no, 'worker')
        worker_ips.extend(ec2.get_instance_ips(serial_no, 'keeper'))

        # TODO: Refactor me to use retry inside the HttpClient
        # This loop ensures that if authentication times out then it will retry
        # The steps will be skipped if they have already been setup
        while True:
            try:
                print('==> Configuring VM UI for cloud deployment')
                set_deployment_type_to_cloud(fsiem)

                has_new_workers = clickhouse_has_new_workers(
                    fsiem, worker_disk_sizes, worker_ips)
                # Only configure once, or when there is a new worker
                if has_new_workers:
                    print('==> Configuring ClickHouse database')
                    region = db.get_deployment_region(serial_no)
                    print(f'Super known disks sizes:  {super_disk_sizes}')
                    print(f'Worker known disks sizes: {worker_disk_sizes}')
                    print(f'Keeper known disks sizes: {keeper_disk_sizes}')
                    clickhouse_super_setup(fsiem, super_disk_sizes, region,
                                           serial_no, new_password, email)
                    clickhouse_archive_setup(fsiem, clickhouse_s3_bucket,
                                             clickhouse_s3_region)
                    clickhouse_worker_setup(fsiem, worker_disk_sizes,
                                            keeper_disk_sizes, region,
                                            serial_no, worker_ips,
                                            clickhouse_s3_bucket,
                                            clickhouse_s3_region)
                    clickhouse_config(fsiem, super_disk_sizes,
                                      worker_disk_sizes, keeper_disk_sizes,
                                      region, serial_no, clickhouse_s3_bucket,
                                      clickhouse_s3_region)

                # File system expansion
                print('==> Trying expanding ClickHouse file system on workers')
                expand_fs_worker_disks(region, serial_no)

                # Query worker config
                print('==> Configuring event query workers')
                worker_url = strip_https(worker_url)
                event_query_worker_setup(fsiem, worker_url, WORKER_TYPE.EVENT)

                # Save VM version in db
                print('==> Updating VM version in the DynamoDb')
                set_version_db(fsiem, db, serial_no)
                break
            except UnauthorizedHttpError as e:
                print(e)
                print('Authentication timed out, retrying')
                fsiem = get_client(super_url, secret_vm_auth_dict, cognito_url,
                                   verify_tls=False)

        print('==> Updating AppServer Memory')
        app_server_mem_setup(region, serial_no, app_server_mem_gb)

        print(f'==> Updating status to: `{db.complete}`')
        db.update_status(serial_no, db.complete)
        print('All work is done')
    except Exception as e:
        print('An error has occurred, see details below:')
        print(e)

        # Something failed, update database status to FAILED
        db.update_status(serial_no, db.create_failed)
        # This will propagate error back to runtime which results in an
        # failed application exit code
        raise


def parse_args() -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('First time FSIEM setup for the storage, admin password, '
                   'and workers')
    parser = ArgumentParser(description=description)
    parser.add_argument('--super', type=str, required=True,
                        help='The address of the Super node')
    parser.add_argument('--secret_vm_auth', type=str, required=True,
                        help=('Credentials from secrets manager to '
                              'authenticate with cognito for JWT auth'))
    parser.add_argument('--cognito_url', type=str, required=True,
                        help='The URL of cognito')
    parser.add_argument('--clickhouse_s3_bucket', type=str, required=True,
                        help='Bucket name where to store archive data')
    parser.add_argument('--clickhouse_s3_region', type=str, required=True,
                        help='S3 bucket region')
    parser.add_argument('--new_password', type=str, required=True,
                        help='The new password for admin account')
    parser.add_argument('--worker_url', type=str, required=True,
                        help='The URL of the workers load balancer')
    parser.add_argument('--email', type=str, required=True,
                        help='The email address for admin account')
    parser.add_argument('--serial_number', type=str, required=True,
                        help='The serial number of this deployment')
    parser.add_argument('--dynamodb_table', type=str, required=True,
                        help='The name of the dynamodb table')
    parser.add_argument('--dynamodb_region', type=str, required=True,
                        help='The region of the dynamodb table')
    parser.add_argument('--app_server_mem_gb', type=int, required=True,
                        help=('The JVM memory to be assigned to the app server'
                              'service, in GB'))
    return parser.parse_args()


if __name__ == '__main__':
    # Usage: python3 main.py --super 54.1.1.1
    # --secret_vm_auth arn:aws:s:a:1234:secret:licensing-creds-playground
    # --cognito_url https://cognito-idp.us-east-1.amazonaws.com/...
    # --clickhouse_s3_bucket bucket_name
    # --clickhouse_s3_region: us-east-1
    # --new_password test1234
    # --worker_url https://worker.fortisiem.cloud --email test@test.com
    # --serial_number fsiem1234 --dynamodb_table fsiem_activation_table_dev
    # --dynamodb_region us-east-1 --app_server_mem_gb 5

    print('Running setup task')
    config = parse_args()
    main(config.super, config.secret_vm_auth, config.cognito_url,
         config.clickhouse_s3_bucket, config.clickhouse_s3_region,
         config.new_password, config.worker_url,
         config.email, config.serial_number, config.dynamodb_table,
         config.dynamodb_region, config.app_server_mem_gb)
    print('Finished setup task')
