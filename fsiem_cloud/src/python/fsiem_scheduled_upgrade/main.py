import boto3
import threading
import dateutil
from datetime import datetime, timezone
from time import sleep
from argparse import ArgumentParser
from fsiem_api_client import ActivationTable, EventBridge
from fsiem_api_client.aws.ec2 import Ec2
from sched_upgrades_table import SchedUpgradesTable
from status_handler import StatusHandler


status_successes = ['Success', 'CompletedWithSuccess']
status_failures = ['Failed', 'TimedOut', 'Cancelled', 'Rejected',
                   'CompletedWithFailure']
delay_between_automation_checks = 120


def find_pending_upgrades(items: list,
                          sched_table: SchedUpgradesTable) -> list:
    """Find scheduled upgrades that are scheduled for the past, whose status is
    pending, and are therefore due to be upgraded. Upgrades that are scheduled
    for the future will be filtered out

    Parameters
    ----------
    items : list
        A list of all scheduled deployments
    sched_table : SchedUpgradesTable
        Class to interact with the scheduled upgrades table

    Returns
    -------
    list
        A list of all scheduled upgrades that are due for upgrading
    """
    print('Finding scheduled upgrades that are ready for upgrading')
    due_items = []
    for item in items:
        if 'scheduledLocal' in item:
            date_string = item['scheduledLocal']['S']
        else:
            date_string = item['scheduled']['S'] + 'Z'  # assumes UTC datetime

        try:
            # use dateutil to parse by default
            # python doesn't handle 7 decimal places very well in milliseconds
            # pfft - what is this language
            # ^ C# casual
            date = dateutil.parser.isoparse(date_string)
        except ValueError:
            print(f'{item["serialNumber"]["S"]} has an invalid date string: '
                  f'{date_string} and cannot be upgraded')
            continue

        # check if we should run based on UTC comparison of both dates
        if datetime.now(timezone.utc) < date.astimezone(timezone.utc):
            print(f'{item["serialNumber"]["S"]} is scheduled for future date '
                  f'{date_string} and will not be upgraded')
            continue
        if item['status']['S'] != sched_table.status_pending:
            print(f'{item["serialNumber"]["S"]} has status '
                  f'{item["status"]["S"]} and will not be upgraded')
            continue
        due_items.append(item)
    print(f'Found {len(due_items)} {sched_table.status_pending} upgrades that '
          'are scheduled for upgrade')
    return due_items


def check_activation_entry(activation_table: ActivationTable,
                           items: list) -> list:
    """Check the stack entry in the activation table and ensure that the
    deployments that are due to be upgrades have the status Complete and do not
    have the preventUpdate flag set to True

    Parameters
    ----------
    activation_table : ActivationTable
        The class that allows queries against the dynamoDb Activation table
    items : list
        A list of scheduled upgrades

    Returns
    -------
    list
        A list of all scheduled upgrades where the deployment status is
        Complete
    """
    print('Querying activation table to ensure scheduled deployments have '
          'status Complete')
    completed_items = []
    for item in items:
        serial_no = item['serialNumber']['S']
        activation_status = activation_table.get_status(serial_no)
        if activation_status != activation_table.complete:
            print(f'{serial_no} has status {activation_status} and will not '
                  'be upgraded')
        elif 'preventUpdate' in item and item['preventUpdate']['BOOL']:
            print(f'{serial_no} has preventUpdate flag and will not be '
                  'upgraded')
        else:
            completed_items.append(item)
    print(f'Found {len(completed_items)} deployments that are Complete')
    return completed_items


