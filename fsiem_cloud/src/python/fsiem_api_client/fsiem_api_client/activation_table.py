import boto3
from datetime import datetime
from typing import Any
from fsiem_api_client.deployment_metrics import DeploymentMetrics


class ActivationTable:

    initializing = 'Initializing'
    license_in_progress = 'LicenseInProgress'
    setup_initializing = 'SetupInitializing'
    setup_in_progress = 'SetupInProgress'
    create_failed = 'CreateFailed'
    create_in_progress = 'CreateInProgress'
    complete = 'Complete'
    update_in_progress = 'UpdateInProgress'
    update_failed = 'UpdateFailed'
    update_completed = 'UpdateCompleted'
    delete_in_progress = 'DeleteInProgress'
    delete_failed = 'DeleteFailed'
    fail_statuses = [create_failed, update_failed, delete_failed]
    online_storage = 'ONLINE'
    archive_storage = 'ARCHIVE'

    def __init__(self, table: str, region: str) -> None:
        """Access to the DynamoDb table with info about fsiem deployments.

        Parameters
        ----------
        table : str
            The name of the DynamoDb table
        region : str
            The region the DynamoDb table is located
        """
        self.client = boto3.client('dynamodb', region_name=region)
        self.table = table
        self.region = region

    def _get_item_attribute(self, serial_number: str, key: str,
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

    def _update_item(self, sn: str, key: str, value: str, value_type='S') \
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

    def get_full_item(self, serial_number: str) -> Any | None:
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

    def get_status(self, serial_number: str) -> str:
        """Get the current status of the deployment

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment

        Returns
        -------
        str
            The status of the deployment or None if deployment not found
        """
        return self._get_item_attribute(serial_number, 'status')

    def update_status(self, serial_number: str, status: str):
        """Update the status of the deployment

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        status : str
            What to update the status to
        """
        self._update_item(serial_number, 'status', status)

    def update_sku(self, serial_number: str, sku: dict):
        """Update the sku for a given deployment

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        sku : dict
            new sku to be applied to deployment
        """
        empty = {'M': {'quantity': {'N': '0'}}}
        compute = sku.get('compute', {})
        online = sku.get('onlineStorage', {})
        archive = sku.get('archiveStorage', {})

        cmd = f'''UPDATE {self.table}
                  SET deploymentSKU.compute=?
                  SET deploymentSKU.onlineStorage=?
                  SET deploymentSKU.archiveStorage=?
                  WHERE serialNumber=?
            '''
        p = []
        p.append({'M': self.add_sku_update(compute)} if compute else empty)
        p.append({'M': self.add_sku_update(online)} if online else empty)
        p.append({'M': self.add_sku_update(archive)} if archive else empty)
        p.append({'S': serial_number})
        self.client.execute_statement(Statement=cmd, Parameters=p)

    def add_sku_update(self, item: dict):
        """Build up correct parameters for a dictionary
        to add to DynamoDB

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        item : dict
            provided entitlement
        """
        new_sku = {}
        # quantity is the only guaranteed field
        quantity = item.get('quantity', 0)
        endDate = item.get('endDate')
        startDate = item.get('startDate')
        expiryDays = item.get('expiryDays')

        if quantity:
            new_sku['quantity'] = {'N': str(quantity)}
        if endDate:
            new_sku['endDate'] = {'S': endDate}
        if startDate:
            new_sku['startDate'] = {'S': startDate}
        if expiryDays:
            new_sku['expiryDays'] = {'N': str(expiryDays)}
        return new_sku

    def get_all_items(self, limit=1000) -> list:
        """Run scan to get all records from the DynamoDb table

        Returns
        -------
        list
            A list of all items in the dynamodb table
        """
        items = []
        resp = self.client.scan(
            TableName=self.table, Limit=limit, ConsistentRead=True)
        items.extend(resp['Items'])

        while True:
            if 'LastEvaluatedKey' not in resp:
                break
            resp = self.client.scan(
                TableName=self.table, ConsistentRead=True,
                ExclusiveStartKey=resp['LastEvaluatedKey'], Limit=limit)
            items.extend(resp['Items'])
        return items

    def get_deployment_region(self, serial_number: str) -> str:
        """Get the AWS region where FortiSiem deployment occurred

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment

        Returns
        -------
        str
            AWS region for the deployment, or None if it was not found
        """
        return self._get_item_attribute(serial_number, 'region')

    def get_version(self, serial_number: str) -> str | None:
        """Get FortiSiem VM version from the database

        Parameters
        ----------
        serial_number : str
            serial number

        Returns
        -------
        str
            Version string, for example: "7.1.1.0159" or "7.1.4.0171"
            If the version is not present in the database, this call returns
            None.
        """
        return self._get_item_attribute(serial_number, 'version')

    def update_version(self, serial_number: str, version: str):
        """Update recorded the FSIEM version

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        version : str
            The FSIEM version to update the entry to
        """
        self._update_item(serial_number, 'version', version)

    def update_usage_size(self, storage_type: str,
                          serial_number: str, bytes: int):
        """Update size of efs

        Parameters
        ----------
        type: str
            The given type to update (ONLINE, ARCHIVE)
        serial_number : str
            The serial number of the deployment
        bytes : int
            The amount of bytes to set the new usage to
        """
        field = ''
        if storage_type == self.online_storage:
            field = 'onlineSizeUsage'
        elif storage_type == self.archive_storage:
            field = 'archiveSizeUsage'
        else:
            raise Exception(f"Invalid storage type passed `{storage_type}`")

        bytes_as_string = str(bytes)
        self._update_item(serial_number, field, bytes_as_string, 'N')

    def get_license_inserted_on(self, serial_number: str) -> str:
        return self._get_item_attribute(serial_number, 'licenseInsertedOn')

    def set_license_inserted_on(self, serial_number: str, val: str) -> str:
        self._update_item(serial_number, 'licenseInsertedOn', val)

    def get_storage_type(self, serial_number: str) -> str:
        return self._get_item_attribute(serial_number, 'storageType')

    def set_storage_type(self, serial_number: str, val: str) -> str:
        self._update_item(serial_number, 'storageType', val)

    def get_prevent_update(self, serial_number: str) -> bool:
        return self._get_item_attribute(serial_number, 'preventUpdate', 'BOOL')

    def set_prevent_update(self, serial_number: str, val: bool) -> bool:
        self._update_item(serial_number, 'preventUpdate', val, 'BOOL')

    def get_prevent_update_reason(self, serial_number: str) -> str:
        return self._get_item_attribute(serial_number, 'preventUpdateReason')

    def set_prevent_update_reason(self, serial_number: str, val: str) -> str:
        self._update_item(serial_number, 'preventUpdateReason', val)

    def get_uuid(self, serial_number: str) -> str:
        return self._get_item_attribute(serial_number, 'uuid')

    def set_uuid(self, serial_number: str, uuid: str):
        self._update_item(serial_number, 'uuid', uuid)

    def get_is_backup_enabled(self, serial_number: str) -> bool:
        return self._get_item_attribute(
            serial_number, 'isBackupEnabled', 'BOOL')

    def set_is_backup_enabled(self, serial_number: str, val: bool) -> bool:
        self._update_item(serial_number, 'isBackupEnabled', val, 'BOOL')

    def get_is_backup_running(self, serial_number: str) -> bool:
        value = self._get_item_attribute(
            serial_number, 'isBackupRunning', 'BOOL')
        return value if value else False

    def set_is_backup_running(self, serial_number: str, is_running: bool):
        self._update_item(serial_number, 'isBackupRunning', is_running, 'BOOL')

    def get_is_restore_running(self, serial_number: str) -> bool:
        value = self._get_item_attribute(
            serial_number, 'isRestoreRunning', 'BOOL')
        return value if value else False

    def set_is_restore_running(self, serial_number: str, is_running: bool):
        self._update_item(serial_number, 'isRestoreRunning', is_running,
                          'BOOL')

    def get_deployment_metrics(self, serial_number: str) -> DeploymentMetrics:
        map = self._get_item_attribute(serial_number, 'metrics', 'M')
        if not map:
            return None
        bucket = map['s3ArchiveBucket']['S']
        dir = map['s3ArchiveDir']['S']
        size = int(map['s3ArchiveSizeBytes']['N'])
        count = int(map['s3ArchiveObjectsCount']['N'])
        dt = datetime.fromisoformat(map['s3UpdatedOn']['S'])

        online_size_bytes = int(map['onlineSizeBytes']['N'])
        onlineMetricsJsonStr = map['onlineMetricsJsonStr']['S']

        return DeploymentMetrics(bucket, dir, size, count, dt,
                                 online_size_bytes, onlineMetricsJsonStr)

    def set_deployment_metrics(self, serial_number: str, m: DeploymentMetrics):
        iso_datetime = datetime.isoformat(m.s3_updated_on)
        self.client.update_item(
            TableName=self.table,
            Key={'serialNumber': {'S': serial_number}},
            UpdateExpression='SET #name = :value',
            ExpressionAttributeNames={'#name': 'metrics'},
            ExpressionAttributeValues={
                ':value': {
                    'M': {
                        's3ArchiveBucket': {'S': m.s3_archive_bucket},
                        's3ArchiveDir': {'S': m.s3_archive_dir},
                        's3UpdatedOn': {'S': iso_datetime},
                        's3ArchiveSizeBytes': {
                            # Casting value to str, otherwise DynamoDb, throws
                            # Invalid type for parameter error
                            'N': str(m.s3_archive_size_bytes)
                        },
                        's3ArchiveObjectsCount': {
                            'N': str(m.s3_archive_objects_count)
                        },
                        'onlineSizeBytes': {
                            'N': str(m.online_size_bytes)
                        },
                        'onlineMetricsJsonStr': {
                            'S': m.online_metrics_json_str
                        }
                    }
                }
            })

    def get_fmon_key(self, serial_number: str) -> str:
        return self._get_item_attribute(serial_number, 'fmonKey')

    def set_fmon_key(self, serial_number: str, fmon_id: str):
        self._update_item(serial_number, 'fmonKey', fmon_id)

    def get_emails(self, serial_number: str) -> list:
        emails = []
        emails.append(
            self._get_item_attribute(serial_number, 'deploymentEmail'))
        additional = self._get_item_attribute(
            serial_number, 'additionalContacts', 'S')
        if additional:
            emails.extend(additional.split(','))
        return emails
