import boto3
from typing import Any


class DynamoDb:
    """A helper class for DynamoDB table"""
    db_resource: Any

    def __init__(self, table_name: str, region: str) -> None:
        db = boto3.resource("dynamodb", region_name=region)
        self.db_resource = db.Table(table_name)

    def get_item(self, id: str, id_attr_name: str = 'serialNumber') -> Any:
        return self.db_resource.get_item(Key={id_attr_name: id})

    def get_cidr_v4(self, id: str) -> list[str]:
        response = self.get_item(id)
        if 'Item' not in response or not response['Item']['ipV4Cidr']:
            print(f'Item with id {id} does not have ipV4Cidr')
            return None
        ip_string = response['Item']['ipV4Cidr']
        return [x.strip() for x in ip_string.split(',')]

    def get_cidr_v6(self, id: str) -> list[str]:
        response = self.get_item(id)
        if 'Item' not in response or not response['Item']['ipV6Cidr']:
            print(f'Item with id {id} does not have ipV6Cidr')
            return None
        ip_string = response['Item']['ipV6Cidr']
        return [x.strip() for x in ip_string.split(',')]
