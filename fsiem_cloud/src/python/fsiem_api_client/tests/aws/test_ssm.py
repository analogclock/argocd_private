import pytest
from moto import mock_aws
from fsiem_api_client.aws.ssm import Ssm


class TestSsm:
    inst_id = 'i-0ce99cc45635d63cb'
    uuid = 'f20822af-3733-4b17-b4d6-f08dc48de463'
    success_resp = '[ \'output\', \'Success\', 0]\n'

    def test_ctor(self):
        assert Ssm(region='us-east-1').client

    @mock_aws
    def test_send_cmd(self):
        with pytest.raises(ValueError):
            actual = Ssm(region='us-east-1').send_cmd([], ['lsblk'])
        with pytest.raises(ValueError):
            actual = Ssm(region='us-east-1').send_cmd([self.inst_id], [])
        actual = Ssm(region='us-east-1').send_cmd([self.inst_id], ['lsblk'])
        assert actual

    @mock_aws
    def test_get_output(self):
        with pytest.raises(ValueError):
            Ssm(region='us-east-1').get_output('', 'lsblk')
        with pytest.raises(ValueError):
            Ssm(region='us-east-1').get_output(self.inst_id, '')
