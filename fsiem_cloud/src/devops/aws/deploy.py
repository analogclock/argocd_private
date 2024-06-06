from argparse import ArgumentParser
from fsiem_api_client import ActivationTable, EventBridge

# This script automates the process of triggering the deploy container to
# update or delete an FSIEM Cloud deployment. It does so by reading the
# deployments entry in the dynamodb activation table to create an event for
# eventbridge. It then places the event on the eventbridge event bus which
# triggers the deploy container to update or delete the deployment.


def main(options: dict):
    event_bus = f'portal-bus-{options["environment"]}'
    activation_table = f'fsiem_activation_table_{options["environment"]}'
    eventbridge = EventBridge(event_bus)
    db = ActivationTable(activation_table, options['region'])
    item = db.get_full_item(options['serial_number'])
    event = eventbridge.get_deploy_event(
        item, deploy_type=options['event_type'])
    if options['dry_run'] == 'false':
        eventbridge.send_events([event], options['region'])
    else:
        print(event)


def parse_args() -> ArgumentParser:
    """Parses the parameters when the script is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Update or delete an FSIEM Cloud deployment')
    parser = ArgumentParser(description=description)
    parser.add_argument('--environment', type=str, default='dev',
                        choices=['dev', 'playground', 'prod'],
                        help='The environment the deployment is located in')
    parser.add_argument('--region', type=str, default='us-east-1',
                        help='The region the Portal is located in')
    parser.add_argument('--serial_number', type=str,
                        default='FSMCLD0000000101',
                        help='The serial number of the target deployment')
    parser.add_argument('--event_type', type=str,
                        default='UPDATE', choices=['UPDATE', 'DELETE'],
                        help=('The event type to create, either to update the '
                              'deployment or to delete it, default UPDATE'))
    parser.add_argument('--dry_run', type=str,
                        default='false', choices=['true', 'false'],
                        help=('If set to true then it will not send the event '
                              'but just print it to console, default false'))
    return parser.parse_args()


if __name__ == '__main__':
    config = parse_args()
    main(vars(config))
