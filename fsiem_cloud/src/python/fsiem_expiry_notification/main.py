import boto3
from argparse import ArgumentParser
from datetime import datetime, timezone
from jinja2 import Template, StrictUndefined
from fsiem_api_client import ActivationTable

# 2022-08-12T00:00:00+00:00
datetime_format = '%Y-%m-%dT%H:%M:%S%z'

expiring_days = [35, 30, 14, 7]
expired_days = [-1]


def find_near_expiry(deployments: list) -> dict:
    """Get number of days until the license expires for each deployment and
    email address, returning only those that fall on a day we will send an
    email

    Parameters
    ----------
    deployments : list
        A dict of the deployments from the activation table

    Returns
    -------
    dict
        A dict of the serial number, number of days until expiry and email,
        i.e.
        {
            'FSMCLD0000000123': {
                'emails': ['test@test.com'],
                'expiry': 5
            }.
            ...
        }
    """
    expiring = {}
    for deployment in deployments:
        serial_no = deployment['serialNumber']['S']
        emails = []
        emails.append(deployment['deploymentEmail']['S'])
        # do we have additional contacts
        # and do they have a value
        if 'additionalContacts' in deployment and \
                deployment['additionalContacts']:
            additional = deployment['additionalContacts']['S']
            emails.extend(additional.split(','))
        expiry = datetime.strptime(
            deployment['deploymentSKU']['M']['compute']['M']['endDate']['S'],
            datetime_format
        )
        now = datetime.now(timezone.utc)
        delta = expiry - now
        if delta.days not in expiring_days and delta.days not in expired_days:
            continue
        expiring[serial_no] = {
            'emails': emails,
            'expiry': delta.days
        }
    return expiring


def remove_blocked_email_addresses(expiring: dict, email_block_table: str,
                                   dynamodb_region: str) -> dict:
    """Check whether the email addresses in the expiring deployments are
    present in the email block dynamodb table. If so they will be removed from
    the list of deployments to send emails to.

    Parameters
    ----------
    expiring : dict
        A dict of expiring deployments with the email address to send to and
        how many days until expiry
    email_block_table : str
        The name of the dynamodb email block list table
    dynamodb_region : str
        The region of the dynamodb table

    Returns
    -------
    dict
        Updated expiring dict where entries with email addresses present in the
        block list removed
    """
    blocked_deployments = []
    client = boto3.client('dynamodb', region_name=dynamodb_region)
    for serial_no, expiry in expiring.items():
        for email in expiry['emails']:
            response = client.get_item(
                TableName=email_block_table,
                Key={
                    'email': {
                        'S': email,
                    }
                }
            )

            # This second if statement is redundant, as if the email address
            # wasn't in the table then there would be no 'Item' field. However
            # it could be a good extra check if there was a weird response, or
            # if there was some screw up in this code.
            if 'Item' in response and response['Item']['email']['S'] == email:
                print(f'Address {email} found in block list, email will not '
                      'be sent')
                expiry['emails'].remove(email)

        if not expiry['emails']:
            print(f'All email addresses for {serial_no} are blocked, no email '
                  'will be sent')
            blocked_deployments.append(serial_no)

    # Remove deployment from dict if it has no more emails
    for serial_no in blocked_deployments:
        expiring.pop(serial_no)

    return expiring


