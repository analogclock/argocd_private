import boto3
from botocore.exceptions import WaiterError
from dataclasses import dataclass


TIMEOUT_1_HOUR_IN_SECONDS = 60 * 60 * 1
TIMEOUT_23_HOURS_IN_SECONDS = 60 * 60 * 23


@dataclass
class SsmCmdResponse:
    """AWS Ssm command execution response"""
    output: str = ''        # Standard out from the executed command
    status: str = ''        # Success or Failed
    response_code: int = 0  # Program exit code, usually 0 for success
    instance_id: str = ''   # Instance id where this command has run
    error: str = ''         # Standard error from the executed command


class Ssm:
    """A client class for AWS SSM."""

    status_success = ['Success', 'CompletedWithSuccess']
    status_failure = ['Failed', 'TimedOut', 'Cancelled', 'Rejected',
                      'CompletedWithFailure']

    def __init__(self, region: str) -> None:
        self.client = boto3.client('ssm', region_name=region)

    def send_cmd(self, instance_ids: list, shell_cmd: list,
                 execution_timeout_sec=TIMEOUT_1_HOUR_IN_SECONDS) -> str:
        """Execute AWS SSM AWS-RunShellScript document with provided commands

        Parameters
        ----------
        instance_ids : list
            A list of AWS EC2 instance ids, e.g. ['i-0ce99cc45635d63cb']

        shell_cmd : list
            A single command, e.g.:
                [ 'lsblk' ]
            Several commands wrapped in brackets, e.g.:
                [ '(lsblk | grep nvme)' ]
            Multiple independent commands, e.g.:
                [ 'lsblk', 'ifconfig']

            Note: if you want to pipe output between commands, you may need
                to use this syntax with escaping chars, e.g.:
                [ '(lsblk | grep \042nvme\042)' ]
                where \042 is an ASCII octal value for a quote char.

        execution_timeout_sec: int
            Number of seconds for command to finish, default to 1 hour in sec.

        Returns
        -------
        str
            a UUID of the scheduled command
        """
        if not instance_ids:
            raise ValueError('instance_ids is empty')
        if not shell_cmd:
            raise ValueError('shell_cmd is empty')

        print(f'Running AWS shell script {shell_cmd} on {instance_ids}')
        resp = self.client.send_command(
            InstanceIds=instance_ids,
            Parameters={
                'commands': shell_cmd,
                'executionTimeout': [str(execution_timeout_sec)]
            },
            TimeoutSeconds=execution_timeout_sec,
            DocumentName='AWS-RunShellScript')
        cmd_id = resp['Command']['CommandId']
        return cmd_id

    def get_output(self, instance_id: str, cmd_id: str) -> SsmCmdResponse:
        """Retrieve the result of a remote command, based on command UUID

        Parameters
        ----------
        instance_ids : str
            AWS EC2 instance id, e.g. 'i-0ce99cc45635d63cb'

        cmd_id : str
            UUID of the command

        Returns
        -------
        SsmCmdResponse
            Output string, Status (Success/Failed), ResponseCode (exit code)
        """
        if not instance_id:
            raise ValueError('instance_id is empty')
        if not cmd_id:
            raise ValueError('cmd_id is empty')
        try:
            waiter = self.client.get_waiter("command_executed")
            waiter.wait(CommandId=cmd_id, InstanceId=instance_id)
        except WaiterError as e:
            print(f'Waiter error: {e}, last response: {e.last_response}')
        resp = self.client.get_command_invocation(
            CommandId=cmd_id, InstanceId=instance_id)
        response_code = resp['ResponseCode']
        output = resp['StandardOutputContent']
        err = resp['StandardErrorContent']
        status = resp['Status']
        if response_code != 0:
            raise ValueError(f'Failed, code { response_code }, err: {err}')
        return SsmCmdResponse(output, status, response_code)

    def exec_command(self, instance_id: str, cmd: str) -> SsmCmdResponse:
        """Execute commands on the remote EC2 instance"""
        if not instance_id:
            raise ValueError('instance_id is empty')
        if not cmd:
            raise ValueError('cmd is empty')

        id = self.send_cmd([instance_id], [cmd])
        return self.get_output(instance_id, id)

    def exec_commands(self, instance_ids: list[str],
                      cmd: list[str],
                      execution_timeout_sec=TIMEOUT_1_HOUR_IN_SECONDS,
                      **waiter_config) -> list[SsmCmdResponse]:
        """Execute multiple commands on the remote EC2 instances"""
        if not instance_ids:
            raise ValueError('instance_ids is empty')
        if not cmd:
            raise ValueError('cmd is empty')

        # Schedule commands for execution
        print(f'Running AWS shell script {cmd} on {instance_ids}')
        responses = self.client.send_command(
            InstanceIds=instance_ids,
            TimeoutSeconds=execution_timeout_sec,
            Parameters={
                'commands': cmd,
                'executionTimeout': [str(execution_timeout_sec)]
            },
            DocumentName='AWS-RunShellScript')
        cmd_id = responses['Command']['CommandId']
        print(f'Command_id: {cmd_id}')

        # Wait for all to finish
        try:
            waiter = self.client.get_waiter("command_executed")
            for instance_id in instance_ids:
                # If waiter config isn't provided (None), the default value is
                #
                #     {'Delay': 5, 'MaxAttempts': 20 }
                #
                # If you run a long-running operation, pass in different value,
                # for example: check every minute for 24 hours looks like:
                #
                #     {'Delay': 60, 'MaxAttempts': 1440 }
                #
                # See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/waiter/CommandExecuted.html # noqa
                waiter.wait(CommandId=cmd_id, InstanceId=instance_id,
                            WaiterConfig=waiter_config)
        except WaiterError as err:
            print('One of the commands failed, last command status')
            print(err.last_response)
            raise err

        # Retrieve results
        responses: list[SsmCmdResponse] = []
        for instance_id in instance_ids:
            r = self.client.get_command_invocation(
                CommandId=cmd_id, InstanceId=instance_id)
            cmd_resp = SsmCmdResponse(
                instance_id=r['InstanceId'],
                output=r['StandardOutputContent'],
                error=r['StandardErrorContent'],
                status=r['Status'],
                response_code=r['ResponseCode'])
            if cmd_resp.response_code != 0:
                raise ValueError(
                    f'Failed to execute command on {cmd_resp.instance_id}, '
                    f'code { cmd_resp.response_code }, '
                    f'error {cmd_resp.error}')
            responses.append(cmd_resp)
            print(f'Response:{responses}')
        return responses

    def start_automation(self, doc_name: str, parameters: dict,
                         target_region: str, automation_role_name: str) -> str:
        """Start an SSM automation

        Parameters
        ----------
        doc_name : str
            The name of the SSM doc to run the automation with
        parameters : dict
            The parameters of the SSM doc
        target_region : str
            The region to run the document in
        automation_role_name : str
            The name of the IAM role to run the automation

        Returns
        -------
        str
            Execution ID of the automation
        """
        print(f'Triggering execution with SSM document: {doc_name}')
        aws_account = boto3.client('sts').get_caller_identity().get('Account')
        response = self.client.start_automation_execution(
            DocumentName=doc_name,
            Parameters=parameters,
            TargetLocations=[
                {
                    'Accounts': [aws_account],
                    'Regions': [target_region],
                    'ExecutionRoleName': automation_role_name
                }
            ]
        )

        return response['AutomationExecutionId']

    def get_automation_status(self, execution_id: str) -> str:
        """Get the current status of the automation execution

        Parameters
        ----------
        execution_id : str
            The ID of the automation execution
        region : str
            The region to run the automation

        Returns
        -------
        str
            The status of the automation execution
        """
        print(f'Finding automation status for execution ID {execution_id}')
        response = self.client.describe_automation_executions(
            Filters=[
                {
                    'Key': 'ExecutionId',
                    'Values': [execution_id]
                }
            ]
        )
        # 'Pending'|'InProgress'|'Waiting'|'Success'|'TimedOut'|'Cancelling'|'Cancelled'|'Failed'|'PendingApproval'|'Approved'|'Rejected'|'Scheduled'|'RunbookInProgress'|'PendingChangeCalendarOverride'|'ChangeCalendarOverrideApproved'|'ChangeCalendarOverrideRejected'|'CompletedWithSuccess'|'CompletedWithFailure'
        automations = response['AutomationExecutionMetadataList']

        if not automations:
            print(f'Could not find automation ID {execution_id}')
            return None
        status = automations[0]['AutomationExecutionStatus']
        print(f'Status of automation ID {execution_id} is {status}')
        return status
