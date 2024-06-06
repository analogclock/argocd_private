# Program to backup the super & workers instances
import boto3


def backup_instances(event):
    sts = boto3.client('sts')
    region = boto3.Session().region_name
    account_id = sts.get_caller_identity()['Account']
    client = boto3.client('backup')
    instances = event['Workers'] + event['Supers']
    BackupVaultName = event['BackupVaultName']
    IamRoleArn = event['IamRoleArn']
    DeleteAfterDays = event['DeleteAfterDays']
    for instance in instances:
        client.start_backup_job(
            BackupVaultName=BackupVaultName,
            ResourceArn=(
                f'arn:aws:ec2:{region}:{account_id}:instance/{instance}'),
            IamRoleArn=IamRoleArn,
            Lifecycle={
                        'DeleteAfterDays': DeleteAfterDays
            }
        )
    return
