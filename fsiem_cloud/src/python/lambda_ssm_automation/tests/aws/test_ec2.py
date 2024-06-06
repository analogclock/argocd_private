import pytest
import json
from aws.ec2 import Ec2


class TestEc2:

    uut = Ec2('us-east-1')

    def test_ip_permissions_json_args_error(self):
        with pytest.raises(ValueError):
            self.uut.ip_permissions_json('foo', [])
        with pytest.raises(ValueError):
            self.uut.ip_permissions_json('Ipv4', [])

    def test_ip_permissions_json_v4(self):
        cidr_nets = ['10.1.1.1/32', '76.54.23.32/16']
        expected = [{
            'FromPort': 443,
            'ToPort': 443,
            'IpProtocol': 'tcp',
            'IpRanges': [
               {
                   "CidrIp": "10.1.1.1/32",
                   "Description": "Load balancer access from external networks"
               },
               {
                   "CidrIp": "76.54.23.32/16",
                   "Description": "Load balancer access from external networks"
               }
            ]
        }]
        actual = self.uut.ip_permissions_json('Ipv4', cidr_nets)
        assert json.dumps(expected) == json.dumps(actual)

    def test_ip_permissions_json_v6(self):
        cidr_nets = ['00:aa:bb/8', '00:01:09:03/4']
        expected = [{
            'FromPort': 443,
            'ToPort': 443,
            'IpProtocol': 'tcp',
            'Ipv6Ranges': [
                {
                   "CidrIpv6": "00:aa:bb/8",
                   "Description": "Load balancer access from external networks"
                },
                {
                   "CidrIpv6": "00:01:09:03/4",
                   "Description": "Load balancer access from external networks"
                }
            ]
        }]
        actual = self.uut.ip_permissions_json('Ipv6', cidr_nets)
        assert json.dumps(expected) == json.dumps(actual)
