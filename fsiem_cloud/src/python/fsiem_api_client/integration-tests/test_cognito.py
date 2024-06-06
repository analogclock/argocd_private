from fsiem_api_client.aws.cognito import (get_cognito_creds, get_cognito_token)


secret_id = 'fsiem-vm-auth-creds-playground'
url = 'https://forticloud-fsiem-playground.auth.us-east-1.amazoncognito.com'


def test_get_cognito_creds():
    resp = get_cognito_creds(secret_id)
    assert resp['client_id']
    assert resp['client_secret']


def test_get_cognito_token():
    cred = get_cognito_creds(secret_id)
    resp = get_cognito_token(cred, url)
    assert resp
