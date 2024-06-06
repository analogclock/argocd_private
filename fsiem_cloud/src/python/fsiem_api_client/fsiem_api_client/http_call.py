import logging
from typing import Any
import requests
from requests import Response
from http import HTTPStatus
from tenacity import (Retrying, after_log, retry_if_not_exception_type,
                      wait_exponential, stop_after_attempt)
import urllib3
from fsiem_api_client.exceptions import UnauthorizedHttpError


class HttpCall:

    def __init__(self,  max_retry: int = 10, verify_tls=True) -> None:
        self.max_retry = max_retry
        self.verify_tls = verify_tls

        # Used by tenacity retry
        self.logger = logging.getLogger(__name__)

        if not verify_tls:
            print('WARNING: verify_ssl is set to False. This means that TLS '
                  'certificate validation is disabled and connections to '
                  'sites with invalid TLS certificates will be allowed')
            # This prevents warning message spam, the above warning is enough
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Configure default retry:
        # - Stop after N calls (self.max_retry)
        # - Wait exponentially, good for calling networking services
        # - Wait minimum 10 seconds and max 300 seconds
        # - Log errors into the logger
        # - Raise actual exception, not the RetryException + inner exception
        self.default_retry = Retrying(
            stop=stop_after_attempt(self.max_retry),
            wait=wait_exponential(multiplier=1, min=10, max=300),
            after=after_log(self.logger, logging.DEBUG),
            retry=retry_if_not_exception_type(UnauthorizedHttpError),
            reraise=True)

        # Set after a call to _login
        self.cookies = None
        self.auth = None
        self.h5_auth_token = None

    def _call(self, verb: str, url: str, headers: dict = None,
              json: dict = None, data=None, params=None, files=None,
              ok_text=None, use_cookies=True, verbose=True) -> Response:
        msg = f'{url} {json}' if verbose else f'{url}'
        print(f'Req: http {verb} {msg}', flush=True)
        if not self.auth and self.h5_auth_token:
            if not params:
                params = {}
            params['s'] = self.h5_auth_token
        cookies = self.cookies if use_cookies else None
        r = requests.request(method=verb, url=url, json=json, data=data,
                             params=params, cookies=cookies, headers=headers,
                             files=files, verify=self.verify_tls,
                             auth=self.auth)

        # Check if token is expired, either status code 401 or
        # response contains HTML with login page (this happens too!)
        if r.status_code == 401 or 'button id="loginBtn"' in r.text:
            raise UnauthorizedHttpError('Client auth token is not valid')
        r.raise_for_status()

        # ok_text is a string
        if ok_text and isinstance(ok_text, str) and ok_text not in r.text:
            raise ValueError(f'Unexpected response: {r.text}')

        # ok_text is a list
        if ok_text and isinstance(ok_text, list) and \
           not any(item in r.text for item in ok_text):
            raise ValueError(f'Unexpected response: {r.text}')

        status = HTTPStatus(r.status_code)
        msg = f'{status.value} {status.phrase} {r.text}' if verbose \
            else f'{status.value} {status.phrase}'
        print(f'Res: {msg}', flush=True)
        return r

    def _retry(self, verb: str, url: str, headers: dict = None,
               json: dict = None, data=None, params=None, files=None,
               ok_text=None, use_cookies=True, verbose=True,
               retry=None) -> Response:
        """Call HTTP POST with retry.

        Retry will execute if exception is thrown. Current logic is:
        - Stop after self.max_retry, passed into ctor. In tests we use 1, in
          prod code we use 10
        - Wait with exponential delay from 10 seconds to 60 seconds max
        - Log error after each failed retry
        - Do NOT retry if exception is UnauthorizedHttpError. This happens when
          we try to login with a password that's incorrect. Retrying this will
          lock an account very quickly.
        - If all retries fail, finally raise the original exception and don't
          wrap that exception into the RetryException

        """
        if not retry:
            retry = self.default_retry

        # Print re-try statistics, on a first try/call it is an empty dict
        if retry.statistics and retry.statistics['attempt_number'] != 1:
            print(f'Retry stats: {retry.statistics}', flush=True)

        # First argument is a function name that we want to retry if an
        # exception happens, without round brackets. All subsequent
        # arguments are the arguments for that function.
        return retry(self._call, verb, url, headers, json, data, params,
                     files, ok_text, use_cookies, verbose)

    def set_auth(self, auth: Any):
        self.auth = auth

    def set_cookies(self, cookies: dict):
        self.cookies = cookies

    def set_h5_auth_token(self, h5_auth_token: str):
        self.h5_auth_token = h5_auth_token

    def set_verify_tls(self, verify_tls: bool):
        self.verify_tls = verify_tls

    def get(self, url: str, headers: dict = None, json: dict = None,
            data=None, params=None, files=None, ok_text=None,
            use_cookies=True, verbose=True) -> Response:
        return self._call('get', url, headers, json, data, params, files,
                          ok_text, use_cookies, verbose)

    def post(self, url: str, headers: dict = None, json: dict = None,
             data=None, params=None, files=None, ok_text=None,
             use_cookies=True, verbose=True) -> Response:
        return self._call('post', url, headers, json, data, params, files,
                          ok_text, use_cookies, verbose)

    def put(self, url: str, headers: dict = None, json: dict = None,
            data=None, params=None, ok_text=None, files=None, use_cookies=True,
            verbose=True) -> Response:
        return self._call('put', url, headers, json, data, params, files,
                          ok_text, use_cookies, verbose)

    def retry_get(self, url: str, headers: dict = None, json: dict = None,
                  data=None, params=None,  files=None, ok_text=None,
                  use_cookies=True, verbose=True, retry=None) -> Response:
        return self._retry('get', url, headers, json, data, params, files,
                           ok_text, use_cookies, verbose, retry=retry)

    def retry_post(self, url: str, headers: dict = None, json: dict = None,
                   data=None, params=None,  files=None, ok_text=None,
                   use_cookies=True, verbose=True, retry=None) -> Response:
        return self._retry('post', url, headers, json, data, params, files,
                           ok_text, use_cookies, verbose, retry)

    def retry_put(self, url: str, headers: dict = None, json: dict = None,
                  data=None, params=None, ok_text=None,  files=None,
                  use_cookies=True, verbose=True, retry=None) -> Response:
        return self._retry('put', url, headers, json, data, params, files,
                           ok_text, use_cookies, verbose, retry)

    def verify_resp_for_item(self, json, item: str):
        if item not in str(json['success']) or item in str(json['failed']):
            raise ValueError(f'Operation failed for {item}. Response: {json}')

    def verify_resp_for_list(self, json, items: list):
        for item in items:
            self.verify_resp_for_item(json, item)
