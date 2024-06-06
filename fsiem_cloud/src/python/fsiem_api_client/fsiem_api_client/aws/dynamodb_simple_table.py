import boto3
from botocore.exceptions import ClientError
from typing import Any


class DynamoDbSimpleTable:
    """DynamoDb representation of a table with a single serialNumber key"""

    def __init__(self, table: str, region: str) -> None:
        """Access to the DynamoDb table

        Parameters
        ----------
        table : str
            The name of the DynamoDb table
        region : str
            The region when DynamoDb table is located
        """
        self.client = boto3.client('dynamodb', region_name=region)
        self.table = table
        self.region = region

    def get_attribute(self, serial_number: str, key: str,
                      value_type='S') -> Any | None:
        """Get value of an attribute from an item in the DynamoDb table

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        key : str
            Column name in the database
        value_type : str, optional
            DynamoDb type for the column, by default 'S' (which is a String)

        Returns
        -------
        Any | None
            Item from DynamoDB based on serial number and the column name
            or None if key doesn't exist
        """
        resp = self.client.get_item(
            TableName=self.table,
            Key={'serialNumber': {'S': serial_number}},
            ConsistentRead=True)
        # Check item exists, if not - return None
        item = resp.get('Item')
        if not item or not item.get(key):
            return None
        return item[key][value_type]

    def update(self, sn: str, key: str, value: str, value_type='S') \
            -> Any | None:
        """Update item in DynamoDb

        Parameters
        ----------
        sn : str
            The serial number of the deployment
        key : str
            Column name in the database
        value : str
            New value to set for the given key
        value_type : str, optional
            DynamoDb type for the column, by default 'S' (which is a String)
        """
        self.client.update_item(
            TableName=self.table,
            Key={'serialNumber': {'S': sn}},
            UpdateExpression='SET #name = :value',
            ExpressionAttributeNames={'#name': key},
            ExpressionAttributeValues={':value': {value_type: value}})

    def get_full(self, serial_number: str) -> Any | None:
        """Get the full item from the DynamoDB table

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment

        Returns
        -------
        Any | None
            Item from DynamoDB based on serial number
        """
        resp = self.client.get_item(
            TableName=self.table,
            Key={'serialNumber': {'S': serial_number}},
            ConsistentRead=True)
        # Check item exists, if not - return None
        return resp.get('Item')

    def insert(self, item: dict):
        """Insert item in DynamoDb

        Parameters
        ----------
        sn : str
            The serial number of the deployment
        item : dict
            A json object, e.g.:
            item = {
                'serialNumber': {'S': '00000'},
                'name': {'S': 'example_name'},
            }
        """
        self.client.put_item(TableName=self.table, Item=item)

    def upsert(self, item: dict):
        """Upsert item in DynamoDb

        Parameters
        ----------
        sn : str
            The serial number of the deployment
        item : dict
            A json object, e.g.:
            item = {
                'serialNumber': {'S': '00000'},
                'name': {'S': 'example_name'},
            }
        """
        try:
            self.client.put_item(TableName=self.table, Item=item)
        except ClientError as e:
            print(f'Failed to insert an item: {e}')

            # If the item does not exist, insert it
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':  # noqa
                self.client.update_item(item)

    def delete(self, sn: str) -> bool:
        """Delete an item from DynamoDb. Does not throw if item isn't there."""
        resp = self.client.delete_item(
            TableName=self.table,
            Key={'serialNumber': {'S': sn}})
        return resp['ResponseMetadata']['HTTPStatusCode'] == 200

    def exists(self, sn: str) -> bool:
        """Checks if item exists in DynamoDb"""
        return self.get(sn) is not None
