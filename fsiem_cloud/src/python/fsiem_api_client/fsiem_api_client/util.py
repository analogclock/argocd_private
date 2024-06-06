from fsiem_api_client.http_call import HttpCall
from fsiem_api_client.fsiem_api import FsiemApi
from fsiem_api_client.fsiem_api_auth import FsiemApiJWTAuth


def get_client(super_addr: str, secret_vm_auth: str, cognito_url: str,
               max_retry: int = 10, verify_tls=True) -> FsiemApi:
    """Create a client using JWT authentication, if authentication fails
    this method returns None.

    Parameters
    ----------
    super_addr : str
        address of super
    secret_vm_auth: str
        The value of the secrets manager secret with the cognito credentials
    cognito_url: str
        The URL of cognito
    max_retry: int
        Number of connection attempts. Defaults to 10
    verify_tls: bool
        Verify TLS cert or not. Defaults to True
    """
    if secret_vm_auth and cognito_url:
        http = HttpCall(max_retry, verify_tls)
        fsiem = FsiemApiJWTAuth(super_addr, http, secret_vm_auth, cognito_url)
        if fsiem.authenticate():
            return FsiemApi(fsiem)
    return None
