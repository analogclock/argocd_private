from collector import add_org_collectors_to_super, provision_collectors

# Action name to function dictionary
supported_commands = {
    'add_org_collectors_to_super': add_org_collectors_to_super,
    'provision_collectors': provision_collectors
}


def lambda_handler(event, context):
    """Main lambda method (entry point)"""
    # Serial number and command are passed in the event
    sn = event["SerialNumber"]
    command = event['Command']

    print(f'Execute {command} for {sn}')
    print(f'Event data: {event}')

    if not sn:
        raise ValueError('Serial number is None or empty')
    if command not in supported_commands:
        raise ValueError(f'Command {command} is not supported')

    # Execute command that we received in the event
    # Pass the event itself as an arg to a function
    # based on https://stackoverflow.com/a/7937987/706456
    supported_commands[command](event)
    return {
        'body': f'{command} executed successfully for event {event}'
    }
