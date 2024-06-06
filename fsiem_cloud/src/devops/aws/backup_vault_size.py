import boto3

vault_name = 'prod-vault'
region = 'eu-west-1'


def bytes_to_tb(size: int) -> int:
    """Turns a byte value into a TerraByte value, rounded down to the nearest
    TB

    Parameters
    ----------
    size : int
        Byte value

    Returns
    -------
    int
        TB Value
    """
    return size // (1024 * 1024 * 1024 * 1024)


client = boto3.client('backup', region_name=region)

total = 0
efs_size_bytes = 0
ebs_size_bytes = 0
ec2_size_bytes = 0
unknown_size_bytes = 0

response = client.list_recovery_points_by_backup_vault(
    BackupVaultName=vault_name,
    MaxResults=100
)

while True:

    for point in response['RecoveryPoints']:
        if point['Status'] != 'COMPLETED':
            continue

        if point['ResourceType'] == 'EFS':
            efs_size_bytes += point['BackupSizeInBytes']
        elif point['ResourceType'] == 'EBS':
            ebs_size_bytes += point['BackupSizeInBytes']
        elif point['ResourceType'] == 'EC2':
            ec2_size_bytes += point['BackupSizeInBytes']
        else:
            unknown_size_bytes += point['BackupSizeInBytes']
        total += point['BackupSizeInBytes']

    if "NextToken" not in response:
        break
    else:
        response = client.list_recovery_points_by_backup_vault(
            NextToken=response['NextToken'],
            BackupVaultName=vault_name,
            MaxResults=100
        )

print(f'Total size  : {total}   {bytes_to_tb(total)} TB')
print(f'EFS size    : {efs_size_bytes}    {bytes_to_tb(efs_size_bytes)} TB')
print(f'EBS size    : {ebs_size_bytes}    {bytes_to_tb(ebs_size_bytes)} TB')
print(f'AMI size    : {ec2_size_bytes}    {bytes_to_tb(ec2_size_bytes)} TB')
print(f'Unknown size: {unknown_size_bytes}')
