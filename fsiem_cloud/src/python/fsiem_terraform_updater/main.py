from argparse import ArgumentParser
from datetime import datetime
from fsiem_api_client import ActivationTable, EventBridge
from pytz import timezone


region_time_map = {
    'us-east-1': timezone('America/New_York'),
    'us-east-2': timezone('America/New_York'),
    'us-west-1': timezone('America/Los_Angeles'),
    'us-west-2': timezone('America/Los_Angeles'),
    'af-south-1': timezone('Africa/Johannesburg'),
    'ap-east-1': timezone('Asia/Hong_Kong'),
    'ap-south-1': timezone('Asia/Calcutta'),
    'ap-south-2': timezone('Asia/Calcutta'),
    'ap-northeast-1': timezone('Asia/Tokyo'),
    'ap-northeast-2': timezone('Asia/Seoul'),
    'ap-northeast-3': timezone('Asia/Tokyo'),
    'ap-southeast-1': timezone('Asia/Singapore'),
    'ap-southeast-2': timezone('Australia/Sydney'),
    'ap-southeast-3': timezone('Asia/Jakarta'),
    'ca-central-1': timezone('America/New_York'),
    'eu-central-1': timezone('Europe/Berlin'),
    'eu-central-2': timezone('Europe/Zurich'),
    'eu-west-1': timezone('Europe/Dublin'),
    'eu-west-2': timezone('Europe/London'),
    'eu-west-3': timezone('Europe/Paris'),
    'eu-south-1': timezone('Europe/Rome'),
    'eu-south-2': timezone('Europe/Madrid'),
    'eu-north-1': timezone('Europe/Berlin'),
    'me-south-1': timezone('Asia/Qatar'),
    'me-central-1': timezone('Asia/Dubai'),
    'sa-east-1': timezone('America/Sao_Paulo')
}


def region_midnight(item: dict) -> bool:
    """Check if the it is between 00:00 and 01:00 in the timezone of the stacks
    AWS region

    Parameters
    ----------
    item : dict
        Single entry pulled from the activation table

    Returns
    -------
    bool
        True if midnight, False if not
    """
    now = datetime.now(region_time_map[item['region']['S']])
    if now.hour != 0:
        # Do not upgrade if the time is not midnight in the AWS region
        print(f'{item["serialNumber"]["S"]} in {item["region"]["S"]} cant be '
              f'updated yet, not yet midnight locally. Hour is {now.hour}')
        return False
    else:
        return True


def main(dynamodb_table: str, aws_region: str, event_bus_name: str):
    """Updates all FSIEM cloud deployments with the latest terraform code

    Parameters
    ----------
    dynamodb_table : str
        The name of the dynamodb table
    dynamodb_region : str
        The AWS region where resources are located
    event_bus_name : str
        The name of the EventBridge event bus
    """
    activation_table = ActivationTable(dynamodb_table, aws_region)
    eventbridge = EventBridge(event_bus_name)
    items = activation_table.get_all_items()

    events = []
    for item in items:
        if not region_midnight(item):
            continue
        event = eventbridge.get_deploy_event(item, check_prevent=True)
        if event:
            events.append(event)

    if not events:
        print('No deployments are valid to be updated, exiting')
        return
    eventbridge.send_events(events, aws_region)


def parse_args() -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Updates all FSIEM cloud deployments with the latest '
                   'terraform code')
    parser = ArgumentParser(description=description)
    parser.add_argument('--dynamodb_table', type=str, required=True,
                        help='The name of the dynamodb table')
    parser.add_argument('--aws_region', type=str, required=True,
                        help='The AWS region where resources are located')
    parser.add_argument('--event_bus_name', type=str, required=True,
                        help='The name of the EventBridge event bus')
    return parser.parse_args()


if __name__ == '__main__':
    # Usage:
    # python3 main.py                                        \
    # --dynamodb_table  "fsiem_activation_table_playground"  \
    # --dynamodb_region "us-east-1"                          \
    # --event_bus_name "portal-bus-playground"
    config = parse_args()
    main(config.dynamodb_table, config.aws_region, config.event_bus_name)
