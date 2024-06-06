import boto3
from typing import Any


class Ec2:
    """A helper class for EC2 service"""
    ec2_resource: Any

    def __init__(self, region: str) -> None:
        self.ec2_resource = boto3.resource("ec2", region_name=region)

    def get_sg(self, id: str):
        return self.ec2_resource.SecurityGroup(id)

    def ip_permissions_json(self, ip_type: str, cidr_nets: list) -> list:
        """Make ipv4 or ipv6 inbound rules for ALB's security group"""
        if ip_type not in ['Ipv4', 'Ipv6']:
            raise ValueError(f'Unexpected ip type: {ip_type}')
        if not cidr_nets:
            raise ValueError('CIDR network not provided')

        ip_range = 'IpRanges' if ip_type == 'Ipv4' else 'Ipv6Ranges'
        cidr_ip = 'CidrIp' if ip_type == 'Ipv4' else 'CidrIpv6'
        values = []
        for cidr_net in cidr_nets:
            values.append({
                cidr_ip: cidr_net,
                'Description': 'Load balancer access from external networks'})
        return [{
            'FromPort': 443,
            'ToPort': 443,
            'IpProtocol': 'tcp',
            ip_range: values
        }]

    def authorize_ingress(self, sg_id: str, cidr_networks: list, ip_type: str):
        """Add ipV4 and ipV6 inbound rules to the ALB's security group

        Parameters
        ----------
        sg_id : str
            Security group id, e.g.: sg-0001
        cidr_networks : list
            List of CIDR networks, e.g. ['1.2.3.4/32', '2.2.3.4/24]
        ip_type : str
            CIDR network type: Ipv4 or Ipv6
        """
        if not cidr_networks:
            raise ValueError('CIDR is None, cannot be added to a sg')
        if ip_type not in ['Ipv4', 'Ipv6']:
            raise ValueError(f'Unexpected ip type: {ip_type}')
        if not sg_id:
            raise ValueError('Security group id is None')
        sg = self.get_sg(sg_id)
        data = self.ip_permissions_json(ip_type, cidr_networks)
        sg.authorize_ingress(GroupId=sg_id, IpPermissions=data)
        print(f"{cidr_networks} were added to security group {sg_id}")

    def revoke_ingress(self, sg_id: str, cidr_networks: list, ip_type: str):
        """Delete ipV4 and ipV6 inbound rules to the ALB's security group

        Parameters
        ----------
        sg_id : str
            Security group id, e.g.: sg-0001
        cidr_networks : list
            List of CIDR networks, e.g. ['1.2.3.4/32', '2.2.3.4/24]
        ip_type : str
            CIDR network type: Ipv4 or Ipv6
        """
        if not cidr_networks:
            raise ValueError('CIDR is None, cannot be deleted from a sg')
        if ip_type not in ['Ipv4', 'Ipv6']:
            raise ValueError(f'Unexpected ip type: {ip_type}')
        if not sg_id:
            raise ValueError('Security group id is None')
        sg = self.get_sg(sg_id)
        data = self.ip_permissions_json(ip_type, cidr_networks)
        sg.revoke_ingress(GroupId=sg_id, IpPermissions=data)

        print(f"{cidr_networks} were deleted from security group {sg_id}")
