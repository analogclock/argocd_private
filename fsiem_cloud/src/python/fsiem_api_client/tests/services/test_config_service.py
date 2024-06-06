import pytest
from fsiem_api_client.services.config_service import ConfigService
from fsiem_api_client.http_call import HttpCall


class TestConfigService:

    def test_ctor(self):
        with pytest.raises(ValueError):
            ConfigService(None, 'foo')
        with pytest.raises(ValueError):
            ConfigService(HttpCall(), None)
        uut = ConfigService(HttpCall(), 'foo')
        assert uut.super_url == 'foo'

    def test_set_deployment_type_cloud(self, requests_mock):
        uut = ConfigService(HttpCall(), 'https://foo.com')
        requests_mock.put(
            f'https://foo.com{ConfigService.deploy_type_url}',
            status_code=204)
        resp = uut.set_deployment_type_cloud()
        assert resp.status_code == 204

    def test_set_deployment_type_local(self, requests_mock):
        uut = ConfigService(HttpCall(), 'https://foo.com')
        requests_mock.put(
            f'https://foo.com{ConfigService.deploy_type_url}',
            status_code=204)
        resp = uut.set_deployment_type_local()
        assert resp.status_code == 204

    def test_set_deployment_type(self, requests_mock):
        uut = ConfigService(HttpCall(), 'https://foo.com')
        requests_mock.put(
            f'https://foo.com{ConfigService.deploy_type_url}',
            status_code=204)
        with pytest.raises(ValueError):
            uut._set_deployment_type('foo')
