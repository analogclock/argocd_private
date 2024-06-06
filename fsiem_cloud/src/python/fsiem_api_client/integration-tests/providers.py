from fsiem_api_client.activation_table import ActivationTable
from config_value import ConfigReader
from fsiem_api_client.fsiem_api_auth import (FsiemApiBasicAuth,
                                             FsiemApiJWTAuth)
from fsiem_api_client.http_call import HttpCall


class ConfigProvider:

    def all():
        reader = ConfigReader()
        return reader.all()


# Cache clients for re-use in tests
h5_clients = []
basic_clients = []
jwk_clients = []


class ClientProvider:

    def fsiem_client_basic_auth(should_auth=True):
        # We have loaded clients already, return them
        if basic_clients:
            return basic_clients

        # First run, we need to create the clients and authenticate if needed
        for cfg in ConfigProvider.all():
            http = HttpCall(max_retry=1, verify_tls=cfg.vm_api.verify_tls)
            client = FsiemApiBasicAuth(
                super_url=cfg.vm_api.super_url,
                http=http,
                user=cfg.vm_api.basic_auth_user,
                password=cfg.vm_api.basic_auth_password)
            if should_auth:
                if not client.authenticate():
                    raise ValueError('basic auth failed')
            basic_clients.append(client)
        return basic_clients

    def fsiem_client_jwt_auth(should_auth=True):
        # We have loaded clients already, return them
        if jwk_clients:
            return jwk_clients

        for cfg in ConfigProvider.all():
            http = HttpCall(max_retry=1, verify_tls=cfg.vm_api.verify_tls)
            client = FsiemApiJWTAuth(
                secret_vm_auth=cfg.vm_api.secret_mgr_secret_id,
                super_url=cfg.vm_api.super_url,
                http=http,
                cognito_url=cfg.vm_api.cognito_url)
            if should_auth:
                if not client.authenticate():
                    raise ValueError('jwt auth failed')
            jwk_clients.append(client)
        return jwk_clients


class DynamoDbClientProvider:

    def tables():
        for cfg in ConfigProvider.all():
            # check we have non empty config for database
            if cfg.db.table_name:
                yield ActivationTable(table=cfg.db.table_name,
                                      region=cfg.db.region)
