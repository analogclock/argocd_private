import pytest
from requests import HTTPError
from fsiem_api_client.services.worker_service import WORKER_ACTION, WORKER_TYPE, WorkerService # noqa
from fsiem_api_client.http_call import HttpCall


class TestWorkerService:

    uut = WorkerService(HttpCall(), 'https://foo.com')

    def test_ctor(self):
        with pytest.raises(ValueError):
            WorkerService(None, 'foo')
        with pytest.raises(ValueError):
            WorkerService(HttpCall(), None)

    #
    # worker.get
    #
    def test_worker_get_httperror(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.GET, WORKER_TYPE.EVENT)
        requests_mock.get(url, status_code=500)
        with pytest.raises(HTTPError):
            self.uut.get(WORKER_TYPE.EVENT)

    def test_get_event_wrong_type(self, requests_mock):
        with pytest.raises(ValueError):
            self.uut.get('nope')

    def test_worker_get_event_no_events(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.GET, WORKER_TYPE.EVENT)
        requests_mock.get(
            url, text='No event worker exists')
        r = self.uut.get(WORKER_TYPE.EVENT)
        assert len(r) == 0

    def test_worker_get_query_no_events(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.GET, WORKER_TYPE.QUERY)
        requests_mock.get(
            url, text='No event worker exists')
        r = self.uut.get(WORKER_TYPE.QUERY)
        assert len(r) == 0

    def test_worker_get(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.GET, WORKER_TYPE.EVENT)
        requests_mock.get(url,
                          text='{\"addresses\": [ \"addr1\", \"addr2\"]}')
        r = self.uut.get(WORKER_TYPE.EVENT)
        assert len(r) == 2
        assert r[0] == 'addr1'
        assert r[1] == 'addr2'

    #
    # worker.add
    #
    def test_worker_add_httperror(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.ADD, WORKER_TYPE.EVENT)
        requests_mock.post(url, status_code=500)
        with pytest.raises(HTTPError):
            self.uut.add('wrk1', WORKER_TYPE.EVENT)

    def test_worker_add(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.ADD, WORKER_TYPE.EVENT)
        requests_mock.post(
            url,
            text='{"success":["Event worker added: wrk1"],"failed":[]}')
        self.uut.add('wrk1', WORKER_TYPE.EVENT)

    def test_worker_add_query(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.ADD, WORKER_TYPE.QUERY)
        requests_mock.post(
            url,
            text='{"success":["Event worker added: wrk1"],"failed":[]}')
        self.uut.add('wrk1', WORKER_TYPE.QUERY)

    def test_worker_add_no_success(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.ADD, WORKER_TYPE.EVENT)
        requests_mock.post(
            url,
            text='{"success":["Event worker added: bazinga"],"failed":[]}')
        with pytest.raises(ValueError):
            self.uut.add('wrk1', WORKER_TYPE.EVENT)

    def test_worker_add_fail(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.ADD, WORKER_TYPE.EVENT)
        requests_mock.post(url,
                           text='{"success":["wrk1"],"failed":["wrk1"]}')
        with pytest.raises(ValueError):
            self.uut.add('wrk1', WORKER_TYPE.EVENT)

    def test_add_event_wrong_type(self, requests_mock):
        with pytest.raises(ValueError):
            self.uut.add('wrk1', 'nope')

    #
    # worker.delete
    #
    def test_worker_delete_httperror(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.DEL, WORKER_TYPE.EVENT)
        requests_mock.post(url, status_code=500)
        with pytest.raises(HTTPError):
            self.uut.delete(['wrk1'], WORKER_TYPE.EVENT)

    def test_worker_delete(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.DEL, WORKER_TYPE.EVENT)
        requests_mock.post(
            url,
            text='{"success":["Event worker added: wrk1"],"failed":[]}')
        self.uut.delete(['wrk1'], WORKER_TYPE.EVENT)

    def test_worker_delete_query(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.DEL, WORKER_TYPE.QUERY)
        requests_mock.post(
            url,
            text='{"success":["Event worker added: wrk1"],"failed":[]}')
        self.uut.delete(['wrk1'], WORKER_TYPE.QUERY)

    def test_worker_delete_no_success(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.DEL, WORKER_TYPE.EVENT)
        requests_mock.post(
            url,
            text='{"success":["Event worker added: bazinga"],"failed":[]}')
        with pytest.raises(ValueError):
            self.uut.delete(['wrk1'], WORKER_TYPE.EVENT)

    def test_worker_delete_fail(self, requests_mock):
        url = self.uut._url_from(WORKER_ACTION.DEL, WORKER_TYPE.EVENT)
        requests_mock.post(
            url,
            text='{"success":["wrk1"],"failed":["wrk1"]}')
        with pytest.raises(ValueError):
            self.uut.delete(['wrk1'], WORKER_TYPE.EVENT)

    def test_worker_delete_wrong_type(self, requests_mock):
        with pytest.raises(ValueError):
            self.uut.delete(['wrk1'], 'nope')
