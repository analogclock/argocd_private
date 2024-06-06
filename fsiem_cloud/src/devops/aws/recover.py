import boto3
import string
from random import choices
from argparse import ArgumentParser
from json import loads, dumps
from time import sleep


def trim_metadata(metadata: dict) -> dict:
    """The metadata we get from get_recovery_point_restore_metadata contains
    several fields that will be rejected by start_restore_job. This function
    removes them

    Parameters
    ----------
    metadata : dict
        The metadata retrieved from get_recovery_point_restore_metadata

    Returns
    -------
    dict
        Metadata with redundant fields removed

    Raises
    ------
    Exception
        If the instance somehow has more than one network interface the code
        cant currently handle it
    """
    # Fields to keep from metadata
    metadata_list = [
        'VpcId', 'Monitoring', 'CapacityReservationSpecification',
        'InstanceInitiatedShutdownBehavior', 'DisableApiTermination',
        'HibernationOptions', 'EbsOptimized', 'Placement', 'InstanceType',
        'NetworkInterfaces'
    ]
    new_metadata = {}
    for key in metadata_list:
        new_metadata[key] = metadata[key]

    # Remove redundant fields from NetworkInterfaces
    network_interfaces = loads(new_metadata['NetworkInterfaces'])
    if len(network_interfaces) > 1:
        raise Exception('Instance has more than 1 network interface, this '
                        'script cannot handle that')
    del network_interfaces[0]['AssociatePublicIpAddress']
    del network_interfaces[0]['PrivateIpAddress']
    del network_interfaces[0]['SecondaryPrivateIpAddressCount']
    del network_interfaces[0]['NetworkInterfaceId']
    new_metadata['NetworkInterfaces'] = dumps(network_interfaces)
    return new_metadata


def get_iam_role(iam_role: str) -> str:
    """Check if the IAM role is specified in the args, if not it will try to
    find the default AWS role AWSBackupDefaultServiceRole

    Parameters
    ----------
    iam_role : str
        The value of the iam_role arg, if not set it will be None

    Returns
    -------
    str
        Either the role specified in iam_role, if set, or the arn of the
        default AWS role

    Raises
    ------
    e
        Exception finding the role AWSBackupDefaultServiceRole
    """
    # Check if --iam_role is specified, if not it will try and find the
    # default AWS role
    if iam_role:
        role = iam_role
    else:
        iam_client = boto3.client('iam')
        try:
            default_role = 'AWSBackupDefaultServiceRole'
            response = iam_client.get_role(
                RoleName=default_role
            )
            role = response['Role']['Arn']
        except Exception as e:
            print(f'Error finding default IAM role {default_role}')
            raise e
    return role


def restore_instance(recovery_point: str, metadata: dict, role: str,
                     region: str) -> str:
    """Creates a new instance from the recovery point

    Parameters
    ----------
    recovery_point : str
        The ARN of the recovery point in AWS backup
    metadata : dict
        The prepared metadata from trim_metadata
    role : str
        The IAM role with which to execute the recovery
    region : str
        The AWS region in which the backup exists and in which it will be
        restored

    Returns
    -------
    str
        The instance ID of the restored instance
    """
    # generates a random 10 character string for IdempotencyToken
    token = ''.join(choices(string.ascii_uppercase + string.digits, k=10))

    backup_client = boto3.client('backup', region_name=region)
    response = backup_client.start_restore_job(
        RecoveryPointArn=recovery_point,
        Metadata=metadata,
        IamRoleArn=role,
        IdempotencyToken=token
    )
    job_id = response['RestoreJobId']

    # Wait for job to succeed or fail
    while True:
        response = backup_client.describe_restore_job(
            RestoreJobId=job_id
        )
        status = response['Status']
        if status != 'PENDING' and status != 'RUNNING':
            print(f'Restore job {job_id} finished with status {status}')
            break
        print(f'Restore job {job_id} still running with status: {status}')
        sleep(5)
    instance_arn = response['CreatedResourceArn']
    instance_id = instance_arn.split('/')[-1]
    return instance_id


def parse_args() -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Restores an FSIEM cloud AWS instance')
    parser = ArgumentParser(description=description)
    parser.add_argument('--vault_name', type=str, required=True,
                        help='The name of the Backup Vault')
    parser.add_argument('--region', type=str, required=True,
                        help='The AWS region where the vault is located')
    parser.add_argument('--iam_role', type=str, required=False,
                        help=('The ARN of the IAM role to use for the restore.'
                              'If none is set then it will default to using '
                              'the AWS role AWSBackupDefaultServiceRole.'))
    parser.add_argument('--recovery_point', type=str, required=True,
                        help='The ARN of the backup')
    return parser.parse_args()


def main():
    """Restores an FSIEM cloud AWS instance
    """
    # TODO Add preventUpdate flag to activation table

    config = parse_args()
    backup_client = boto3.client('backup', region_name=config.region)

    response = backup_client.get_recovery_point_restore_metadata(
        BackupVaultName=config.vault_name,
        RecoveryPointArn=config.recovery_point
    )
    metadata = response['RestoreMetadata']
    iam_profile = metadata['IamInstanceProfileName']

    new_metadata = trim_metadata(metadata)

    role = get_iam_role(config.iam_role)

    instance_id = restore_instance(
        config.recovery_point, new_metadata, role, config.region
    )

    # We add the profile AFTER instance creation as the instance role is
    # missing some permissions that let it be assigned during restore
    ec2_client = boto3.client('ec2', region_name=config.region)
    response = ec2_client.associate_iam_instance_profile(
        IamInstanceProfile={
            'Name': iam_profile
        },
        InstanceId=instance_id
    )
    # TODO Update terraform state with new resources
    # TODO Run the deploy container against this stack
    # TODO Remove preventUpdate flag to activation table


if __name__ == '__main__':
    # Usage:  python3 -u main.py --vault_name dev-vault --region us-east-1 \
    # --iam_role arn:aws:iam:::role/service-role/AWSBackupDefaultServiceRole \
    # --recovery_point arn:aws:ec2:us-east-1::image/ami-00576324591b7f8ca
    main()
