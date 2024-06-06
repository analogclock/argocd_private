import configparser
import os
from os.path import exists
from dataclasses import dataclass


@dataclass
class FsiemClientCfg:
    super_url: str
    verify_tls: bool
    basic_auth_user: str
    basic_auth_password: str
    secret_mgr_secret_id: str
    cognito_url: str


@dataclass
class DynamoDbCfg:
    table_name: str
    region: str


@dataclass
class ConfigValue:
    vm_api: FsiemClientCfg
    db: DynamoDbCfg


class ConfigReader:

    # Based on https://stackoverflow.com/a/715468/706456
    def str2bool(self, v):
        """Convert string to bool.

        Why did you write this? Well, because:

        >>> bool('False')
        >>> True

        Eh? See https://stackoverflow.com/q/715417/706456, esp check comments.
        """
        return str(v).lower() in ("yes", "true", "t", "1")

    def load(self, path: str) -> ConfigValue:
        if not exists(path):
            raise FileNotFoundError(f'\'{path}\' does not exist')
        config = configparser.ConfigParser()
        config.read(path)
        vm_api = FsiemClientCfg(
            super_url=config['FSIEM']['super_url'],
            basic_auth_user=config['FSIEM']['basic_auth_user'],
            basic_auth_password=config['FSIEM']['basic_auth_password'],
            secret_mgr_secret_id=config['FSIEM']['secret_mgr_secret_id'],
            cognito_url=config['FSIEM']['cognito_url'],
            verify_tls=self.str2bool(config['FSIEM']['verify_tls']))
        db = DynamoDbCfg(
            table_name=config['DynamoDB']['table_name'],
            region=config['DynamoDB']['region']
        )
        return ConfigValue(vm_api, db)

    def all(self, config_dir='integration-tests/config'):
        for file in os.listdir(config_dir):
            yield self.load(os.path.join(config_dir, file))
