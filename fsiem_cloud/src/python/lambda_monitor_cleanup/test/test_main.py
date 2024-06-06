import boto3
from moto import mock_aws
from json import dumps
from main import get_fmon_api_key


def create_secret(secret_name, secret_value, region):
    client = boto3.client('secretsmanager', region_name=region)
    response = client.create_secret(
        Name=secret_name
    )
    arn = response['ARN']
    secret_dict = {'api_key': secret_value}
    response = client.put_secret_value(
        SecretId=arn,
        SecretString=dumps(secret_dict)
    )
    return arn


@mock_aws
def test_get_fmon_api_key():
    api_key = 'abc123'
    region = 'us-east-1'
    secret_arn = create_secret('unit_test', api_key, region)
    actual = get_fmon_api_key(secret_arn, region)
    assert api_key == actual
