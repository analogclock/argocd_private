from fsiem_api_client.util import get_client
from fsiem_api_client.fsiem_api import FsiemApi
from pytest import fail
from fsiem_setup.fsiem_api import (clickhouse_super_setup, clickhouse_config,
                                   clickhouse_get_new_workers,
                                   clickhouse_has_new_workers,
                                   clickhouse_worker_setup)
from fsiem_api_client.const import (super_disk_sizes, worker_disk_sizes,
                                    keeper_disk_sizes)


class TestFsiemApi:

    supper = 'https://fsmcld0000000154.playground.fortisiem.cloud'
    region = 'us-east-1'
    sn = 'FSMCLD0000000154'
    email = "test@test.com"
    password = 'Fortinet*11'
    worker_ips = ['10.0.101.240']
    s3_bucket = 'fsiem-clickhouse-data-us-east-1-playground/FSMCLD0000000154'
    s3_region = 'us-east-1'
    secret_id = 'fsiem-vm-auth-creds-playground'
    cognito_url = 'https://forticloud-fsiem-playground.auth.us-east-1.amazoncognito.com' # noqa

    def get_fsiem(self) -> FsiemApi:
        fsiem_api = get_client(self.supper, self.secret_id, self.cognito_url,
                               1, True)
        if not fsiem_api:
            fail('Cannot authenticate, check password')
        return fsiem_api

    def test_clickhouse_super_setup(self):
        api = self.get_fsiem()
        clickhouse_super_setup(api, super_disk_sizes, self.region,
                               self.sn, self.password, self.email)

    def test_clickhouse_worker_setup(self):
        api = self.get_fsiem()
        clickhouse_worker_setup(
            api, worker_disk_sizes, keeper_disk_sizes, self.region,
            self.sn, self.worker_ips, self.s3_bucket, self.s3_region)

    def test_clickhouse_config(self):
        api = self.get_fsiem()
        clickhouse_config(api, super_disk_sizes, worker_disk_sizes,
                          keeper_disk_sizes, self.region,
                          self.sn, self.password, self.email)

    def test_clickhouse_get_new_workers(self):
        api = self.get_fsiem()
        ip = ['123.123.123.123']
        actual = clickhouse_get_new_workers(api, worker_disk_sizes, ip)
        assert actual == ip

    def test_clickhouse_has_new_workers(self):
        api = self.get_fsiem()
        ip = ['123.123.123.123']
        assert clickhouse_has_new_workers(api, worker_disk_sizes, ip)
        assert not clickhouse_has_new_workers(api, worker_disk_sizes, [])
