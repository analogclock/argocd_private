import boto3
from typing import Any


class ExternalStorageTable:
    """
    Access to external storage table
    """

    def __init__(self, table: str, region: str) -> None:
        """Access to the DynamoDb table with info about external storage

        Parameters
        ----------
        table : str
            The name of the DynamoDb table
        region : str
            The region when DynamoDb table is located
        """
        self.client = boto3.client('dynamodb', region_name=region)
        self.resource = boto3.resource('dynamodb', region_name=region)
        self.table = table
        self.region = region

    def _get_item_attribute(self, serial_number: str) -> Any | None:
        """Get value of an attribute from an item in the DynamoDb table

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment

        Returns
        -------
        Any | None
            Item from DynamoDB based on serial number and the column name
            or None if key doesn't exist
        """

        resp = self.client.query(
            TableName=self.table, ConsistentRead=True,
            ExpressionAttributeValues={':serial_number': {'S': serial_number}},
            KeyConditionExpression='serialNumber = :serial_number')

        # Check item exists in external storage table, if not - return None
        items = resp.get('Items', [])
        if items:
            return items
        else:
            print(f"No items found in external storage table  "
                  f"for the serial number: {serial_number}")
            return None

    def get_external_storage_dests(self, serial_number: str) -> Any | None:
        """Retrieve the organization_id and s3 bucket name

        Parameters
        ----------
        serial_number : str
            _The serial number of the deployment_

        Returns
        -------
        Any | None
            _ get all the attribute values for that serial number_
        """
        values = self._get_item_attribute(serial_number)
        return values

    def update_external_storage_table(self, serial_number: str,
                                      organization_id: int, last_update: str,
                                      last_status: str, status_message: str,
                                      data_transferred: str) -> dict:

        """Update the last update and status

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        organization_id : int
            Organization id
        last_update : str
            date and time of last s3 data copy for the organization id
        last_status : str
            status of the last s3 data copy for the organization id
        status_message : str
            message stating in-progress, complete or failed
        data_transferred : str
            bytes transferred to s3 bucket

        Returns
        -------
        dict
            Response of the dynamodb item update
        """
        # Iterate through the list and update each item
        table = self.resource.Table(self.table)
        response = table.update_item(
            Key={
                'serialNumber': serial_number,
                'organizationId': organization_id
            },
            UpdateExpression="SET #l_update = :n_update, \
                                  #l_status = :n_status,  \
                                  #l_status_msg = :n_status_msg, \
                                  #l_data_trans = :n_data_trans",
            ExpressionAttributeNames={
                '#l_update': 'lastUpdate',
                '#l_status': 'lastStatus',
                '#l_status_msg': 'comments',
                '#l_data_trans': 'dataTransferred'
            },
            ExpressionAttributeValues={
                ':n_update': last_update,
                ':n_status': last_status,
                ':n_status_msg': status_message,
                ':n_data_trans': data_transferred
            }
        )
        return response
