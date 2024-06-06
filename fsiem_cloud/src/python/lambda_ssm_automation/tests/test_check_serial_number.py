from moto import mock_aws
from check_serial_number import check_serial_number
from tests.aws.aws_helpers import (dynamodb_create_table, dynamodb_put_item)


@mock_aws
def test_check_serial_number():
    sn = 'FSMCLD0000000152'
    table_name = 'fsiem_activation_table_playground'
    region = 'us-east-1'

    dynamodb_create_table(table_name, region)
    dynamodb_put_item(table_name, region, sn)

    event = {
        'SerialNumber': sn,
        'EnvId': "playground",
        'DefaultRegion': region

    }
    check_serial_number(event)
