import boto3
from datetime import datetime


class SchedUpgradesTable:
    status_pending = 'Pending'
    status_in_progress = 'InProgress'
    status_complete = 'Complete'
    status_failed = 'Failed'

    def __init__(self, table: str, region: str) -> None:
        self.client = boto3.client('dynamodb', region_name=region)
        self.table = table

    def get_all_upgrades(self) -> list:
        """Scan scheduled upgrades table to retrieve all scheduled upgrades

        Returns
        -------
        list
            A list of all entries in the scheduled upgrades table
        """
        print('Querying scheduled upgrades table')
        items = []
        response = self.client.scan(
            TableName=self.table
        )
        items.extend(response['Items'])
        while True:
            if 'LastEvaluatedKey' not in response:
                break
            response = self.client.scan(
                TableName=self.table,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response['Items'])
        print(f'Found {len(items)} entries in the scheduled upgrades table')
        return items

    def update_status(self, serial_number: str, upgrade_path: str, status: str,
                      update_start_time: bool = False,
                      update_end_time: bool = False):
        """Update the status of the scheduled upgrade

        Parameters
        ----------
        serial_number : str
            The serial number of the deployments whose status will be updated
        upgrade_path : str
            The upgrade path that the scheduled upgrade will use
        status : str
            The status to change to
        update_start_time : bool, optional
            Whether to update the startTime field, by default False
        update_end_time : bool, optional
            Whether to update the endTime field, by default False
        """
        print(f'Updating upgrade status for deployment {serial_number} to '
              f'status {status}')

        update_expression = 'SET #status = :s'
        expression_names = {'#status': 'status'}
        expression_values = {':s': {'S': status}}
        datetime_string = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        if update_start_time:
            update_expression = f'{update_expression}, #start_time = :t'
            expression_names['#start_time'] = 'startTime'
            expression_values[':t'] = {'S': datetime_string}
        if update_end_time:
            update_expression = f'{update_expression}, #end_time = :e'
            expression_names['#end_time'] = 'endTime'
            expression_values[':e'] = {'S': datetime_string}
        self.client.update_item(
            TableName=self.table,
            Key={
                'serialNumber': {
                    'S': serial_number
                },
                'upgradePath': {
                    'S': upgrade_path
                }
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