def trigger_deploy(eventbridge: EventBridge, db: ActivationTable,
                   serial_no: str, region: str) -> bool:
    """Trigger deployment update by adding event to eventbridge to trigger the
    deploy containers. Then watch the deployments status and wait until it
    reaches Complete state.

    Parameters
    ----------
    eventbridge : EventBridge
        The class that allows actions through AWS eventbridge
    db : ActivationTable
        The class that allows queries against the dynamoDb Activation table
    serial_no : str
        The serial number of the deployment to update
    region : str
        The region the eventbus is located within

    Returns
    -------
    bool
        True if it reaches Complete state, False if it reaches a fail state or
        this function reached time out
    """
    item = db.get_full_item(serial_no)
    event = eventbridge.get_deploy_event(item)
    eventbridge.send_events([event], region)

    # Check status once a minute for 30 minutes
    for i in range(30):
        sleep(60)
        status = db.get_status(serial_no)
        if status == db.complete:
            print(f'{serial_no} back in {db.complete} state')
            return True
        elif status in db.fail_statuses:
            print(f'{serial_no} in fail state: {status}')
            return False

    # If loop has finished without getting a true or false then we'll say it
    # timed out and put it down as a failure
    print(f'{serial_no} timed out waiting for terraform-updater')
    return False


def get_upgrade_path(upgrade_path: str, table: str, region: str,
                     serial_number: str,
                     sched_table: SchedUpgradesTable) -> dict:
    """Get all the details for the specified upgrade path

    Parameters
    ----------
    upgrade_path : str
        The upgrade path
    table : str
        The name of the upgrades dynamoDB table
    region : str
        The region the dynamoDB table is located
    serial_number : str
        The serial number of the deployments whose status will be updated
    sched_table : SchedUpgradesTable
        Class to interact with the scheduled upgrades table

    Returns
    -------
    dict
        Returns the upgrade path item from the dynamodb table
    """
    print(f'Searching for upgrade path {upgrade_path}, thread '
          f'{threading.get_ident()}')
    client = boto3.client('dynamodb', region_name=region)
    response = client.get_item(
        TableName=table,
        Key={
            'upgradePath': {
                'S': upgrade_path
            }
        }
    )
    try:
        upgrade_path = response['Item']
    except KeyError as e:
        sched_table.update_status(serial_number, upgrade_path,
                                  sched_table.status_failed,
                                  update_end_time=True)
        print(f'Could not find upgrade path {upgrade_path}')
        raise e
    return upgrade_path


def trigger_automation(doc_name: str, worker_keeper_ids: list, super_ids: list,
                       zip_name: str, cluster_region: str, doc_region: str,
                       serial_number: str, worker_sec_group_ids: list,
                       super_sec_group_ids: list, aws_account: str,
                       automation_role_name: str) -> str:
    """Trigger the specified SSM Automation for upgrading FSIEM

    Parameters
    ----------
    doc_name : str
        The name of the automation document to be used
    worker_keeper_ids : list
        A list of the worker and keeper instance IDs
    super_ids : list
        A list of the supers instance IDs
    zip_name : str
        The name of the zip file to use in the upgrade
    cluster_region : str
        The region to run the automation
    doc_region : str
        The region where the doc is held in SSM
    serial_number : str
        The serial number of the deployment which will be upgraded
    worker_sec_group_ids : list
        The ID of the workers ALB security group
    super_sec_group_ids : list
        The ID of the supers ALB security group
    aws_account : str
        The AWS account ID
    automation_role_name : str
        The name of the IAM execution role to be used for the automation

    Returns
    -------
    str
        The automation execution ID
    """
    print(f'Triggering upgrade automation for deployment {serial_number}, '
          f'thread: {threading.get_ident()}')
    client = boto3.client('ssm', region_name=doc_region)
    response = client.start_automation_execution(
        DocumentName=doc_name,
        Parameters={
            'Workers': worker_keeper_ids,
            'Supers': super_ids,
            'File': [zip_name],
            'SecurityGroupIdW': worker_sec_group_ids,
            'SecurityGroupIdS': super_sec_group_ids,
            'SerialNumber': [serial_number],
            'DeploymentRegion': [cluster_region]
        },
        TargetLocations=[
            {
                'Accounts': [aws_account],
                'Regions': [cluster_region],
                'ExecutionRoleName': automation_role_name
            }
        ]
    )
    print(f'Triggered automation {response["AutomationExecutionId"]}, '
          f'thread: {threading.get_ident()}')
    return response['AutomationExecutionId']


