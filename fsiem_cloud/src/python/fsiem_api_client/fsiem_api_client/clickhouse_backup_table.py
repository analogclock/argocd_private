import boto3
from dataclasses import dataclass, field


class BackupStatus:
    """The status we store in DynamoDb for a single backup info instance"""
    backup_in_progress = 'BackupInProgress'
    backup_ok = 'BackupCreated'
    backup_failed = 'BackupFailed'
    backup_delete_in_progress = 'BackupDeleteInProgress'
    backup_delete_ok = 'BackupDeleted'
    backup_delete_failed = 'BackupDeleteFailed'


@dataclass
class BackupInfo:
    """A single backup (full or incremental).
    NOTE: if you change this class, modify the
    ClickhouseBackupTable.update accordingly"""
    serial_number: str          # Stack serial number
    name: str                   # Name for this backup, e.g. DATE-TYPE-SEQ_NUM
    start_date: str             # When backup has started
    stop_date: str              # When it finished
    status: str                 # One of BackupStatus values
    failed_reason: str          # Failure reason
    previous_backup_name: str   # Set this when creating an incremental backup
    type: str                   # Type: full or incremental
    current_seq_number: int     # Number in a chain, e.g. full (1) -> inc (2)
    total_seq_number: int       # Always incremented number of backups
    s3_location: str            # Where we store the backups
    backup_options: str         # Any additional backup options


@dataclass
class BackupInfoHistory:
    """A history of all backups for the current stack (based on its SN)"""
    all: list[BackupInfo] = field(default_factory=list)


class ClickhouseBackupTable:
    """DynamoDb ORM class. Allows CRUD operations for BackupInfo and
    BackupInfoHistory.
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

    def _to_backup_info(self, item: dict) -> BackupInfo:
        return BackupInfo(
            item['serialNumber']['S'],
            item['name']['S'],
            item['startDate']['S'],
            item['stopDate']['S'],
            item['status']['S'],
            item.get('failedReason', {}).get('S', ''),
            item['previousBackupName']['S'],
            item['type']['S'],
            int(item['currentSeqNumber']['N']),
            int(item['totalSeqNumber']['N']),
            item['s3Location']['S'],
            item.get('backupOptions', {}).get('S', ''))

    def get_one(self, sn: str, name: str) -> BackupInfo | None:
        """Get an item from DynamoDb"""
        resp = self.client.get_item(
            TableName=self.table, ConsistentRead=True,
            Key={'serialNumber': {'S': sn}, 'name': {'S': name}})
        # Check if item exists, if not - return None
        item = resp.get('Item')
        if not item or not item.get('serialNumber'):
            return None
        return self._to_backup_info(item)

    def get_backup_history(self, sn: str) -> BackupInfoHistory | None:
        """Get backup history from DynamoDb"""
        resp = self.client.query(
            TableName=self.table, ConsistentRead=True,
            ExpressionAttributeValues={':arg1': {'S': sn}},
            KeyConditionExpression='serialNumber = :arg1')
        # Check if item exists, if not - return None
        items = resp.get('Items')
        if not items:
            return None
        history = BackupInfoHistory()
        for item in items:
            history.all.append(self._to_backup_info(item))

        # Sort by the total sequence number
        history.all = sorted(history.all, key=lambda x: x.total_seq_number)
        return history

    def insert(self, item: BackupInfo):
        """Insert an item in DynamoDb, throws if item exists

        Parameters
        ----------
        item : BackupInfo
            Details about backup
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
            'previousBackupName': ?,
            'type': ?,
            'currentSeqNumber': ?,
            'totalSeqNumber': ?,
            's3Location': ?,
            'backupOptions': ?
            }}'''
        params = [
            {'S': item.serial_number},
            {'S': item.name},
            {'S': item.start_date},
            {'S': item.stop_date},
            {'S': item.status},
            {'S': item.failed_reason},
            {'S': item.previous_backup_name},
            {'S': item.type},
            {'N': str(item.current_seq_number)},
            {'N': str(item.total_seq_number)},
            {'S': item.s3_location},
            {'S': item.backup_options},
        ]
        self.client.execute_statement(Statement=cmd, Parameters=params)

    def insert_many(self, items: list[BackupInfo]):
        """Insert items into DynamoDb, throws if any item exists

        Parameters
        ----------
        item : list[BackupInfo]
            Details about backup
        """
        for item in items:
            self.insert(item)

    def insert_if_does_not_exist(self, item: BackupInfo):
        """Insert an item in DynamoDb if it doesn't exist. If item exists,
        this call does nothing.

        Parameters
        ----------
        item : BackupInfo
            Details about backup
        """
        if not self.exists(item):
            self.insert(item)

    def insert_many_if_does_not_exist(self, items: list[BackupInfo]):
        """Insert items in DynamoDb if any item doesn't exist. If item exists,
        this call does nothing and proceeds to the next item to insert.

        Parameters
        ----------
        item : list[BackupInfo]
            Details about backup
        """
        for item in items:
            if not self.exists(item):
                self.insert(item)

    def delete(self, item: BackupInfo) -> bool:
        """Delete an item from DynamoDb. Does not throw if item isn't there."""
        resp = self.client.delete_item(
            TableName=self.table,
            Key={
                'serialNumber': {'S': item.serial_number},
                'name': {'S': item.name}
            },)
        return resp['ResponseMetadata']['HTTPStatusCode'] == 200

    def delete_many(self, items: list[BackupInfo]) -> bool:
        """Delete items from DynamoDb"""
        for item in items:
            self.delete(item)

    def exists(self, item: BackupInfo) -> bool:
        """Checks if item exists in DynamoDb"""
        return self.get_one(item.serial_number, item.name) is not None

    def update(self, item: BackupInfo):
        """Update an item in DynamoDb

        Parameters
        ----------
        item : BackupInfo
            Details about backup
        """
        cmd = f'''UPDATE {self.table}
                  SET startDate=?
                  SET stopDate=?
                  SET status=?
                  SET failedReason=?
                  SET previousBackupName=?
                  SET type=?
                  SET currentSeqNumber=?
                  SET totalSeqNumber=?
                  SET s3Location=?
                  SET backupOptions=?
                  WHERE serialNumber=?
                        AND
                        name=?
            '''
        params = [
            {'S': item.start_date},
            {'S': item.stop_date},
            {'S': item.status},
            {'S': item.failed_reason},
            {'S': item.previous_backup_name},
            {'S': item.type},
            {'N': str(item.current_seq_number)},
            {'N': str(item.total_seq_number)},
            {'S': item.s3_location},
            {'S': item.backup_options},
            {'S': item.serial_number},
            {'S': item.name},
        ]
        self.client.execute_statement(Statement=cmd, Parameters=params)
