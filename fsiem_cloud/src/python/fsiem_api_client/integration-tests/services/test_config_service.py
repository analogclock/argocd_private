from providers import ClientProvider
from fsiem_api_client.services.config_service import ConfigService


class TestConfigService:

    def test_set_deployment_type_local(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = ConfigService(client.http, client.super_url)
            resp = uut.set_deployment_type_local()
            assert resp.status_code == 204

    def test_set_deployment_type_cloud(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = ConfigService(client.http, client.super_url)
            resp = uut.set_deployment_type_cloud()
            assert resp.status_code == 204
