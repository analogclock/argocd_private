import boto3
from botocore.exceptions import ClientError
from typing import Any


class ExternalStorageStatusTable:
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

    def update_external_storage_status_table(self, serial_number: str,
                                             organization_id: int,
                                             start_datetime: str,
                                             end_datetime: str,
                                             bytes_copied: int
                                             ) -> Any | None:
        """Update external storage status table

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        organization_id : int
            organization id
        start_datetime: str
            start date and time of s3 data copy
        end_datetime : str
            end date and time of s3 data copy
        bytes_copied : int
            total bytes copied to s3 bucket during one transaction

        Returns
        -------
        Any | None
         Response to putting item in the dynamodb table
        """
        # Iterate through the list and update each item
        table = self.resource.Table(self.table)

        # Use put_item to add a new row only if the item does not already exist
        try:
            table.put_item(
                Item={
                    'serialNumber': serial_number,
                    'organizationId': organization_id,
                    'startDateTime': start_datetime,
                    'endDateTime': end_datetime,
                    'bytesCopied': bytes_copied
                },

            )
            print("PutItem successful")
        except ClientError as e:
            print(f"Error putting item: {e}")
