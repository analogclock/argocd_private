import boto3
from sys import argv
from argparse import ArgumentParser
from json import loads
from time import sleep
from fsiem_api_client.util import get_client
from fsiem_api_client.aws.ssm_ops import SsmOps, Ssm
from fsiem_api_client.const import worker_disk_sizes
from fsiem_api_client.services.h5_service import H5_ACTION_TYPE
from fsiem_api_client import ActivationTable


status_test = 'autoscaling:TEST_NOTIFICATION'
status_terminate = 'autoscaling:EC2_INSTANCE_TERMINATING'
status_launch = 'autoscaling:EC2_INSTANCE_LAUNCHING'


class LifecycleHandler:

    def __init__(self, cluster_region: str, portal_region: str, serial_no: str,
                 environment: str, s3_bucket: str, s3_region: str,
                 super_url: str, secret_vm_auth_dict: dict,
                 cognito_url: str) -> None:
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region
        self.serial_no = serial_no
        self.env = environment
        self.cluster_region = cluster_region
        self.ssm_ops = SsmOps(cluster_region, serial_no)
        self.ssm = Ssm(portal_region)
        self.fsiem = get_client(super_url, secret_vm_auth_dict, cognito_url,
                                verify_tls=False)

    def _get_instance_info(self, instance_id: str) -> dict:
        """Get the info for the target instance

        Parameters
        ----------
        instance_id : str
            The ID of the target instance

        Returns
        -------
        dict
            A dict of info about the instance
        """
        workers_info = self.ssm_ops.get_instance_info_id(instance_id,
                                                         worker_disk_sizes)
        if not workers_info:
            raise ValueError(
                f'Could not find info for instance: {instance_id}')
        return workers_info[0]

    def _run_automation(self, doc_name: str, fmon_cust_key: str,
                        automation_role_name: str, instance_id: str):
        """Run the instance setup automation

        Parameters
        ----------
        doc_name : str
            The name of the SSM doc to run the automation with
        fmon_cust_key : str
            The fortimonitor customer key
        automation_role_name : str
            The name of the IAM automation role
        instance_id : str
            The ID of the target instance
        """
        print(f'Triggering instance setup for {instance_id}')
        parameters = {
            'Instance': [instance_id],
            'SerialNo': [self.serial_no],
            'ServerKey': [
                f'{self.serial_no}_{self.env}_agent_ingestion_worker'
            ],
            'CustomerKey': [fmon_cust_key]
        }
        execution_id = self.ssm.start_automation(
            doc_name, parameters, self.cluster_region, automation_role_name)
        status = self.ssm.get_automation_status(execution_id)

        # Ensure that status is successful or failed, otherwise sleep and stay
        # in the while loop
        while (
            status not in self.ssm.status_success) and (
                status not in self.ssm.status_failure):
            status = self.ssm.get_automation_status(execution_id)
            print(f'Waiting for automation {execution_id} to finish')
            sleep(30)

    def terminate_ingestion_worker(self, instance_id: str):
        """Terminate an ingestion worker instance

        Parameters
        ----------
        instance_id : str
            The ID of the target instance
        """
        print(f'Handling termination of instance: {instance_id}')

        worker_info = self._get_instance_info(instance_id)
        self.dns = worker_info['PrivateDnsName']
        self.ip = worker_info['PrivateIpAddress']
        self.disks = worker_info['ClickHouseDiskPaths']

        # Check if worker has already been added to the cluster
        worker_list = self.fsiem.h5.check_old_workers([self.ip])
        if worker_list:
            print(f'Worker {self.ip} has not been added to FSIEM cluster,'
                  ' skipping')
            return

        print(f'Removing worker {instance_id} from FSIEM cluster')
        self.fsiem.h5.clickhouse_worker(
            self.disks, None, self.dns, self.ip, self.s3_bucket,
            self.s3_region, H5_ACTION_TYPE.REMOVE)

    def launch_ingestion_worker(self, doc_name: str, automation_role_name: str,
                                fmon_cust_key: str, instance_id: str):
        """Launch the ingestion worker instance

        Parameters
        ----------
        doc_name : str
            The name of the SSM doc to run the automation with
        automation_role_name : str
            The name of the IAM automation role to run the automation
        fmon_cust_key : str
            The fortimonitor customer key
        instance_id : str
            The ID of the target instance
        """
        print(f'Handling launch of instance: {instance_id}')
        print('Waiting 2 minutes to ensure instance is ready')
        sleep(120)

        worker_info = self._get_instance_info(instance_id)
        self.dns = worker_info['PrivateDnsName']
        self.ip = worker_info['PrivateIpAddress']
        self.disks = worker_info['ClickHouseDiskPaths']

        self._run_automation(doc_name, fmon_cust_key, automation_role_name,
                             instance_id)

        print('Waiting 2 minutes to ensure instance has recovered from reboot')
        sleep(120)

        print(f'Adding worker {instance_id} from FSIEM cluster')
        self.fsiem.h5.clickhouse_worker(
            self.disks, None, self.dns, self.ip, self.s3_bucket,
            self.s3_region, H5_ACTION_TYPE.TEST)
        self.fsiem.h5.clickhouse_worker(
            self.disks, None, self.dns, self.ip, self.s3_bucket,
            self.s3_region, H5_ACTION_TYPE.ADD)