def get_automation_status(execution_id: str, region: str) -> str:
    """Get the current status of the automation execution

    Parameters
    ----------
    execution_id : str
        The ID of the automation execution
    region : str
        The region to run the automation

    Returns
    -------
    str
        The status of the automation execution
    """
    print(f'Finding automation status for execution ID {execution_id}, '
          f'thread: {threading.get_ident()}')
    client = boto3.client('ssm', region_name=region)
    response = client.describe_automation_executions(
        Filters=[
            {
                'Key': 'ExecutionId',
                'Values': [execution_id]
            }
        ]
    )
    # 'Pending'|'InProgress'|'Waiting'|'Success'|'TimedOut'|'Cancelling'|'Cancelled'|'Failed'|'PendingApproval'|'Approved'|'Rejected'|'Scheduled'|'RunbookInProgress'|'PendingChangeCalendarOverride'|'ChangeCalendarOverrideApproved'|'ChangeCalendarOverrideRejected'|'CompletedWithSuccess'|'CompletedWithFailure'
    automations = response['AutomationExecutionMetadataList']

    if not automations:
        print(f'Could not find automation ID {execution_id}, thread: '
              f'{threading.get_ident()}')
        return None
    status = automations[0]['AutomationExecutionStatus']
    print(f'Status of automation ID {execution_id} is {status}, thread: '
          f'{threading.get_ident()}')
    return status


def thread_function(scheduled_upgrade: dict, activation_table: ActivationTable,
                    sched_table: SchedUpgradesTable, upgrade_table: str,
                    tables_region: str, automation_role_name: str,
                    event_bus_name: str):
    """Trigger the automation for the upgrade and monitor until it either
    succeeds or fails, then update statuses

    Parameters
    ----------
    scheduled_upgrade : dict
        The entry from the scheduled upgrades table
    activation_table : ActivationTable
        Class to interact with activation table
    sched_table : SchedUpgradesTable
        Class to interact with the scheduled upgrades table
    upgrade_table : str
        The name of the dynamodb upgrades table
    tables_region : str
        The AWS region where the dynamodb tables are located
    automation_role_name: str
        The name of the IAM role to perform the automation
    event_bus_name: str
        The name of the EventBridge event bus

    Raises
    ------
    ValueError
        Unable to find instance IDs for the Super or Workers, or failed
        to find the security groups for the Super or Worker ALB
    """
    eventbridge = EventBridge(event_bus_name)

    serial_number = scheduled_upgrade['serialNumber']['S']
    upgrade_path = scheduled_upgrade['upgradePath']['S']
    upgrade_details = get_upgrade_path(upgrade_path, upgrade_table,
                                       tables_region, serial_number,
                                       sched_table)
    zip_name = upgrade_details['zipName']['S']
    ssm_doc_name = upgrade_details['ssmDocName']['S']

    handler = StatusHandler(serial_number, upgrade_path, sched_table,
                            activation_table)

    # Get cluster region
    region = activation_table.get_deployment_region(serial_number)

    ec2 = Ec2(region)
    super_ids = ec2.get_instance_ids(serial_number, 'super')
    worker_ids = ec2.get_instance_ids(serial_number, 'worker')
    keeper_ids = ec2.get_instance_ids(serial_number, 'keeper')
    worker_keeper_ids = worker_ids + keeper_ids
    worker_sec_group_ids = ec2.get_security_group_ids(
        serial_number, 'worker-alb')
    super_sec_group_ids = ec2.get_security_group_ids(
        serial_number, 'super-alb')

    # Check if any of the lists are empty and if so error out
    if (not worker_ids) or (not super_ids):
        print(f'Worker IDs: {worker_ids}')
        print(f'Super IDs: {super_ids}')
        raise ValueError('List of worker or super instance IDs are empty')

    # Ensure we have found only one security group for each
    if (len(worker_sec_group_ids) != 1) or (len(super_sec_group_ids) != 1):
        print(f'Worker ALB Sec group: {worker_sec_group_ids}')
        print(f'Super ALB Sec group: {super_sec_group_ids}')
        raise ValueError(
            'Either did not find the ALB security group or found too many for'
            f'worker {worker_sec_group_ids} or super {super_sec_group_ids}'
        )

    handler.in_progress()

    # Update the stack by triggering the deploy container
    # This ensures it has the latest terraform applied
    print(f'Running initial deploy update on {serial_number}')
    if not trigger_deploy(eventbridge, activation_table, serial_number,
                          tables_region):
        handler.failure()
        raise ValueError(
            f'Terraform update failed for {serial_number}, upgrade failed'
        )
    print(f'Terraform update succeeded for {serial_number}')

    # Updating status in activation table to UpdateInProgress so other
    # containers leave it alone
    activation_table.update_status(serial_number,
                                   activation_table.update_in_progress)

    aws_account = boto3.client('sts').get_caller_identity().get('Account')

    # Beginning upgrade
    automation_id = trigger_automation(
        ssm_doc_name, worker_keeper_ids, super_ids, zip_name, region,
        tables_region, serial_number, worker_sec_group_ids,
        super_sec_group_ids, aws_account, automation_role_name)

    status = get_automation_status(automation_id, tables_region)

    # Ensure that status is successful or failed, otherwise sleep and stay in
    # the while loop
    while (status not in status_successes) and (status not in status_failures):
        status = get_automation_status(automation_id, tables_region)
        sleep(delay_between_automation_checks)

    print(f'Automation {automation_id} finished with status: {status}')

    # Run deploy container again to reapply CIDRs
    print(f'Running final deploy update on {serial_number}')
    if not trigger_deploy(eventbridge, activation_table, serial_number,
                          tables_region):
        handler.failure()
        raise ValueError(
            f'Terraform update failed for {serial_number}, upgrade failed'
        )

    print(f'Terraform update succeeded for {serial_number}')

    # Updating status of both scheduled upgrade table and activation table
    if status in status_successes:
        handler.success()
    else:
        activation_table.update_status(serial_number,
                                       activation_table.update_failed)
        handler.failure()


