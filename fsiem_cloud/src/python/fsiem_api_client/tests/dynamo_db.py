import boto3


def create_table(table_name: str, region: str, wait=False):
    client = boto3.client('dynamodb', region_name=region)
    resp = client.create_table(
        TableName=table_name,
        AttributeDefinitions=[
            {
                'AttributeName': 'serialNumber',
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': 'serialNumber',
                'KeyType': 'HASH'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    if wait:
        waiter = client.get_waiter('table_exists')
        waiter.wait(TableName=table_name,
                    WaiterConfig={'Delay': 1, 'MaxAttempts': 10})
    return resp


def delete_table(table_name: str, region: str, wait=False):
    client = boto3.client('dynamodb', region_name=region)
    resp = client.delete_table(TableName=table_name)
    if wait:
        waiter = client.get_waiter('table_not_exists')
        waiter.wait(TableName=table_name,
                    WaiterConfig={'Delay': 1, 'MaxAttempts': 10})
    return resp


def insert_item(table_region: str, cmd: str):
    client = boto3.client('dynamodb', region_name=table_region)
    return client.execute_statement(Statement=cmd)


def put_item(table_name: str, table_region: str, serial_number: str,
             status: str, cluster_region='us-east-1'):
    client = boto3.client('dynamodb', region_name=table_region)
    return client.put_item(
        TableName=table_name,
        Item={
            'serialNumber': {
                'S': serial_number
            },
            'status': {
                'S': status
            },
            'region': {
                'S': cluster_region
            }
        }
    )
