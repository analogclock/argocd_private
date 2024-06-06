from fsiem_api_client.aws.ec2 import Ec2


class TestEc2:

    sn = 'FSMCLD0000000154'
    uut = Ec2(region='us-east-1')

    def test_instance_ids(self):
        resp = self.uut.get_instance_ids(self.sn, 'super')
        assert resp

    def test_instance_info(self):
        resp = self.uut.get_instance_info(self.sn, 'super')
        for item in resp:
            assert item['PrivateDnsName']

    def test_instance_info_dns(self):
        dns_name = 'ip-10-0-101-210.ec2.internal'
        resp = self.uut.get_instance_info_from_dns(self.sn, dns_name)
        for item in resp:
            assert item['PrivateDnsName'] == dns_name
