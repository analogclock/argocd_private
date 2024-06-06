import boto3

# AWS helpers for mocking AWS services
# When used with moto, this in-memory DynamoDb table, put a demo deployment
# record there. Allows us to create an EC2 security group, etc.


#
# Ec2
#
def ec2_create_sg(sg_name: str, region: str) -> str:
    ec2 = boto3.resource('ec2', region_name=region)
    vpc = ec2.Vpc('id')
    resp = vpc.create_security_group(GroupName=sg_name, Description='test')
    return resp.group_id


#
# DynamoDb
#
def dynamodb_create_table(table_name: str, region: str, wait=False):
    client = boto3.client('dynamodb', region_name=region)
    resp = client.create_table(
        TableName=table_name,
        AttributeDefinitions=[
            {'AttributeName': 'serialNumber', 'AttributeType': 'S'}],
        KeySchema=[
            {'AttributeName': 'serialNumber', 'KeyType': 'HASH'}],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}
    )
    if wait:
        waiter = client.get_waiter('table_exists')
        waiter.wait(TableName=table_name,
                    WaiterConfig={'Delay': 1, 'MaxAttempts': 10})
    return resp


def dynamodb_delete_table(table_name: str, region: str, wait=False):
    client = boto3.client('dynamodb', region_name=region)
    resp = client.delete_table(TableName=table_name)
    if wait:
        waiter = client.get_waiter('table_not_exists')
        waiter.wait(TableName=table_name,
                    WaiterConfig={'Delay': 1, 'MaxAttempts': 10})
    return resp


def dynamodb_insert_item(table_region: str, cmd: str):
    client = boto3.client('dynamodb', region_name=table_region)
    return client.execute_statement(Statement=cmd)


def dynamodb_put_item(table_name: str, table_region: str, serial_number: str,
                      status: str = '', cluster_region='us-east-1'):
    client = boto3.client('dynamodb', region_name=table_region)
    resp = client.put_item(
        TableName=table_name,
        Item={
            'serialNumber': {'S': serial_number},
            'status': {'S': status},
            'region': {'S': cluster_region},
            'alternateCertificateARN': {'S': 'arn:aws:acm:eu-west-1:023941436530:certificate/74b5618d-5500-49c7-a167-e134bc56e190'},  # noqa
            'alternateDomain': {'S': 'tester.dev.fortisiem.cloud.'},
            'archiveSizeUsage': {'N': '6144'},
            'created': {'S': '2022-11-01T15:56:39.1341+00:00'},
            'deploymentEmail': {'S': 'prataps@fortinet.com'},
            'deploymentSKU': {
                'M': {
                    'archiveStorage': {
                        'M': {
                            'endDate': {'S': '2023-08-08T00:00:00+00:00'},
                            'expiryDays': {'N': '264'},
                            'quantity': {'N': '1'},
                            'startDate': {'S': '2022-08-08T00:00:00+00:00'}
                        }
                    },
                    'compute': {
                        'M': {
                            'endDate': {'S': '2023-08-08T00:00:00+00:00'},
                            'expiryDays': {'N': '264'},
                            'quantity': {'N': '5'},
                            'startDate': {'S': '2022-08-08T00:00:00+00:00'}
                        }
                    },
                    'onlineStorage': {
                        'M': {'endDate': {'S': '2024-08-07T00:00:00+00:00'},
                              'expiryDays': {'N': '629'},
                              'quantity': {'N': '1'},
                              'startDate': {'S': '2022-08-08T00:00:00+00:00'}
                              }
                    }
                }
            },
            'deploymentType': {'S': 'va'},
            'displayRegion': {'S': 'Europe (Ireland)'},
            'endpoint': {
                'M': {
                    'displayName': {'S': 'Europe (Ireland)'},
                    'originalSystemName': {'S': 'eu-west-1'},
                    'partitionDnsSuffix': {'S': 'amazonaws.com'},
                    'partitionName': {'S': 'aws'},
                    'systemName': {'S': 'eu-west-1'}
                }
            },
            'ipV4Cidr': {'S': '57.57.57.57/32, 65.65.65.65/32'},
            'ipV6Cidr': {'S': '::/0, 2345:425:2CA1:0000:0000:567:673:23b5/64'},
            'isPOC': {'BOOL': False},
            'onlineSizeUsage': {'N': '215015424'},
            'updateAlternateDomain': {'BOOL': False},
            'url': {
                'S': 'https://fsmcld0000000152.playground.fortisiem.cloud'},
            'version': {'S': '6.7.0.1963'},
            'workersUrl': {
                'S':
                'https://worker-fsmcld0000000152.playground.fortisiem.cloud'}
        }
    )
    return resp
