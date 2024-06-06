
from moto import mock_aws
from fsiem_api_client.activation_table import ActivationTable
from tests.dynamo_db import create_table, put_item


@mock_aws
def test_get_full_item():
    table_name = 'test'
    region = 'us-east-1'
    status = ActivationTable(table_name, region)
    serial_number = 'test'
    create_table(table_name, region)
    put_item(table_name, region, serial_number, status.complete)

    expected = {
        'serialNumber': {
            'S': serial_number
        },
        'status': {
            'S': status.complete
        },
        'region': {
            'S': region
        }
    }
    actual = status.get_full_item(serial_number)
    assert actual == expected


@mock_aws
def test_get_status():
    table_name = 'test'
    region = 'us-east-1'
    status = ActivationTable(table_name, region)
    serial_number = 'test'
    create_table(table_name, region)
    put_item(table_name, region, serial_number, status.complete)

    expected = status.complete
    actual = status.get_status(serial_number)
    assert actual == expected


@mock_aws
def test_update_status():
    table_name = 'test'
    region = 'us-east-1'
    status = ActivationTable(table_name, region)
    serial_number = 'test'
    create_table(table_name, region)
    put_item(table_name, region, serial_number, status.complete)

    expected = None
    actual = status.update_status(serial_number, status.update_in_progress)
    assert actual == expected


@mock_aws
def test_get_all_items():
    table_name = 'test'
    region = 'us-east-1'
    cluster_region = 'us-west-2'
    status = ActivationTable(table_name, region)
    serial_number = 'test'
    create_table(table_name, region)
    put_item(table_name, region, serial_number, status.complete,
             cluster_region=cluster_region)

    expected = [{
        'serialNumber': {'S': serial_number},
        'status': {'S': 'Complete'},
        'region': {'S': cluster_region}
    }]
    actual = status.get_all_items()
    assert actual == expected


@mock_aws
def test_get_deployment_region():
    table_name = 'test'
    table_region = 'us-west-2'
    cluster_region = 'us-east-1'
    status = ActivationTable(table_name, table_region)
    serial_number = 'test'
    create_table(table_name, table_region)
    put_item(table_name, table_region, serial_number, status.complete,
             cluster_region=cluster_region)

    expected = cluster_region
    actual = status.get_deployment_region(serial_number)
    assert actual == expected


@mock_aws
def test_update_version():
    table_name = 'test'
    region = 'us-west-2'
    status = ActivationTable(table_name, region)
    serial_number = 'test'
    version = '6.1.0'
    create_table(table_name, region)
    put_item(table_name, region, serial_number, status.complete)

    expected = None
    actual = status.update_version(serial_number, version)
    assert actual == expected
