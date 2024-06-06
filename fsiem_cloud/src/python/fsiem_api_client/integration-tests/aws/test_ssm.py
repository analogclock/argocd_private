import pytest
from fsiem_api_client.aws.ssm import Ssm


class TestSsm:

    # Put a valid currently running EC2 instance and region.
    inst_id = 'i-0a5dc95e72d3bca3f'
    uut = Ssm(region='us-east-1')

    def test_send_cmd(self):
        resp = self.uut.send_cmd([self.inst_id], ['ifconfig'])
        assert len(resp) > 0

    def test_get_output(self):
        resp = self.uut.send_cmd([self.inst_id], ['ifconfig'])
        resp = self.uut.get_output(self.inst_id, resp)
        assert len(resp.output) > 0

    def test_multiple_get_output(self):
        resp = self.uut.send_cmd([self.inst_id],
                                 ['(lsblk | grep \042nvme\042)'])
        resp = self.uut.get_output(self.inst_id, resp)
        assert resp.output.find('nvme') >= 0

    def test_get_output_wrong_cmd(self):
        resp = self.uut.send_cmd([self.inst_id], ['this-command-not-exist'])
        with pytest.raises(ValueError):
            self.uut.get_output(self.inst_id, resp)

    def test_clickhouse_get_archive_size(self):
        query = """clickhouse-client --query="
            SELECT sum(bytes_on_disk)
            FROM system.parts
            WHERE disk_name='archive'"
        """
        resp = self.uut.send_cmd(['i-050829cbb66275924'], [query])
        resp = self.uut.get_output('i-050829cbb66275924', resp)
        archive_size1 = int(resp.output)
        assert archive_size1 >= 0

        resp = self.uut.send_cmd(['i-037eeec004c499d4d'], [query])
        resp = self.uut.get_output('i-037eeec004c499d4d', resp)
        archive_size2 = int(resp.output)
        assert archive_size2 >= 0

        total = archive_size1 + archive_size2

        assert total >= 0

    def test_start_automation(self):
        parameters = {
            'SerialNumber': 'FSMCLD<id>',
            'ExternalStorage': 'fsiem-external-storage'
        }
        exec_id = self.uut.start_automation(
            'fsiem_test_ext_storage_playground', parameters, 'us-east-1',
            'iam_role_name'
        )
        assert exec_id
