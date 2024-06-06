import pytest
import requests
from tenacity import Retrying, stop_after_attempt, retry_if_not_exception_type
from fsiem_api_client.exceptions import UnauthorizedHttpError
from fsiem_api_client.http_call import HttpCall


class TestHttpCall:

    super_addr = '10.0.0.1'
    user = 'admin'
    password = 'admin*1'
    resp_ok = 'ok'
    cookies = {'JSESSIONID': 'burn_things', 's': 'nuke_the_whales'}
    salt_response = '{"salt":"bDwFVbPNPG"}'
    # Re-use the same retry in tests
    maxretry = 10
    retry = Retrying(
        stop=stop_after_attempt(maxretry),
        retry=retry_if_not_exception_type(UnauthorizedHttpError),
        reraise=True)

    def test_ctor(self):
        uut = HttpCall(3, False)
        assert uut.max_retry == 3

    def test_http_get(self, requests_mock):
        requests_mock.get('https://foo.com/bar', text=self.resp_ok)
        uut = HttpCall()
        actual = uut.get('https://foo.com/bar')
        assert actual.text == self.resp_ok

    def test_http_post(self, requests_mock):
        requests_mock.post('https://foo.com/bar', text=self.resp_ok)
        uut = HttpCall()
        actual = uut.post('https://foo.com/bar')
        assert actual.text == self.resp_ok

    def test_http_put(self, requests_mock):
        requests_mock.put('https://foo.com/bar', text=self.resp_ok)
        uut = HttpCall()
        actual = uut.put('https://foo.com/bar')
        assert actual.text == self.resp_ok

    def test_failed_request(self, requests_mock):
        requests_mock.put('https://foo.com/bar', status_code=400)
        uut = HttpCall()
        with pytest.raises(requests.HTTPError):
            uut.put('https://foo.com/bar')

    def test_retry_get_2xx_no_retry(self, requests_mock):
        uut = HttpCall()
        requests_mock.get('https://foo.com/bar', status_code=200)
        uut.retry_get('https://foo.com/bar', retry=self.retry)
        assert self.retry.statistics['attempt_number'] == 1

        requests_mock.get('https://foo.com/bar', status_code=201)
        uut.retry_get('https://foo.com/bar', retry=self.retry)
        assert self.retry.statistics['attempt_number'] == 1

    def test_retry_get_401_ignore_auth_failures(self, requests_mock):
        uut = HttpCall()
        requests_mock.get('https://foo.com/bar', status_code=401)
        with pytest.raises(UnauthorizedHttpError):
            uut.retry_get('https://foo.com/bar', retry=self.retry)

    def test_retry_get_500_max_retry_count(self, requests_mock):
        uut = HttpCall()
        requests_mock.get('https://foo.com/bar', status_code=500)
        with pytest.raises(requests.exceptions.HTTPError):
            uut.retry_get('https://foo.com/bar', retry=self.retry)
        assert self.retry.statistics['attempt_number'] == uut.max_retry

    def test_retry_post_2xx_noretry(self, requests_mock):
        uut = HttpCall()
        requests_mock.post('https://foo.com/bar', status_code=200)
        uut.retry_post('https://foo.com/bar', data={}, retry=self.retry)
        assert self.retry.statistics['attempt_number'] == 1

        requests_mock.post('https://foo.com/bar', status_code=201)
        uut.retry_post('https://foo.com/bar', data={}, retry=self.retry)
        assert self.retry.statistics['attempt_number'] == 1

    def test_retry_post_401_ignore_auth_failures(self, requests_mock):
        uut = HttpCall()
        requests_mock.post('https://foo.com/bar', status_code=401)
        with pytest.raises(UnauthorizedHttpError):
            uut.retry_post('https://foo.com/bar', data={}, retry=self.retry)

    def test_retry_post_500_maxretry_count(self, requests_mock):
        uut = HttpCall()
        requests_mock.post('https://foo.com/bar', status_code=500)
        with pytest.raises(requests.exceptions.HTTPError):
            uut.retry_post('https://foo.com/bar', data={}, retry=self.retry)
        assert self.retry.statistics['attempt_number'] == uut.max_retry
