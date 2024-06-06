from providers import ClientProvider
from fsiem_api_client.services.worker_service import WORKER_TYPE, WorkerService  # noqa


class TestWorkerService:

    def test_worker_get(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = WorkerService(client.http, client.super_url)
            uut.get(WORKER_TYPE.EVENT)

    def test_worker_add(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = WorkerService(client.http, client.super_url)
            uut.add('test-worker', WORKER_TYPE.EVENT)

    def test_worker_delete(self):
        clients = ClientProvider.fsiem_client_jwt_auth(should_auth=True)
        for client in clients:
            uut = WorkerService(client.http, client.super_url)
            uut.delete(['test-worker'], WORKER_TYPE.EVENT)
