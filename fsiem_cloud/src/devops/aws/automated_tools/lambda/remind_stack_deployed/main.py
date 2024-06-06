import json
import random
import boto3
from dateutil import parser
from urllib import parse, request

TABLE_NAMES = ["fsiem_activation_table_dev",
               "fsiem_activation_table_playground"]
REGION = "us-east-1"


class DeployedStack:
    def __init__(self, serialNumber, created, deploymentEmail):
        self.serialNumber = serialNumber
        self.created = created
        self.deploymentEmail = deploymentEmail


def get_deployed_stacks():
    deployed_stacks = []
    unique_emails = set()

    for table_name in TABLE_NAMES:
        resource = boto3.resource('dynamodb', region_name=REGION)
        table = resource.Table(table_name)
        response = table.scan()
        items = response['Items']
        for item in items:
            unique_emails.add(item['deploymentEmail'])
            deployed_stacks.append(
                DeployedStack(
                    item['serialNumber'],
                    item['created'],
                    item['deploymentEmail']))
    return unique_emails, deployed_stacks


def get_giphy_embedded_img():
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=REGION)
    response = client.get_secret_value(SecretId="devops/giphy-api-key")
    api_key = json.loads(response['SecretString'])['giphy_api_key']

    query = random.choice(["funny", "no no no", "dog reaction", "crazy cat",
                           "not again", "hacker", "funny movie"])

    url = "http://api.giphy.com/v1/gifs/random"
    params = parse.urlencode({
        "api_key": api_key,
        "tag": query,
        "limit": "1",
        "rating": "g"
    })

    with request.urlopen("".join((url, "?", params))) as response:
        data = json.loads(response.read())

    if response.status == 200:
        return data['data']['images']['fixed_width']['webp']
    else:
        print("Failed to fetch random GIF:", data.get('message'))
        return None


def send_emails(unique_emails, deployed_stacks):
    for unique_email in unique_emails:
        print("Getting a gif")
        gif_url = get_giphy_embedded_img()
        print("Gif obtained")
        stacks = ""
        for stack in deployed_stacks:
            if stack.deploymentEmail == unique_email:
                date = parser.parse(stack.created).date()
                stacks += f"<li> {stack.serialNumber} created on {date} </li>"

        email_body = f"""
        <html>
        <body>
        <h1>Reminder: stacks are up</h1>
        <p>Hi,
        <br/>
        <br/>
        This is a reminder that you have some stacks running in dev/playground.
        <br/>
        Feel free to delete them if you don't need them.
        <br/>
        </p>
        <p><strong>Stacks:</strong>
        <br/>
        <ul>
        {stacks}
        </ul>
        </p>
        <img src="{gif_url}" style="float:left">
        </body>
        </html>
        """

        email_client = boto3.client('ses', region_name=REGION)
        email_client.send_email(
            Destination={
                'ToAddresses': [unique_email],
                # Uncomment for testing
                # 'ToAddresses': ["omandrychenko@fortinet.com"],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': email_body,
                    }
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': "Reminder: stacks in dev/playground",
                },
            },
            Source="no-reply@mail.playground.fortisiem.cloud",
        )
        print(f"Emailed: {unique_email}")


def lambda_handler(event: dict, context) -> dict:
    """This function reminds owner of a deployed stacks"""

    try:
        print("Getting stacks")
        unique_emails, deployed_stacks = get_deployed_stacks()
        print(f"Will send {len(unique_emails)} emails in total")
        send_emails(unique_emails, deployed_stacks)
        print("Done")
    except Exception as e:
        print(f'Unexpected error: {e}')
