import boto3
from os import environ
from jinja2 import Template, StrictUndefined
from enum import Enum
from datetime import datetime, timezone
from dateutil.parser import isoparse
from fsiem_api_client import ActivationTable
from fsiem_api_client.aws.ses import Email, Ses


class STATUS_TYPE(Enum):
    SUCCESS = 'Complete'
    FAILURE = 'Failed'
    IN_PROGRESS = 'InProgress'
    PENDING = 'Pending'


def get_upgrade_path(upgrade_path: str, table: str, region: str) -> dict:
    """Get all the details for the specified upgrade path

    Parameters
    ----------
    upgrade_path : str
        The upgrade path
    table : str
        The name of the upgrades dynamoDB table
    region : str
        The region the dynamoDB table is located

    Returns
    -------
    dict
        Returns the upgrade path item from the dynamodb table
    """
    print(f'Searching for upgrade path {upgrade_path}')
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
        print(f'Could not find upgrade path {upgrade_path}')
        print(e)
        upgrade_path = {}
    return upgrade_path


def activation(record: dict, environment: str) -> tuple[str, str]:
    """Creates message and subject for email about deployment failures recorded
    in the activation dynamodb table

    Parameters
    ----------
    record : dict
        The record received from the dynamodb record
    environment : str
        The environment the function and dynamodb tables are located in

    Returns
    -------
    tuple[str, str]
        A Tuple of the Subject and Message of the email to send
    """
    print('Event is from the activation table')
    if environment == 'playground':
        print('Event is for playground. Will not send activation '
              'email to avoid spam')
        return None, None
    if record['eventName'] != 'MODIFY':
        print(f'Ignoring messages with status: {record["eventName"]}')
        return None, None
    status = record['dynamodb']['NewImage']['status']['S']
    serial_no = record['dynamodb']['NewImage']['serialNumber']['S']
    region = record['dynamodb']['NewImage']['region']['S']
    email = record['dynamodb']['NewImage']['deploymentEmail']['S']
    target_status = ['CreateFailed', 'DeleteFailed', 'UpdateFailed']
    if status not in target_status:
        print(f'Ignoring status: {status}')
        return None, None

    subject = f'FSIEMCloud {environment}: {serial_no} is {status}'
    message = (
        f'Serial Number: {serial_no}\n'
        f'Environment: {environment}\n'
        f'Region: {region}\n'
        f'Status: {status}\n'
        f'Email: {email}\n'
    )
    return subject, message


def poc_approval(record: dict, environment: str) -> tuple[str, str]:
    """Creates message and subject for email about new entries in the POC
    approval dynamoDB table

    Parameters
    ----------
    record : dict
        The record received from the dynamodb record
    environment : str
        The environment the function and dynamodb tables are located in

    Returns
    -------
    tuple[str, str]
        A Tuple of the Subject and Message of the email to send
    """
    if record['eventName'] != 'INSERT':
        print(f'Ignoring messages with status: {record["eventName"]}')
        return None, None
    serial_no = record['dynamodb']['NewImage']['serialNumber']['S']
    is_approved = record['dynamodb']['NewImage']['isApproved']['BOOL']
    subject = f'FSIEMCloud {environment}: New POC {serial_no}'
    message = (
        f'Serial Number: {serial_no}\n'
        f'Environment: {environment}\n'
        f'Is Approved: {is_approved}\n'
    )
    return subject, message


def storage_approval(record: dict, environment: str) -> tuple[str, str]:
    """Creates message and subject for email about new entries in the storage
    approval dynamoDB table

    Parameters
    ----------
    record : dict
        The record received from the dynamodb record
    environment : str
        The environment the function and dynamodb tables are located in

    Returns
    -------
    tuple[str, str]
        A Tuple of the Subject and Message of the email to send
    """
    if record['eventName'] != 'INSERT':
        print(f'Ignoring messages with status: {record["eventName"]}')
        return None, None
    serial_no = record['dynamodb']['NewImage']['serialNumber']['S']
    is_approved = record['dynamodb']['NewImage']['isApproved']['BOOL']
    subject = f'FSIEMCloud {environment}: Storage Reduction {serial_no}'
    message = (
        f'Serial Number: {serial_no}\n'
        f'Environment: {environment}\n'
        f'Is Approved: {is_approved}\n'
    )
    return subject, message


