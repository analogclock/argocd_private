from providers import ClientProvider


class TestFsiemApiClientAuth:

    def test_basic_auth(self):
        for client in ClientProvider.fsiem_client_basic_auth():
            assert client.authenticate()

    def test_jwt_auth(self):
        for client in ClientProvider.fsiem_client_jwt_auth():
            assert client.authenticate()
