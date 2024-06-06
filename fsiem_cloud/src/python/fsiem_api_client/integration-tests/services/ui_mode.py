from argparse import ArgumentParser
from fsiem_api_client.fsiem_api import FsiemApi
from fsiem_api_client.fsiem_api_auth import (FsiemApiAuth, FsiemApiBasicAuth,
                                             FsiemApiJWTAuth)
from fsiem_api_client.http_call import HttpCall


def get_auth(super_url: str, auth_mode: str, secret_id: str, cognito_url: str,
             user: str, password: str) -> FsiemApiAuth:
    """Return auth instance based on the auth mode: jwt/basic"""
    http = HttpCall(max_retry=1, verify_tls=True)
    if auth_mode == 'jwt':
        return FsiemApiJWTAuth(super_url, http, secret_id, cognito_url)
    elif auth_mode == 'basic':
        return FsiemApiBasicAuth(super_url, http, user, password)
    else:
        raise ValueError(f'Auth mode not supported: {auth_mode}')


def main(super_url: str, ui_mode: str, auth_mode: str, secret_id: str,
         cognito_url: str, user, password: str) -> None:
    """Switch UI logic between local or cloud"""

    print('\n==> Connecting...')
    print(f'Stack:   {super_url}')
    print(f'Auth:    {auth_mode}')
    print(f'Ui mode: {ui_mode}')
    auth = get_auth(super_url, auth_mode, secret_id,
                    cognito_url, user, password)
    if not auth.authenticate():
        raise ValueError('Authentication failed')
    fsiem = FsiemApi(auth)

    print(f'\n==> Updating UI mode to {ui_mode}')
    if ui_mode == 'local':
        fsiem.config.set_deployment_type_local()
    elif ui_mode == 'cloud':
        fsiem.config.set_deployment_type_cloud()
    else:
        raise ValueError(f'UI mode not supported: {ui_mode}')
    print('Done')


if __name__ == '__main__':
    """Entry point

    Example calls:

    #
    # Playground JWT (UI=local)
    #
    SUPER_URL=https://fsmcld0000000153.playground.fortisiem.cloud
    UI_MODE=local
    AUTH_MODE=jwt
    SECRET_ID=fsiem-vm-auth-creds-playground
    COGNITO_URL=https://forticloud-fsiem-playground.auth.us-east-1.amazoncognito.com

    python ui_mode.py \
        --super_url $SUPER_URL --ui_mode $UI_MODE --auth_mode $AUTH_MODE \
        --secret_id $SECRET_ID --cognito_url $COGNITO_URL

    #
    # Dev JWT (UI=local)
    #
    SUPER_URL=https://fsmcld0000000177.dev.fortisiem.cloud
    UI_MODE=local
    AUTH_MODE=jwt
    SECRET_ID=fsiem-vm-auth-creds-dev
    COGNITO_URL=https://forticloud-fsiem-dev.auth.us-east-1.amazoncognito.com

    python ui_mode.py \
        --super_url $SUPER_URL --ui_mode $UI_MODE --auth_mode $AUTH_MODE \
        --secret_id $SECRET_ID --cognito_url $COGNITO_URL

    #
    # Dev (UI=cloud)
    #
    SUPER_URL=https://fsmcld0000000177.dev.fortisiem.cloud
    UI_MODE=cloud
    AUTH_MODE=h5
    USER=super/admin
    PASSWORD=Fortinet*11

    python ui_mode.py \
        --super_url $SUPER_URL --ui_mode $UI_MODE --auth_mode $AUTH_MODE \
        --user $USER --password $PASSWORD
    """
    parser = ArgumentParser(description='Set UI mode to local or cloud')
    parser.add_argument('--super_url', type=str, required=True,
                        help='URL of the super node')
    parser.add_argument('--ui_mode', type=str, default='local',
                        choices=['local', 'cloud'],
                        help=('Type of UI mode on super, defaults to local)'))
    parser.add_argument('--auth_mode', type=str, required=True,
                        choices=['jwt', 'basic'],
                        help=('Authentication type, defaults to jwt'))
    parser.add_argument('--secret_id', type=str, required=False,
                        help='Cognito secret for jwt auth')
    parser.add_argument('--cognito_url', type=str, required=False,
                        help='Cognito URL for jwt auth')
    parser.add_argument('--user', type=str, required=False,
                        help='Username when using Basic or H5 auth')
    parser.add_argument('--password', type=str, required=False,
                        help='Password when using Basic or H5 auth')
    config = parser.parse_args()

    main(config.super_url, config.ui_mode, config.auth_mode, config.secret_id,
         config.cognito_url, config.user, config.password)
