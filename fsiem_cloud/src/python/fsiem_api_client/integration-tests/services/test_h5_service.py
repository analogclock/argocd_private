import pytest
from fsiem_api_client.services.h5_service import H5_ACTION_TYPE, H5Service
from providers import ClientProvider


class TestH5Service:

    def test_update_org_bucket_mapping(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            resp = uut.update_org_bucket_mapping()
            assert resp.text == '"OK"'

    def test_clickhouse_check_storage(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            assert uut.clickhouse_check_storage()

    def test_clickhouse_super_test(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            with pytest.raises(ValueError) as er:
                uut.clickhouse_super(
                    ['1'], None, '1', '1', H5_ACTION_TYPE.TEST)
            assert 'Unknown code 1' in er.value.args[0]

    def test_clickhouse_super_save(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            try:
                uut.clickhouse_super_save(
                    ['1'], None, '1', '1', H5_ACTION_TYPE.ADD)
            except Exception as er:
                assert 'Failed' in er.args[0]

    def test_clickhouse_worker_test(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            with pytest.raises(Exception):
                uut.clickhouse_worker(
                    ['1'], None, '1', '1', '1', '1', H5_ACTION_TYPE.TEST)

    def test_clickhouse_worker_save(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            with pytest.raises(Exception):
                uut.clickhouse_worker(
                    ['1'], None, '1', '1', '1', '1', H5_ACTION_TYPE.ADD)

    def test_clickhouse_config_test(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            with pytest.raises(ValueError):
                tmp = [{'ClickHouseDiskPaths': '1', 'PrivateIpAddress': '1'}]
                uut.clickhouse_config(
                    tmp, tmp, tmp, '1', '1', H5_ACTION_TYPE.TEST)

    def test_clickhouse_config_save(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            with pytest.raises(ValueError):
                tmp = [{'ClickHouseDiskPaths': '1', 'PrivateIpAddress': '1'}]
                uut.clickhouse_config(
                    tmp, tmp, tmp, '1', '1', H5_ACTION_TYPE.ADD)

    def test_clickhouse_s3_archive_test(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            with pytest.raises(ValueError):
                uut.clickhouse_s3_archive('foo', 'bar', H5_ACTION_TYPE.TEST)

    def test_clickhouse_s3_archive_save(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            resp = uut.clickhouse_s3_archive('foo', 'bar', H5_ACTION_TYPE.ADD)
            assert resp.text == '"OK"'

    def test_check_old_workers(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            resp = uut.check_old_workers(['foo'])
            assert resp == ['foo']

    def test_add_worker(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            with pytest.raises(ValueError):
                uut.add_worker('foo')

    def test_get_version(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            assert uut.get_version()

    def test_get_uuid(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            assert uut.get_uuid()

    def test_upload_license(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = H5Service(client.http, client.super_url)
            with pytest.raises(ValueError) as er:
                uut.upload_license('foo', b'foo', 'foo', 'fake-password')
            # Tried to insert a licence, but pwd is wrong
            assert 'Invalid password' in er.value.args[0]
