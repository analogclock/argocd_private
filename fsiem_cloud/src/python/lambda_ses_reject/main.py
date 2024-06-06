import boto3
from json import loads
from os import environ


def get_emails(event: dict) -> list:
    """Parse the sns events and collect a list of emails and additional details
    to be add to the block list

    Parameters
    ----------
    event : dict
        The event object containing the data from the dynamodb stream

    Returns
    -------
    list
        A list of emails to be added to the block list
        A list of dictionaries in the following format:
        [
            {
                'email': 'test@test.com,
                'timestamp': '2022-10-18T16:46:18.000Z,
                'type': 'Bounce'
            },
            ...
        ]
    """
    email_list = []
    for record in event['Records']:
        message = loads(record['Sns']['Message'])
        print(event)
        print(message)
        if message['notificationType'] == 'Bounce':
            if message['bounce']['bounceType'] == 'Permanent':
                for recipient in message['bounce']['bouncedRecipients']:
                    email = recipient['emailAddress']
                    print(f'{email} has permanent bounce adding to block list')
                    entry = {
                        'email': email,
                        'timestamp': message['bounce']['timestamp'],
                        'type': 'Bounce'
                    }
                    email_list.append(entry)
            if message['bounce']['bounceType'] == 'Transient':
                for recipient in message['bounce']['bouncedRecipients']:
                    email = recipient['emailAddress']
                    print(f'{email} has transient bounce, will ignore')
        if message['notificationType'] == 'Complaint':
            for recipient in message['complaint']['complainedRecipients']:
                email = recipient['emailAddress']
                print(f'{email} has complaint adding to block list')
                entry = {
                    'email': email,
                    'timestamp': message['complaint']['timestamp'],
                    'type': 'Complaint'
                }
                email_list.append(entry)
    return email_list


def add_to_block_list(email_list: list, table_name: str, table_region: str):
    """Add email addresses and additional details to the block list dynamodb
    table

    Parameters
    ----------
    email_list : list
        A list of dicts of email addresses and additional details taken from
        get_emails()
    table_name : str
        The name of the dynamodb table
    table_region : str
        The region where the dynamodb table is located
    """
    print(f'Adding email addresses to the block list: {email_list}')
    client = boto3.client('dynamodb', region_name=table_region)
    for entry in email_list:
        client.put_item(
            TableName=table_name,
            Item={
                'email': {
                    'S': entry['email']
                },
                'type': {
                    'S': entry['type']
                },
                'timestamp': {
                    'S': entry['timestamp']
                }
            }
        )


def main(event: dict, context):
    """Placeholder

    Parameters
    ----------
    event : dict
        The event object containing the data from the dynamodb stream.
        See: https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    context : Any
        Context information passed to the function at runtime.
        See: https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    """
    table_region = environ['TABLE_REGION']
    table_name = environ['DYNAMODB_EMAIL_BLOCK_TABLE']
    email_list = get_emails(event)
    add_to_block_list(email_list, table_name, table_region)
