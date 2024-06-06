# Program to invoke fortimonitor maintenance schedule
import urllib.request
import json
import ssl
from os import environ
from invoke_fmon_maintenance import get_fmon_api_key

api_url = 'https://api2.panopta.com/v2'


def get_fmon_maintenance_schedule_active(api_key):
    """Get fortimonitor maintenance schedule"""
    url = f'{api_url}/maintenance_schedule/active'
    print(f'Url for get_fmon_maintenance_schedule_active: {url} ')
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'ApiKey {api_key}'
    }
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


def terminate_active_schedule(maintenance_schedule_id, api_key, sn, env_id):
    """Terminate fortimonitor maintenance schedule for fsiem serial number"""
    url = f'{api_url}/maintenance_schedule/{maintenance_schedule_id}/terminate'
    print(f'terminate_fmon_maintenance_schedule: {url}')
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'ApiKey {api_key}'
    }
    req = urllib.request.Request(url, headers=headers, method='PUT')
    response = urllib.request.urlopen(req)
    result = response.read().decode('utf-8')
    print(result)
    if not (response.reason):
        raise ValueError('add_fmon_maintenance_sch got an unhealthy response '
                         f'from fortimonitor, http code: {response.status}')


def terminate_fmon_maintenance(event):
    """Terminate fortimonitor maintenance schedule after upgrade"""
    secret_arn = environ['SECRET_ARN']
    secret_region = environ['SECRET_REGION']
    sn = event["SerialNumber"]
    env_id = event["EnvId"]
    api_key = get_fmon_api_key(secret_arn, secret_region)
    print(api_key)
    # Get active maintenance schedule list
    active_schedules = get_fmon_maintenance_schedule_active(api_key)
    print(f'Maintenance schedules active list: {active_schedules} ')
    name = f'Terraform scheduled maintenance window for upgrade {sn} {env_id}'
    url = None
    id = None
    for schedule in active_schedules["maintenance_schedule_list"]:
        if schedule["name"] == name:
            url = schedule["url"]
            id = url.split("/")[-1]
            break
    if id:
        print(f"The maintenance_schedule_id for '{name}' is: {id}")
    else:
        print(f"No maintenance_schedule_id found for '{name}'.")
    maintenance_schedule_id = int(id)
    print(f'Maintenance schedule id: {maintenance_schedule_id}')
    terminate_active_schedule(maintenance_schedule_id, api_key, sn, env_id)