def prep_emails(expiries: dict, portal_domain: str, year: int) -> list:
    """Finds deployments that are due to have email notifications and prepares
    the emails to be sent

    Parameters
    ----------
    expiries : dict
        A dict of the serial number, number of days until expiry and email
    portal_domain : str
        The domain name of the environments portal
    year: int
        The current year that we are dealing with

    Returns
    -------
    list
        A list of dicts with details on sending an email, i.e.
        [
            {
                'address': 'test@test.com',
                'subject': 'hello',
                'body': '<html>...</html>'
            },
            ...
        ]
    """
    with open('template.html', 'r') as f:
        data = f.read()
    template = Template(data, undefined=StrictUndefined)
    emails = []
    for serial_no, expiry in expiries.items():
        expiry_days = expiry["expiry"]
        if expiry_days in expiring_days:
            subject = (f'FortiSIEM Cloud: Your deployment {serial_no} is '
                       f'nearing expiry - {expiry_days} days remaining')
            body = template.render(
                current_year=year,
                serial_no=serial_no,
                expiry_days=expiry_days,
                portal_domain=portal_domain,
                type='expiring'
            )
        elif expiry_days in expired_days:
            subject = (f'FortiSIEM Cloud: Your deployment {serial_no} has '
                       'expired')
            body = template.render(
                current_year=year,
                serial_no=serial_no,
                expiry_days=expiry_days,
                portal_domain=portal_domain,
                type='expired'
            )
        emails.append({
            'addresses': expiry['emails'],
            'subject': subject,
            'body': body
        })
    return emails


def send_emails(emails: list, from_address: str, fsiem_address: str):
    """Sends all emails though AWS Simple Email Service

    Parameters
    ----------
    emails : list
        A list of emails to be sent, see prep_emails() for format
    from_address : str
        The from email address for sent emails
    fsiem_address : str
        The internal notification address for FortiSIEM cloud to bcc emails to
    """
    client = boto3.client('ses')
    charset = 'UTF-8'
    print(f'Sending {len(emails)} emails')
    for email in emails:
        try:
            client.send_email(
                Source=from_address,
                Destination={
                    'ToAddresses': email['addresses'],
                    'BccAddresses': [fsiem_address]
                },
                Message={
                    'Subject': {
                        'Data': email['subject'],
                        'Charset': charset
                    },
                    'Body': {
                        'Html': {
                            'Data': email['body'],
                            'Charset': charset
                        }
                    }
                },
                ReplyToAddresses=[]
            )
        except Exception as e:
            print(f'Email to {email["addresses"]} failed with exception')
            print(e)


def main(activation_table: str, email_block_table: str, dynamodb_region: str,
         from_address: str, fsiem_address: str, portal_domain: str):
    """Tracks and alerts on expiring deployments

    Parameters
    ----------
    activation_table : str
        The name of the dynamodb activation table
    email_block_table : str
        The name of the dynamodb email block table
    dynamodb_region : str
        The region of the dynamodb tables
    from_address : str
        The from email address for sent emails
    fsiem_address : str
        The internal notification address for FortiSIEM cloud to bcc emails to
    portal_domain : str
        The domain name of the environments portal
    """
    today = datetime.now(timezone.utc)
    db = ActivationTable(activation_table, dynamodb_region)
    deployments = db.get_all_items()

    expiring = find_near_expiry(deployments)

    expiring = remove_blocked_email_addresses(expiring, email_block_table,
                                              dynamodb_region)

    emails = prep_emails(expiring, portal_domain, today.year)

    send_emails(emails, from_address, fsiem_address)


def parse_args() -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Tracks and alerts on expiring deployments')
    parser = ArgumentParser(description=description)
    parser.add_argument('--activation_table', type=str, required=True,
                        help='The name of the dynamodb activation table')
    parser.add_argument('--email_block_table', type=str, required=True,
                        help='The name of the dynamodb email block list table')
    parser.add_argument('--dynamodb_region', type=str, required=True,
                        help='The region of the dynamodb tables')
    parser.add_argument('--from_address', type=str, required=True,
                        help='The from email address for sent emails')
    parser.add_argument('--fsiem_address', type=str, required=True,
                        help='The internal notification address for FortiSIEM '
                             'cloud to bcc emails to')
    parser.add_argument('--portal_domain', type=str, required=True,
                        help='The domain name of the environments portal')
    return parser.parse_args()


if __name__ == '__main__':
    # Usage: python3 main.py --activation_table activation-table
    # --email_block_table email-table --dynamodb_region us-east-1
    # --from_address noreply@mail.test.com --fsiem_address test@test.com
    # --portal_domain fortisiem.cloud

    config = parse_args()
    main(config.activation_table, config.email_block_table,
         config.dynamodb_region, config.from_address, config.fsiem_address,
         config.portal_domain)
