# Program to invoke fortimonitor maintenance schedule
import boto3
import urllib.request
import json
import ssl
from os import environ
from datetime import datetime

api_url = 'https://api2.panopta.com/v2'


def get_current_datetime():
    # Get the current date and time
    current_datetime = datetime.now()

    # Format the date and time as a string
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

    # Return the formatted date and time
    return formatted_datetime


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
    secret_dict = json.loads(response['SecretString'])
    return secret_dict['api_key']


def get_fmon_server_group(api_key, sn):
    """Get fortimonitor Server Group id for fsiem serial number"""
    url = f'{api_url}/server_group'
    print(f'Url for get_fmon_server_group stack {sn}: {url}')
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'ApiKey {api_key}'
    }
    params = {
        'full': 'true',
        'limit': 0,
        'offset': 0,
        'name': sn
    }
    encoded_params = urllib.parse.urlencode(params)
    full_url = f'{url}?{encoded_params}'
    print(full_url)
    req = urllib.request.Request(full_url, headers=headers)
    context = ssl.create_default_context()
    content = urllib.request.urlopen(req, context=context)
    # Reading response content
    response_content = content.read()
    print(response_content.decode('utf-8'))
    # Getting status code and reason
    print("Status code: ", content.status)
    print("Reason: ", content.reason)
    if not (content.reason):
        raise ValueError('get_fmon_server_group got an unhealthy response from'
                         f' fortimonitor, http code: {content.status}')
    resp_json = json.loads(response_content.decode('utf-8'))
    return resp_json


def add_fmon_maintenance_schedule(api_key, duration, target_url, sn, env_id):
    """Add fortimonitor maintenance schedule for fsiem serial number"""
    url = f'{api_url}/maintenance_schedule'
    print(f'add_fmon_maintenance_schedule {url}, {duration} minutes')
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'ApiKey {api_key}'
    }
    name = f'Terraform scheduled maintenance window for upgrade {sn} {env_id}'
    data = {
       "description": 'Maintenance schedule for upgrade',
       "duration": duration,
       "monitoring": 'pause_all_checks',
       "name": name,
       "original_start_time": get_current_datetime(),
       "targets": [target_url]
    }
    print(f' Attributes for maintenance schedule: {data}')
    json_data = json.dumps(data)
    json_as_bytes = json_data.encode('utf-8')   # needs to be bytes
    req = urllib.request.Request(url, headers=headers, method='POST')
    response = urllib.request.urlopen(req,  json_as_bytes)
    result = response.read().decode('utf-8')
    print(result)
    if not (response.reason):
        raise ValueError('add_fmon_maintenance_sch got an unhealthy response '
                         f'from fortimonitor, http code: {response.status}')


def get_fmon_maintenance_schedule(api_key):
    """Get fortimonitor maintenance schedule"""
    url = f'{api_url}/maintenance_schedule'
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'ApiKey {api_key}'
    }
    print(f'Url for get_fmon_maintenance_schedule : {url} ')
    params = {
        'limit': 0,
        'offset': 0
    }
    encoded_params = urllib.parse.urlencode(params)
    full_url = f'{url}?{encoded_params}'
    print(full_url)
    req = urllib.request.Request(full_url, headers=headers)
    context = ssl.create_default_context()
    content = urllib.request.urlopen(req, context=context)
    # Reading response content
    response_content = content.read()
    print(response_content.decode('utf-8'))
    # Getting status code and reason
    print("Status code: ", content.status)
    print("Reason: ", content.reason)
    if not (content.reason == 'OK'):
        raise ValueError('get_fmon_ maintenance_sch got an unhealthy response '
                         f'from fortimonitor, http code: {content.status}')
    resp_json = json.loads(response_content.decode('utf-8'))
    return resp_json


def invoke_fmon_maintenance(event):
    """Invoke fortimonitor maintenance schedule"""
    secret_arn = environ['SECRET_ARN']
    secret_region = environ['SECRET_REGION']
    sn = event["SerialNumber"]
    env_id = event["EnvId"]
    api_key = get_fmon_api_key(secret_arn, secret_region)
    print(api_key)
    # Maintenance schedule for upgrade will be approx 2 hours
    duration = 120
    server_group = get_fmon_server_group(api_key, sn)
    print(f'Data dictionary: {server_group}')
    # Search for the 'url' when the 'name' is env(dev/playground/prod)
    print(f'Invoke fmon maintenance on environment: {env_id}')
    target_env_name = env_id
    target_url = None
    for item in server_group["server_group_list"]:
        if item["server_group"] is not None and \
           item["server_group"]["name"] == target_env_name:
            target_url = item["url"]
            break
    print(f'Server group id url: {target_url}')
    # Add maintenance schedule to fortimonitor
    add_fmon_maintenance_schedule(api_key, duration, target_url, sn, env_id)
    # Get maintenance schedule list
    maintenance_schedule = get_fmon_maintenance_schedule(api_key)
    print(f'Maintenance Schedules List: {maintenance_schedule} ')