def main(options: dict):
    """Handle lifecycle hooks for worker autoscaling groups

    Parameters
    ----------
    options : dict
        Arguments from ArgumentParser
    """
    queue_name = options['queue_name']
    secret_vm_auth_dict = loads(options['secret_vm_auth'])
    cognito_url = options['cognito_url']
    serial_no = options['serial_no']
    environment = options['environment']
    cluster_region = options['cluster_region']
    portal_region = options['portal_region']
    s3_bucket = options['s3_bucket']
    s3_region = options['s3_region']
    super_url = f'https://{options["super_address"]}'
    activation_table = options['activation_table']
    setup_doc_name = options['setup_doc_name']
    automation_role_name = options['automation_role_name']
    fmon_cust_key = options['fmon_cust_key']

    db = ActivationTable(activation_table, portal_region)
    current_status = db.get_status(serial_no)
    print(f'DynamoDb status for `{serial_no}` is `{current_status}`')
    if current_status != db.complete:
        print(f'Do not run when status is `{current_status}`. Exiting.')
        return

    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs.html
    # Get the service resource
    sqs = boto3.resource('sqs')
    autoscaling = boto3.client('autoscaling')

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName=queue_name)

    # Process messages by printing out body and optional author name
    for message in queue.receive_messages():
        body = loads(message.body)

        # For some reason test notifications have a different field name from
        # regular notifications, so we account for them here
        if 'LifecycleTransition' in body:
            event_type = body['LifecycleTransition']
        elif 'Event':
            event_type = body['Event']
        else:
            print('Could not determine event type, skipping')
            continue
        print(f'Found event type: {event_type}')

        if event_type == status_test:
            print('Dropping test notification')
            message.delete()
            continue

        asg_name = body['AutoScalingGroupName']
        lifecycle_name = body['LifecycleHookName']
        lifecycle_token = body['LifecycleActionToken']
        lifecycle_result = 'CONTINUE'
        instance_id = body['EC2InstanceId']

        ingestion_handler = LifecycleHandler(
            cluster_region, portal_region, serial_no, environment, s3_bucket,
            s3_region, super_url, secret_vm_auth_dict, cognito_url)

        if event_type == status_terminate:
            message.delete()
            ingestion_handler.terminate_ingestion_worker(instance_id)
        elif event_type == status_launch:
            message.delete()
            ingestion_handler.launch_ingestion_worker(
                setup_doc_name, automation_role_name, fmon_cust_key,
                instance_id)
        else:
            print(f'Dropping unmanaged event type: {event_type}')
            message.delete()
            continue

        response = autoscaling.complete_lifecycle_action(
            LifecycleHookName=lifecycle_name,
            AutoScalingGroupName=asg_name,
            LifecycleActionToken=lifecycle_token,
            LifecycleActionResult=lifecycle_result,
            InstanceId=instance_id
        )
        print(response)


def parse_args(args) -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Handles the lifecycle hook for the worker autoscaling '
                   'groups')
    parser = ArgumentParser(description=description)
    parser.add_argument('--queue_name', type=str, required=True,
                        help='The name of the SQS queue to read from')
    parser.add_argument('--super_address', type=str, required=True,
                        help='The address of the Super node')
    parser.add_argument('--secret_vm_auth', type=str, required=True,
                        help=('Credentials from secrets manager to '
                              'authenticate with cognito for JWT auth'))
    parser.add_argument('--cognito_url', type=str, required=True,
                        help='The URL of cognito')
    parser.add_argument('--serial_no', type=str, required=True,
                        help='The serial number of the deployment')
    parser.add_argument('--environment', type=str, required=True,
                        help='The environment of the deployment')
    parser.add_argument('--cluster_region', type=str, required=True,
                        help='The AWS region of the deployment')
    parser.add_argument('--portal_region', type=str, required=True,
                        help='The AWS region of the portal')
    parser.add_argument('--s3_bucket', type=str, required=True,
                        help='The name of the archive S3 bucket')
    parser.add_argument('--s3_region', type=str, required=True,
                        help=('The AWS region where the archive S3 bucket is '
                              'located'))
    parser.add_argument('--activation_table', type=str, required=True,
                        help='The name of the dynamodb table')
    parser.add_argument('--setup_doc_name', type=str, required=True,
                        help='The name of the SSM setup doc name')
    parser.add_argument('--automation_role_name', type=str, required=True,
                        help='The name of the IAM automation role')
    parser.add_argument('--fmon_cust_key', type=str, required=True,
                        help='The fortimonitor customer key')
    return parser.parse_args(args)


if __name__ == '__main__':
    print('Starting')
    config = parse_args(argv[1:])
    main(vars(config))
    print('Done')
