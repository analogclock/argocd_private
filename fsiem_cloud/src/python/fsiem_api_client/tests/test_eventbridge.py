import boto3
import pytest
from datetime import datetime
from json import load, dumps
from freezegun import freeze_time
from moto import mock_aws
from fsiem_api_client.eventbridge import EventBridge


@freeze_time("2012-01-14 00:04:34", tz_offset=0)
def test_get_deploy_event():
    event_bus_name = 'marktest'
    with open('tests/deploy_event.json', 'r') as f:
        item = load(f)

    detail_expected = {
        'name': 'FSMCLD0000000155',
        'region': 'us-east-1',
        'deploymentEmail': 'test@fortinet.com',
        'deploymentType': 'sp',
        'deploymentSKU': {
            'compute': {'quantity': '5'},
            'onlineStorage': {'quantity': '1'},
            'archiveStorage': {'quantity': '1'}
        },
        'deploymentIPV4Cidr': '0.0.0.0/0',
        'deploymentIPV6Cidr': '::/0',
        'updatingDeployment': True,
        'primaryAZ': 'us-east-1f',
        'is_poc': False
    }
    expected = {
        'Source': 'fsiem.deploy.pipeline',
        'EventBusName': event_bus_name,
        'Time': datetime.now(),
        'DetailType': 'UpdateDeployment',
        'Detail': dumps(detail_expected)
    }
    eventbridge = EventBridge(event_bus_name)
    actual = eventbridge.get_deploy_event(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=0)
def test_get_deploy_event_check_prevent():
    event_bus_name = 'marktest'
    with open('tests/deploy_event.json', 'r') as f:
        item = load(f)

    detail_expected = {
        'name': 'FSMCLD0000000155',
        'region': 'us-east-1',
        'deploymentEmail': 'test@fortinet.com',
        'deploymentType': 'sp',
        'deploymentSKU': {
            'compute': {'quantity': '5'},
            'onlineStorage': {'quantity': '1'},
            'archiveStorage': {'quantity': '1'}
        },
        'deploymentIPV4Cidr': '0.0.0.0/0',
        'deploymentIPV6Cidr': '::/0',
        'updatingDeployment': True,
        'primaryAZ': 'us-east-1f',
        'is_poc': False
    }
    expected = {
        'Source': 'fsiem.deploy.pipeline',
        'EventBusName': event_bus_name,
        'Time': datetime.now(),
        'DetailType': 'UpdateDeployment',
        'Detail': dumps(detail_expected)
    }
    eventbridge = EventBridge(event_bus_name)
    actual = eventbridge.get_deploy_event(item, check_prevent=True)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=0)
def test_get_deploy_event_prevent_true():
    event_bus_name = 'marktest'
    with open('tests/deploy_event_prevent.json', 'r') as f:
        item = load(f)

    expected = {}
    eventbridge = EventBridge(event_bus_name)
    actual = eventbridge.get_deploy_event(item, check_prevent=True)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=0)
def test_get_deploy_event_bad_archive():
    event_bus_name = 'mark_test'
    with open('tests/deploy_event_bad_archive.json', 'r') as f:
        item = load(f)

    detail_expected = {
        'name': 'FSMCLD0000000155',
        'region': 'us-east-1',
        'deploymentEmail': 'test@fortinet.com',
        'deploymentType': 'sp',
        'deploymentSKU': {
            'compute': {'quantity': '5'},
            'onlineStorage': {'quantity': '1'},
            'archiveStorage': {'quantity': '0'}
        },
        'deploymentIPV4Cidr': '0.0.0.0/0',
        'deploymentIPV6Cidr': '::/0',
        'updatingDeployment': True,
        'primaryAZ': 'us-east-1f',
        'is_poc': False
    }
    expected = {
        'Source': 'fsiem.deploy.pipeline',
        'EventBusName': event_bus_name,
        'Time': datetime.now(),
        'DetailType': 'UpdateDeployment',
        'Detail': dumps(detail_expected)
    }
    eventbridge = EventBridge(event_bus_name)
    actual = eventbridge.get_deploy_event(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=0)
def test_get_deploy_event_bad_compute():
    event_bus_name = 'mark_test'
    with open('tests/deploy_event_bad_compute.json', 'r') as f:
        item = load(f)

    eventbridge = EventBridge(event_bus_name)

    with pytest.raises(KeyError):
        eventbridge.get_deploy_event(item)


@mock_aws
def test_send_events():
    detail = {
        'name': 'test',
        'region': 'eu-west-1',
        'deploymentEmail': 'test@fortinet.com',
        'deploymentType': 'va',
        'deploymentWorkerCount': '2',
        'deploymentIPV4Cidr': '0.0.0.0/0',
        'deploymentIPV6Cidr': '::/0',
        'updatingDeployment': True
    }
    events = {
        'Source': 'fsiem.deploy.pipeline',
        'EventBusName': 'marktest',
        'Time': datetime.now(),
        'DetailType': 'UpdateDeployment',
        'Detail': dumps(detail)
    }
    boto3.client('events', region_name='us-east-1').create_event_bus(
        Name='marktest'
    )
    eventbridge = EventBridge('test')
    actual = eventbridge.send_events([events], 'us-east-1')
    assert len(actual['Entries']) == 1
