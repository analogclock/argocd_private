

from datetime import datetime
from json import dumps
from typing import Any
import boto3


class EventBridge:

    def __init__(self, event_bus_name: str):
        self.event_bus_name = event_bus_name

    def get_deploy_event(self, item: dict, deploy_type: str = 'UPDATE',
                         check_prevent: bool = False) -> dict:
        """Generate an event for the deploy eventbridge pipeline

        Parameters
        ----------
        item : dict
            Activation table entry
        deploy_type : str, optional
            Whether to update the deployment or delete it. Either UPDATE or
            DELETE, by default UPDATE
        check_prevent : bool, optional
            Whether to respect the preventUpdate flag, by default False

        Returns
        -------
        dict
            The prepared event. Will return an empty dict if check_prevent is
            True and the preventUpdate flag is set
        """
        if check_prevent and self._prevent_update(item):
            return {}
        if deploy_type == 'UPDATE':
            event = self._prepare_update_event(item)
        elif deploy_type == 'DELETE':
            event = self._prepare_delete_event(item)
        else:
            raise ValueError('Invalid value for deploy_type')
        return event

    def _prevent_update(self, item: dict) -> bool:
        serial_no = item['serialNumber']['S']
        if item['status']['S'] != 'Complete':
            print(f'{serial_no} is not in status Complete')
            return True
        elif 'preventUpdate' in item and item['preventUpdate']['BOOL']:
            why = item['preventUpdateReason']['S'] if \
                'preventUpdateReason' in item else 'Not defined'

            print(f'preventUpdate flag for {serial_no} is set to true, reason '
                  f'{why}')
            return True
        else:
            return False

    def _prepare_update_event(self, item: dict) -> dict[str, Any]:
        sku = item['deploymentSKU']['M']
        try:
            compute = sku['compute']['M']['quantity']['N']
            online = sku['onlineStorage']['M']['quantity']['N']
        except KeyError:
            print('SKU map for compute or online storage is malformed, cannot '
                  'update')
            raise

        try:
            archive = sku['archiveStorage']['M']['quantity']['N']
        except KeyError as e:
            print('SKU map for archive storage is malformed, will set to 0')
            print(e)
            archive = '0'

        sku_map = {
            'compute': {
                'quantity': compute
            },
            'onlineStorage': {
                'quantity': online
            },
            'archiveStorage': {
                'quantity': archive
            }
        }
        detail = {
            'name': item['serialNumber']['S'],
            'region': item['region']['S'],
            'deploymentEmail': item['deploymentEmail']['S'],
            'deploymentType': item['deploymentType']['S'],
            'deploymentSKU': sku_map,
            'deploymentIPV4Cidr': item['ipV4Cidr']['S'],
            'deploymentIPV6Cidr': item['ipV6Cidr']['S'],
            'updatingDeployment': True
        }

        # Check for fields that are not always present in dynamodb entry and
        # add them to event if they exist
        if 'primaryAZ' in item:
            detail['primaryAZ'] = item['primaryAZ']['S']
        if 'isPOC' in item:
            detail['is_poc'] = item['isPOC']['BOOL']
        if 'externalStorageDest' in item:
            detail['externalStorageDest'] = item['externalStorageDest']['S']

        event = {
            'Source': 'fsiem.deploy.pipeline',
            'EventBusName': self.event_bus_name,
            'Time': datetime.now(),
            'DetailType': 'UpdateDeployment',
            'Detail': dumps(detail)
        }
        return event

    def _prepare_delete_event(self, item: dict) -> dict[str, Any]:
        detail = {
            'name': item['serialNumber']['S'],
            'region': item['region']['S'],
            'action': 'destroy'
        }
        event = {
            'Source': 'fsiem.deploy.pipeline',
            'EventBusName': self.event_bus_name,
            'Time': datetime.now(),
            'DetailType': 'DestroyDeployment',
            'Detail': dumps(detail)
        }
        return event

    def send_events(self, events: list, region: str):
        """Send events to eventbridge event bus

        Parameters
        ----------
        events : list
            List of prepared events
        region : str
            The AWS region the event bus is located in
        """
        client = boto3.client('events', region_name=region)
        response = client.put_events(
            Entries=events
        )
        print(response)
        return response
