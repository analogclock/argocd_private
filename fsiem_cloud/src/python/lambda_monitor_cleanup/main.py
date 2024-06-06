import boto3
import requests
from json import loads
from os import environ
from urllib.parse import urlparse


api_url = 'https://api2.panopta.com/v2'


def get_fmon_api_key(secret_arn: str, secret_region: str) -> str:
    """Retrieve the fortimonitor API key from aws secrets manager

    Parameters
    ----------
    secret_arn : str
        The ARN of the secret
    secret_region : str
        The region the secret is located within

    Returns
    -------
    str
        The fortimonitor api key
    """
    client = boto3.client('secretsmanager', region_name=secret_region)
    response = client.get_secret_value(SecretId=secret_arn)
    secret_dict = loads(response['SecretString'])
    return secret_dict['api_key']


def get_fmon_server_id(server_key: str, api_key: str) -> str:
    """Uses the server key to retrieve the server ID from fortimonitor

    Parameters
    ----------
    server_key : str
        The server key
    api_key : str
        The fortimonitor api key

    Returns
    -------
    str
        The server ID

    Raises
    ------
    ValueError
        An unexpected response from fortimonitor
    """
    url = f'{api_url}/server'
    params = {
        'server_key': server_key
    }
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'ApiKey {api_key}'
    }
    response = requests.get(
        url,
        headers=headers,
        params=params,
        verify=True
    )
    if not response.ok:
        print(response.text, flush=True)
        raise ValueError('Get server request got an unhealthy response from '
                         f'fortimonitor, http code: {response.status_code}')
    resp_json = response.json()
    url_object = urlparse(resp_json['server_list'][0]['url'])
    return url_object.path.split('/')[-1]


def delete_fmon_server(server_id: str, api_key: str):
    """Delete the server from fortimonitor

    Parameters
    ----------
    server_id : str
        The ID of the server to delete from fortimonitor
    api_key : str
        The fortimonitor api key

    Raises
    ------
    ValueError
        An unexpected response from fortimonitor
    """
    url = f'{api_url}/server/{server_id}'
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'ApiKey {api_key}'
    }
    response = requests.delete(
        url,
        headers=headers,
        verify=True
    )
    if not response.ok:
        print(response.text, flush=True)
        raise ValueError(
            'Delete server request got an unhealthy response from '
            f'fortimonitor, http code: {response.status_code}')
    else:
        print(f'Successfully deleted: {server_id}', flush=True)


def main(event, context):
    """Receives changes to entries in the dynamodb table activation_table, and
    if a deployment is deleted then it will retrieve the fortimonitor server
    key for the fortimonitor container and delete it from fortimonitor

    Parameters
    ----------
    event : Any
        The event object containing the data from the dynamodb stream.
        See: https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    context : Any
        Context information passed to the function at runtime.
        See: https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    """
    secret_arn = environ['SECRET_ARN']
    secret_region = environ['SECRET_REGION']
    environment = environ['ENVIRONMENT']

    api_key = get_fmon_api_key(secret_arn, secret_region)

    for record in event['Records']:
        print(f'Event record: {record}', flush=True)
        if record['eventName'] != 'REMOVE':
            print('Ignoring event unless its a deletion', flush=True)
            print(record, flush=True)
            continue

        # Find server key
        if 'serialNumber' not in record['dynamodb']['OldImage']:
            print('Could not find serialNumber in event, will skip this entry',
                  flush=True)
            print(record, flush=True)
            continue

        serial_number = record['dynamodb']['OldImage']['serialNumber']['S']
        # server key is based on a unique, deterministic name
        # serial_number_fsiemcontainer
        server_key = f"{serial_number}_{environment}_fsiemcontainer"
        print(f'Deleting server key: {server_key}', flush=True)

        server_id = get_fmon_server_id(server_key, api_key)
        print(server_id, flush=True)
        delete_fmon_server(server_id, api_key)
