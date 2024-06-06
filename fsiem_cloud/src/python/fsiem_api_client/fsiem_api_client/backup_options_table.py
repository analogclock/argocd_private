import boto3
import json
from typing import Iterator


class BackupOptions:

    def from_str(self, input: str) -> Iterator[list[tuple]]:
        """Parses config string in the following format

        Use this like so:

            options = BackupOptions()
            items = options.from_str(payload)
            for key, value in items:
                print(key)    # S3_COMPRESSION_LEVEL
                print(value)  # 1

        Parameters
        ----------
        input : str
            String json array, e.g.
            [{"S3_COMPRESSION_LEVEL": "1"}, {"S3_COMPRESSION_FORMAT": "tar"}]

        Yields
        ------
        Iterator[list[tuple]]
            An iterable list with the name of the setting, and its value
        """
        if not input:
            return []
        json_array = json.loads(input)
        for json_object in json_array:
            for first_value, second_value in json_object.items():
                yield (first_value, second_value)


class BackupOptionsTable:
    """DynamoDb ORM class. Allows CRUD operations for backup options"""

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

    def get(self, sn: str) -> list[tuple]:
        """Get an item from DynamoDb"""
        resp = self.client.get_item(
            TableName=self.table,
            ConsistentRead=True,
            Key={'serialNumber': {'S': sn}})

        # Check if item exists, if not - return None
        item = resp.get('Item')
        if not item or not item.get('backupOptions'):
            return []
        options = BackupOptions()
        resp = options.from_str(item['backupOptions']['S'])
        return list(resp) if resp else []

    def insert(self, sn: str, backup_options: str):
        """Insert an item in DynamoDb, throws if item exists"""
        cmd = f'''
        INSERT INTO {self.table}
        VALUE {{
            'serialNumber': ?,
            'backupOptions': ?
            }}'''
        params = [
            {'S': sn},
            {'S': backup_options}
        ]
        return self.client.execute_statement(Statement=cmd, Parameters=params)

    def insert_if_does_not_exist(self,  sn: str, backup_options: str):
        """Insert an item in DynamoDb if it doesn't exist. If item exists,
        this call does nothing.
        """
        if not self.exists(sn):
            return self.insert(sn, backup_options)

    def delete(self, sn: str) -> bool:
        """Delete an item from DynamoDb. Does not throw if item isn't there."""
        resp = self.client.delete_item(
            TableName=self.table,
            Key={'serialNumber': {'S': sn}})
        return resp['ResponseMetadata']['HTTPStatusCode'] == 200

    def exists(self, sn: str) -> bool:
        """Checks if item exists in DynamoDb"""
        return self.get(sn) is not None

    def update(self, sn: str, backup_options: str):
        """Update an item in DynamoDb"""
        cmd = f'''UPDATE {self.table}
                  SET backupOptions=?
                  WHERE serialNumber=?
            '''
        params = [
            {'S': backup_options},
            {'S': sn}
        ]
        return self.client.execute_statement(Statement=cmd, Parameters=params)
