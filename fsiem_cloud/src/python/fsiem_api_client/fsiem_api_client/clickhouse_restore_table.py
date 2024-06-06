import boto3
from dataclasses import dataclass, field


class RestoreStatus:
    """The status we store in DynamoDb for a single restore info instance"""
    restore_in_progress = 'RestoreInProgress'
    restore_ok = 'RestoreCompleted'
    restore_failed = 'RestoreFailed'


@dataclass
class RestoreInfo:
    """A single restore from ClickHouse backup.
    NOTE: if you change this class, modify the
    ClickhouseRestoreTable.update accordingly"""
    serial_number: str          # Stack serial number
    name: str                   # Name for this restore, e.g. DATE-SEQ_NUM
    start_date: str             # When it started
    stop_date: str              # When it finished
    status: str                 # One of RestoreStatus values
    failed_reason: str          # Failure reason
    restored_from: str          # Name of the backup from which we restored
    total_seq_number: int       # Always incremented number of restores
    s3_location: str            # S3 location from where we download backups


@dataclass
class RestoreInfoHistory:
    """A history of all restores for the current stack (based on its SN)"""
    all: list[RestoreInfo] = field(default_factory=list)


class ClickhouseRestoreTable:
    """DynamoDb ORM class. Allows CRUD operations for RestoreInfo and
    RestoreInfoHistory.
    """

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

    def _to_restore_info(self, item: dict) -> RestoreInfo:
        return RestoreInfo(
            item['serialNumber']['S'],
            item['name']['S'],
            item['startDate']['S'],
            item['stopDate']['S'],
            item['status']['S'],
            item.get('failedReason', {}).get('S', ''),
            item['restoredFrom']['S'],
            int(item['totalSeqNumber']['N']),
            item['s3Location']['S'])

    def get_one(self, sn: str, name: str) -> RestoreInfo | None:
        """Get an item from DynamoDb"""
        resp = self.client.get_item(
            TableName=self.table, ConsistentRead=True,
            Key={'serialNumber': {'S': sn}, 'name': {'S': name}})
        # Check if item exists, if not - return None
        item = resp.get('Item')
        if not item or not item.get('serialNumber'):
            return None
        return self._to_restore_info(item)

    def get_restore_history(self, sn: str) -> RestoreInfoHistory | None:
        """Get restore history from DynamoDb"""
        resp = self.client.query(
            TableName=self.table, ConsistentRead=True,
            ExpressionAttributeValues={':arg1': {'S': sn}},
            KeyConditionExpression='serialNumber = :arg1')
        # Check if item exists, if not - return None
        items = resp.get('Items')
        if not items:
            return None
        history = RestoreInfoHistory()
        for item in items:
            history.all.append(self._to_restore_info(item))

        # Sort by the total sequence number
        history.all = sorted(history.all, key=lambda x: x.total_seq_number)
        return history

    def insert(self, item: RestoreInfo):
        """Insert an item in DynamoDb, throws if item exists

        Parameters
        ----------
        item : RestoreInfo
           Details about restore
        """
        cmd = f'''
        INSERT INTO {self.table}
        VALUE {{
            'serialNumber': ?,
            'name': ?,
            'startDate': ?,
            'stopDate': ?,
            'status': ?,
            'failedReason': ?,
            'restoredFrom': ?,
            'totalSeqNumber': ?,
            's3Location': ?
            }}'''
        params = [
            {'S': item.serial_number},
            {'S': item.name},
            {'S': item.start_date},
            {'S': item.stop_date},
            {'S': item.status},
            {'S': item.failed_reason},
            {'S': item.restored_from},
            {'N': str(item.total_seq_number)},
            {'S': item.s3_location},
        ]
        self.client.execute_statement(Statement=cmd, Parameters=params)

    def insert_many(self, items: list[RestoreInfo]):
        """Insert items into DynamoDb, throws if any item exists

        Parameters
        ----------
        item : list[RestoreInfo]
           Details about restore
        """
        for item in items:
            self.insert(item)

    def insert_if_does_not_exist(self, item: RestoreInfo):
        """Insert an item in DynamoDb if it doesn't exist. If item exists,
        this call does nothing.

        Parameters
        ----------
        item : RestoreInfo
           Details about restore
        """
        if not self.exists(item):
            self.insert(item)

    def insert_many_if_does_not_exist(self, items: list[RestoreInfo]):
        """Insert items in DynamoDb if any item doesn't exist. If item exists,
        this call does nothing and proceeds to the next item to insert.

        Parameters
        ----------
        item : list[RestoreInfo]
           Details about restore
        """
        for item in items:
            if not self.exists(item):
                self.insert(item)

    def delete(self, item: RestoreInfo) -> bool:
        """Delete an item from DynamoDb. Does not throw if item isn't there."""
        resp = self.client.delete_item(
            TableName=self.table,
            Key={
                'serialNumber': {'S': item.serial_number},
                'name': {'S': item.name}
            },)
        return resp['ResponseMetadata']['HTTPStatusCode'] == 200

    def delete_many(self, items: list[RestoreInfo]) -> bool:
        """Delete items from DynamoDb"""
        for item in items:
            self.delete(item)

    def exists(self, item: RestoreInfo) -> bool:
        """Checks if item exists in DynamoDb"""
        return self.get_one(item.serial_number, item.name) is not None

    def update(self, item: RestoreInfo):
        """Update an item in DynamoDb

        Parameters
        ----------
        item : RestoreInfo
           Details about restore
        """
        cmd = f'''UPDATE {self.table}
                  SET startDate=?
                  SET stopDate=?
                  SET status=?
                  SET failedReason=?
                  SET restoredFrom=?
                  SET totalSeqNumber=?
                  SET s3Location=?
                  WHERE serialNumber=?
                        AND
                        name=?
            '''
        params = [
            {'S': item.start_date},
            {'S': item.stop_date},
            {'S': item.status},
            {'S': item.failed_reason},
            {'S': item.restored_from},
            {'N': str(item.total_seq_number)},
            {'S': item.s3_location},
            {'S': item.serial_number},
            {'S': item.name},
        ]
        self.client.execute_statement(Statement=cmd, Parameters=params)
