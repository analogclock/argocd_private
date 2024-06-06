import boto3


class Ec2:
    """A client class for AWS Ec2"""

    def __init__(self, region: str) -> None:
        self.client = boto3.client('ec2', region_name=region)

    def get_instance_ids(self, serial_number: str, role: str,
                         instance_states=['running']) -> list:
        """Get EC2 instance ids based on a serial number and a role.

        By default, this will return only running instances, as EC2 keeps
        terminated instances for about 1 hour.

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        role : str
            The instance role, super or worker
        instance_states: list
            A list of EC2 instance states: pending/running/terminated etc.

        Returns
        -------
        list
            List of instance ids
        """
        info = self.get_instance_info(serial_number, role, instance_states)
        return list(map(lambda x: x['InstanceId'], info))

    def get_instance_ips(self, serial_number: str, role: str,
                         instance_states=['running']) -> list:
        """Get EC2 instance private IPv4 addresses based on a serial number and
        a role.

        By default, this will return only running instances, as EC2 keeps
        terminated instances for about 1 hour.

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        role : str
            The instance role, super or worker
        instance_states: list
            A list of EC2 instance states: pending/running/terminated etc.

        Returns
        -------
        list
            List of instance IPv4 addresses
        """
        info = self.get_instance_info(serial_number, role, instance_states)
        return list(map(lambda x: x['PrivateIpAddress'], info))

    def get_instance_info(self, serial_number: str, role: str,
                          instance_states=['running']) -> list:
        """Get EC2 instance info based on a serial number and a role.

        By default, this will return only running instances, as EC2 keeps
        terminated instances for about 1 hour.

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        role : str
            The instance role, super or worker
        instance_states: list
            A list of EC2 instance states: pending/running/terminated etc.

        Returns
        -------
        list
            List of instance info: instance id, storage, network, tags, etc
            For example:
            [
                {
                    'InstanceId': 'i-0ec575a2459b51d26',
                    'InstanceType': 'c6i.xlarge',
                    'PrivateDnsName': 'ip-10-0-102-145.ec2.internal',
                    ... - other instance info
                }
            ]
        """
        print(f'Searching for running EC2 instance info with filtering'
              f' tag:Role={role}, and tag:SerialNumber={serial_number}')
        response = self.client.describe_instances(
            Filters=[
                {'Name': 'tag:SerialNumber', 'Values': [serial_number]},
                {'Name': 'tag:Role', 'Values': [role]},
                {
                    'Name': 'instance-state-name',
                    'Values': instance_states
                }
            ],
            MaxResults=1000
        )
        instance_info = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info.append(instance)
        print(f'Found {len(instance_info)} {role} instance(s) for deployment '
              f'{serial_number}')
        # [OM] Some operation require specific order of the data.
        # I found this when testing clickhouse configuration where
        # same private IP is mapped to an id. If this saved and retested,
        # id needs to be the same.
        return sorted(instance_info, key=lambda x: x['InstanceId'])

    def get_instance_info_from_id(self, instance_id: str,
                                  instance_states=['running']) -> list:
        """Get EC2 instance info based on the instance id

        Parameters
        ----------
        instance_id : str
            The ID of the instance
        instance_states : list, optional
            A list of EC2 instance states: pending/running/terminated etc.

        Returns
        -------
        list
            List of instance info: instance id, storage, network, tags, etc
            For example:
            [
                {
                    'InstanceId': 'i-0ec575a2459b51d26',
                    'InstanceType': 'c6i.xlarge',
                    'PrivateDnsName': 'ip-10-0-102-145.ec2.internal',
                    ... - other instance info
                }
            ]
        """
        print(f'Searching for running EC2 instance info with ID={instance_id}')
        response = self.client.describe_instances(
            InstanceIds=[
                instance_id
            ],
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': instance_states
                }
            ]
        )
        instance_info = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info.append(instance)
        print(f'Found {len(instance_info)} instance(s) for ID {instance_id}')
        return sorted(instance_info, key=lambda x: x['InstanceId'])

    def get_instance_info_from_dns(self, serial_number: str, dns: str,
                                   instance_states=['running']) -> list:
        """Get EC2 instance info based on a serial number and private dns name

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        dns : str
            The private dns name of the instance
        instance_states : list, optional
            A list of EC2 instance states: pending/running/terminated etc.

        Returns
        -------
        list
            List of instance info: instance id, storage, network, tags, etc
            For example:
            [
                {
                    'InstanceId': 'i-0ec575a2459b51d26',
                    'InstanceType': 'c6i.xlarge',
                    'PrivateDnsName': 'ip-10-0-102-145.ec2.internal',
                    ... - other instance info
                }
            ]
        """
        print(f'Searching for running EC2 instance info with filtering'
              f' dns-name={dns}, and tag:SerialNumber={serial_number}')
        response = self.client.describe_instances(
            Filters=[
                {'Name': 'tag:SerialNumber', 'Values': [serial_number]},
                {'Name': 'private-dns-name', 'Values': [dns]},
                {
                    'Name': 'instance-state-name',
                    'Values': instance_states
                }
            ],
            MaxResults=1000
        )
        instance_info = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info.append(instance)
        print(f'Found {len(instance_info)} {dns} instance(s) for deployment '
              f'{serial_number}')
        return sorted(instance_info, key=lambda x: x['InstanceId'])

    def get_security_group_ids(self, serial_number: str, role: str) -> list:
        """Get security group ids based on a serial number and a role

        Parameters
        ----------
        serial_number : str
            The serial number of the deployment
        role : str
            The security group role, i.e. super-alb

        Returns
        -------
        list
            List of security group ids
        """
        response = self.client.describe_security_groups(
            Filters=[
                {'Name': 'tag:SerialNumber', 'Values': [serial_number]},
                {'Name': 'tag:Role', 'Values': [role]},
            ],
            MaxResults=1000
        )
        group_ids = []
        for group in response['SecurityGroups']:
            group_ids.append(group['GroupId'])
        return group_ids