def main(options: dict):
    """Finds upgrades scheduled in the dynamoDB table and triggers the ssm
    automation to perform the upgrade
    """
    activation_table = ActivationTable(options['activation_table'],
                                       options['tables_region'])
    sched_table = SchedUpgradesTable(options['scheduled_upgrades_table'],
                                     options['tables_region'])
    upgrades = sched_table.get_all_upgrades()
    upgrades = find_pending_upgrades(upgrades, sched_table)
    upgrades = check_activation_entry(activation_table, upgrades)

    print(f'Upgrading {len(upgrades)} deployments')
    # Split into threads as each upgrade can take > 50 minutes
    threads = []
    for upgrade in upgrades:
        t = threading.Thread(
            target=thread_function,
            args=(upgrade, activation_table, sched_table,
                  options['upgrade_table'], options['tables_region'],
                  options['automation_role_name'], options['event_bus_name'],)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join


def parse_args() -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Finds upgrades scheduled in the dynamoDB table and '
                   'triggers the ssm automation to perform the upgrade')
    parser = ArgumentParser(description=description)
    parser.add_argument('--activation_table', type=str, required=True,
                        help='The name of the dynamoDB activation table')
    parser.add_argument('--scheduled_upgrades_table', type=str,
                        help=('The name of the dynamoDB scheduled upgrades '
                              'table'), required=True)
    parser.add_argument('--upgrade_table', type=str, required=True,
                        help='The name of the dynamoDB upgrade table')
    parser.add_argument('--tables_region', type=str, required=True,
                        help=('The aws region where the dynamoDB tables are '
                              'located'))
    parser.add_argument('--automation_role_name', type=str, required=True,
                        help=('The name of the IAM role to perform the '
                              'automation'))
    parser.add_argument('--event_bus_name', type=str, required=True,
                        help='The name of the EventBridge event bus')
    return parser.parse_args()


if __name__ == '__main__':
    config = parse_args()
    main(vars(config))