def remove_blocked_email_addresses(to_addresses: list, email_block_table: str,
                                   dynamodb_region: str) -> list:
    """Check whether the email addresses in the expiring deployments are
    present in the email block dynamodb table. If so they will be removed from
    the list of deployments to send emails to.

    Parameters
    ----------
    to_addresses : list
        The list of email addresses that emails will be sent to
    email_block_table : str
        The name of the dynamodb email block list table
    dynamodb_region : str
        The region of the dynamodb table

    Returns
    -------
    list
        Updated to_addresses where blocked emails have been removed
    """
    blocked_emails = []
    client = boto3.client('dynamodb', region_name=dynamodb_region)

    for email in to_addresses:
        response = client.get_item(
            TableName=email_block_table,
            Key={
                'email': {
                    'S': email,
                }
            }
        )

        if 'Item' in response and response['Item']['email']['S'] == email:
            print(f'Address {email} found in block list, email will not '
                  'be sent')
            blocked_emails.append(email)

    # Remove deployment from dict if it has no more emails
    for email in blocked_emails:
        to_addresses.remove(email)

    return to_addresses


def scheduled_upgrade(record: dict, region: str, from_address: str,
                      bcc_address: str, upgrade_table_name: str,
                      activation_table_name: str, email_block_table_name: str,
                      environment: str) -> Email:
    """Creates HTML email for scheduled upgrades

    Parameters
    ----------
    record : dict
        The record received from the dynamodb record
    region : str
        The region the resources are located in
    from_address : str
        The from email address for sent emails
    bcc_address : str
        The internal notification address for FortiSIEM cloud to bcc emails to
    upgrade_table_name : str
        The name of the upgrade dynamoDB table
    activation_table_name : str
        The name of the activation dynamoDB table
    email_block_table_name : str
        The name of the email block dynamoDB table
    environment : str
        The environment the function and dynamodb tables are located in

    Returns
    -------
    Email
        The HTML email to be send via SES
    """
    print('Event is from the scheduled upgrade table')
    if environment == 'playground':
        print('Event is for playground. Will not send scheduled upgrade email '
              'to bcc to avoid spam')
        bcc_addresses = []
    else:
        bcc_addresses = [bcc_address]

    if record['eventName'] == 'REMOVE':
        print('We dont send emails on REMOVE')
        return None
    serial_no = record['dynamodb']['NewImage']['serialNumber']['S']
    status = record['dynamodb']['NewImage']['status']['S']
    scheduled_local = record['dynamodb']['NewImage']['scheduledLocal']['S']
    upgrade_path = record['dynamodb']['NewImage']['upgradePath']['S']

    # Convert scheduled_local into a more aethestically pleasing format
    date = isoparse(scheduled_local)
    datestring = date.strftime("%Y-%m-%d %H:%M:%S%z")

    # Get the upgrade_path table record
    upgrade_details = get_upgrade_path(
        upgrade_path, upgrade_table_name, region)
    if not upgrade_details:
        print(f'Could not find upgrade path {upgrade_path} in table, will not '
              'send email')
        return None

    current_version = upgrade_details['currentVersion']['S']
    new_version = upgrade_details['newVersion']['S']
    docs_link = upgrade_details['docsLink']['S']

    # Get email addresses from activation table
    activation_table = ActivationTable(activation_table_name, region)
    to_addresses = activation_table.get_emails(serial_no)

    # Check addresses against email block table
    to_addresses = remove_blocked_email_addresses(
        to_addresses, email_block_table_name, region)
    if not to_addresses:
        print(f'All addresses for {serial_no} have been blocked, we cannot '
              'send any emails to this deployment.')
        return

    today = datetime.now(timezone.utc)
    year = today.year

    with open('template.html', 'r') as f:
        data = f.read()
    template = Template(data, undefined=StrictUndefined)

    if status == STATUS_TYPE.PENDING.value:
        subject = (f'FortiSIEM Cloud: Your deployment {serial_no} '
                   'has an upgrade scheduled')
    elif status == STATUS_TYPE.IN_PROGRESS.value:
        subject = (f'FortiSIEM Cloud: Your deployment {serial_no} '
                   'has started its upgrade')
    elif status == STATUS_TYPE.SUCCESS.value:
        subject = (f'FortiSIEM Cloud: Your deployment {serial_no} '
                   'has successfully finished its upgrade')
    elif status == STATUS_TYPE.FAILURE.value:
        subject = (f'FortiSIEM Cloud: Your deployment {serial_no} '
                   'has failed its upgrade')
    else:
        print(f'Unexpected email type: {status}. Will abort sending '
              'email.')
        return

    body = template.render(
        current_year=year,
        serial_no=serial_no,
        type=status,
        current_version=current_version,
        new_version=new_version,
        docs_link=docs_link,
        upgrade_time=datestring
    )

    email = Email(
        from_address=from_address,
        to_addresses=to_addresses,
        bcc_addresses=bcc_addresses,
        subject=subject,
        body_text=body)

    return email


