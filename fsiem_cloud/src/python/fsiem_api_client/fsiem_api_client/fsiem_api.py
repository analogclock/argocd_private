
from fsiem_api_client.fsiem_api_auth import FsiemApiAuth
from fsiem_api_client.services.config_service import ConfigService
from fsiem_api_client.services.h5_service import H5Service
from fsiem_api_client.services.worker_service import WorkerService
from fsiem_api_client.services.health_service import HealthService


class FsiemApi:
    """FortiSiem Api Client"""

    def __init__(self, auth: FsiemApiAuth) -> None:
        self.super_url = auth.super_url
        self.http = auth.http
        self.auth = auth
        self.config = ConfigService(self.http, self.super_url)
        self.h5 = H5Service(self.http, self.super_url)
        self.worker = WorkerService(self.http, self.super_url)
        self.health = HealthService(self.http, self.super_url)
