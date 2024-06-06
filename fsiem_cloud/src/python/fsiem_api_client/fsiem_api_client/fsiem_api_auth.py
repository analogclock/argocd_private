from base64 import b64encode
from requests import HTTPError
from requests.auth import AuthBase
from fsiem_api_client.aws.cognito import get_cognito_token
from fsiem_api_client.http_call import HttpCall


class TokenAuth(AuthBase):
    def __init__(self, token, auth_scheme='Bearer'):
        self.token = token
        self.auth_scheme = auth_scheme

    def __call__(self, request):
        request.headers['Authorization'] = f'{self.auth_scheme} {self.token}'
        return request


class FsiemApiAuth:

    def __init__(self, super_url: str, http: HttpCall) -> None:
        if not super_url:
            raise ValueError('Super url is not provided')
        self.super_url = super_url
        self.http = http
        self.h5_auth_token = None
        self.auth = None

    def authenticate(self) -> bool:
        pass


# NOTE: Use JWT authentication instead
class FsiemApiBasicAuth(FsiemApiAuth):
    def __init__(self, super_url: str, http: HttpCall,
                 user='super/admin', password='') -> None:
        if not user:
            raise ValueError('User is not provided')
        if not password:
            raise ValueError('Password is not provided')
        self.user = user
        self.password = password
        super().__init__(super_url, http)

    def authenticate(self) -> bool:
        try:
            user_pwd = f"{self.user}:{self.password}".encode('utf-8')
            token = b64encode(user_pwd).decode("ascii")
            self.http.set_auth(TokenAuth(token, 'Basic'))
            print('Testing Basic auth')
            url = f'{self.super_url}/phoenix'
            resp = self.http.get(url, verbose=False)
            result = resp.ok and 'button id="loginBtn"' not in resp.text
            print(f'Basic auth status: {result}')
            return result
        except Exception as e:
            print(f'Basic auth failed: {e}')
            return False


class FsiemApiJWTAuth(FsiemApiAuth):
    def __init__(self, super_url: str, http: HttpCall,
                 secret_vm_auth='', cognito_url='') -> None:
        if not secret_vm_auth:
            raise ValueError('VM auth secret is not provided')
        if not cognito_url:
            raise ValueError('Aws Cognito url is not provided')
        self.secret_vm_auth = secret_vm_auth
        self.cognito_url = cognito_url
        super().__init__(super_url, http)

    def authenticate(self) -> bool:
        try:
            token = get_cognito_token(self.secret_vm_auth, self.cognito_url)
            self.http.set_auth(TokenAuth(token, 'Bearer'))
            print('Testing JWT auth')
            url = f'{self.super_url}/phoenix/'
            resp = self.http.get(url, verbose=False)
            result = resp.ok and 'button id="loginBtn"' not in resp.text
            print(f'JWT auth status: {result}')
            return result
        except HTTPError as e:
            print(f'JWT auth HTTP error: {e}')
            if e.args and e.args[0] and 'register.xhtml' in e.args[0]:
                print(f'[WARN] The product is not registered: {e.args[0]}')
                print('[WARN] API access is granted to limited functionality')
                return True
            print('[ERROR] No access is granted to any API')
            return False
        except Exception as e:
            print(f'JWT auth failed: {e}')
            return False
