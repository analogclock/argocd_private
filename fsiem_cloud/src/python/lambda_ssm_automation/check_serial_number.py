# Program to check if the Serial Number is valid
from aws.dynamodb import DynamoDb


def check_serial_number(event):
    sn = event["SerialNumber"]
    env_id = event["EnvId"]
    print(f'Serial number passed to check_serial_number: {sn}')
    default_region = event['DefaultRegion']
    table_name = "fsiem_activation_table_" + env_id
    print('Check user-provided serial number from DynamoDb')
    dynamodb = DynamoDb(table_name, region=default_region)
    response = dynamodb.get_item(sn)
    if response:
        print(f'Serial number is valid: {response["Item"]["serialNumber"]}')
    else:
        raise ValueError(f'Invalid serial number - {sn}')
