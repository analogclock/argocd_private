import boto3
import requests
from base64 import b64encode
from json import loads


def get_cognito_creds(secret_id: str) -> dict:
    """Retrieve the AWS Cognito client id and secret that is stored in secrets
    manager

    Parameters
    ----------
    secret_id : str
        The ID of the secrets manager secret which contains the Cognito
        credentials

    Returns
    -------
    dict
        A dict container the client id and secret, in format:
        {
            'client_id': '...',
            'client_secret': '...'
        }
    """
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(
        SecretId=secret_id,
        VersionStage='AWSCURRENT'
    )
    return loads(response['SecretString'])


def get_cognito_token(client_creds: dict, cognito_url: str) -> str:
    """Gets an OAuth token from AWS Cognito


    Parameters
    ----------
    client_creds : dict
        The client id and secret retrieved from secrets manager
    cognito_url : str
        The URL for the aws Cognito endpoint

    Returns
    -------
    str
        The access token returned from Cognito

    Raises
    ------
    Exception
        The post request to get the status code didn't return HTTP code 200
    """
    cognito_oauth_url = f'{cognito_url}/oauth2/token'
    client_str = f'{client_creds["client_id"]}:{client_creds["client_secret"]}'
    encoded_client_str = b64encode(client_str.encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': 'Basic {}'.format(encoded_client_str),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body = 'grant_type=client_credentials'
    response = requests.post(cognito_oauth_url, data=body, headers=headers)
    if not response.status_code == 200:
        print(response.text)
        print(response.status_code)
        raise Exception('Unexpected status code from Cognito')
    data = response.json()
    print("Received access token from Cognito")
    return data['access_token']
