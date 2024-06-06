# Lambda source handler to invoke different python scripts

from check_serial_number import check_serial_number
from backup_instances import backup_instances
from delete_alb_sg_in_rules import delete_alb_sg_in_rules
from add_alb_sg_in_rules import add_alb_sg_in_rules
from invoke_fmon_maintenance import invoke_fmon_maintenance
from terminate_fmon_maintenance import terminate_fmon_maintenance

# Action name to function dictionary
# User passes a name 'backup_instances', we call a function backup_instances()
supported_commands = {
    'check_serial_number': check_serial_number,
    'backup_instances': backup_instances,
    'add_alb_sg_in_rules': add_alb_sg_in_rules,
    'delete_alb_sg_in_rules': delete_alb_sg_in_rules,
    'invoke_fmon_maintenance': invoke_fmon_maintenance,
    'terminate_fmon_maintenance': terminate_fmon_maintenance
}


def lambda_handler(event, context):
    """Main lambda method (entry point)"""
    # Serial number and command are passed in the event
    sn = event["SerialNumber"]
    command = event['ScriptName']

    print(f'Execute {command} for {sn}')
    print(f'Event data: {event}')

    if not sn:
        raise ValueError('Serial number is None or empty')
    if command not in supported_commands:
        raise ValueError('Command {command} is not supported')

    # Execute command that we received in the event
    # Pass the event itself as an arg to a function
    # based on https://stackoverflow.com/a/7937987/706456
    supported_commands[command](event)
    return {
        'body': f'{command} executed successfully for event {event}'
    }