def main(event, context):
    """Receives changes to entries in the dynamodb table activation_table, and
    sends out email alerts if the status of any entry is in a failed state

    Parameters
    ----------
    event : Any
        The event object containing the data from the dynamodb stream.
        See: https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    context : Any
        Context information passed to the function at runtime.
        See: https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    """
    topic = environ['TOPIC']
    activation_arn = environ['ACTIVATION_ARN']
    poc_approval_arn = environ['POC_APPROVAL_ARN']
    storage_approval_arn = environ['STORAGE_APPROVAL_ARN']
    scheduled_upgrade_arn = environ['SCHEDULED_UPGRADE_ARN']
    environment = environ['ENVIRONMENT']
    region = environ['REGION']
    from_address = environ['FROM_ADDRESS']
    bcc_address = environ['FSIEM_BCC_ADDRESS']
    upgrade_table = environ['UPGRADES_TABLE_NAME']
    activation_table = environ['ACTIVATION_TABLE_NAME']
    email_block_table = environ['EMAIL_BLOCK_TABLE_NAME']

    sns = boto3.client('sns')
    ses = Ses(region)

    for record in event['Records']:
        print(f'Event record: {record}')

        # Activation Table
        if record['eventSourceARN'].startswith(activation_arn):
            print('Event is from the activation table')
            subject, message = activation(record, environment)

        # Poc Approval Table
        elif record['eventSourceARN'].startswith(poc_approval_arn):
            print('Event is from the POC approval table')
            subject, message = poc_approval(record, environment)

        # Storage Approval Table
        elif record['eventSourceARN'].startswith(storage_approval_arn):
            print('Event is from the storage approval table')
            subject, message = storage_approval(record, environment)

        # Scheduled Upgrade Table
        elif record['eventSourceARN'].startswith(scheduled_upgrade_arn):
            print('Event is from the scheduled upgrade table')
            email = scheduled_upgrade(
                record, region, from_address, bcc_address, upgrade_table,
                activation_table, email_block_table, environment)
            if not email:
                continue
            ses.send_email_html(email)
            continue

        else:
            print('Could not determine the source of the event, skipping')
            continue

        if subject is None or message is None:
            print('Subject or message not set, skipping')
            continue

        sns.publish(
            TopicArn=topic,
            Message=message,
            Subject=subject
        )
