import requests

from argparse import ArgumentParser
from base64 import b64decode
from datetime import datetime
from json import loads
from json.decoder import JSONDecodeError
from packaging import version
from requests.exceptions import HTTPError
from fsiem_api_client import ActivationTable
from fsiem_api_client.aws.cognito import get_cognito_creds, get_cognito_token
from fsiem_api_client.util import get_client


def get_license(access_token: str, portal_api_url: str, serial_number: str,
                uuid: str) -> dict:
    """Retrieve the license from Portal API Gateway

    Parameters
    ----------
    access_token : str
        The access token returned from cognito
    portal_api_url : str
        The URL of the portal API gateway
    serial_number : str
        The serial number of this deployment
    uuid : str
        The UUID of the super

    Returns
    -------
    dict
        The license returned from API gateway, in format:
        {
            serialNumber: <sn>,
            licenseKey: <base64_string>
        }
    """
    url = f'{portal_api_url}/api/licence'
    params = {
        'serialNumber': serial_number,
        'uuid': uuid
    }
    headers = {
        'Content-type': 'application/json',
        'Accept': 'text/plain',
        'Authorization': 'Bearer {}'.format(access_token)
    }
    try:
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()
        return r.json()
    except (HTTPError, JSONDecodeError) as e:
        if isinstance(e, HTTPError):
            print('Get license request did not return a 200 code')
            print(f'Status Code: {r.status_code}')
        elif isinstance(e, JSONDecodeError):
            print('Get license request did not return expected response')
            print(f'Response: {r.text}')
        print(e)
        raise


def main(super_url: str, license_type: str, default_password: str,
         new_password: str, secret_vm_auth: str, secret_id: str,
         cognito_url: str, portal_api_url: str, serial_number: str,
         dynamodb_table: str, dynamodb_region: str):
    """Queries the super for its UUID, using that to retrieve a license file
    from the license server, then inserts that license into the super

    Parameters
    ----------
    super_url: str
        The address of the super node, full address i.e https://1.1.1.1
    license_type: str
        The license type. Either va for enterprise or sp for service provider
    default_password: str
        The default password for the default admin account
    new_password: str
        The new password for the default admin account
    secret_vm_auth: str
        Credentials from secrets manager to authenticate with cognito for JWT
        auth
    secret_id: str
        The ID of the secrets manager secret used for licensing
    cognito_url: str
        The URL of cognito
    portal_api_url: str
        The URL of the portal api gateway
    serial_number: str
        The serial number of this deployment
    dynamodb_table: str
        The name of the dynamodb table that stores the status of deployments
    dynamodb_region: str
        The aws region the dynamodb table is located
    """
    secret_vm_auth_dict = loads(secret_vm_auth)
    db = ActivationTable(dynamodb_table, dynamodb_region)
    current_status = db.get_status(serial_number)

    statuses_to_run = [
        db.license_in_progress,
        db.update_completed
    ]

    if current_status not in statuses_to_run:
        print(f'Do not run when status is `{current_status}`. Exiting.')
        return

    print(f'==> Testing connection to FSIEM VM API: `{super_url}`')
    fsiem = get_client(super_url, secret_vm_auth_dict, cognito_url,
                       max_retry=1, verify_tls=False)

    if not fsiem:
        print('Connection cannot be established. Exiting...')
        return

    first_time_setup = False

    # Check if we have a UUID in DynamoDb, if we don't have it
    # we assume it's a first time setup
    uuid = db.get_uuid(serial_number)
    if not uuid:
        first_time_setup = True
        print('Getting UUID from server')
        uuid = fsiem.h5.get_uuid()

    print('Getting cognito ID and secret')
    creds = get_cognito_creds(secret_id)

    print('Getting Auth token')
    access_token = get_cognito_token(creds, cognito_url)

    print('Getting license object from portal api')
    license_dict = get_license(access_token, portal_api_url, serial_number,
                               uuid)

    force_upload = license_dict.get('haveDetailsChanged', False)
    license_new_sku = license_dict.get('entitlement', None)
    license_data = b64decode(license_dict['licenseKey'])
    license_name = f'{uuid}.lic'

    # Note: this API call requires user name and pwd, and we don't want
    # to do this as user can change their password, but we have to. See
    # https://mantis.fortinet.com/bug_view_page.php?bug_id=0888924
    if first_time_setup:
        # For the first time, we must submit user password, as this is how
        # We set up user web login
        print('Uploading license file to Super')
        fsiem.h5.upload_license(license_type, license_data, license_name,
                                default_password)
        print('Updating DynamoDB with UUID')
        db.set_uuid(serial_number, uuid)
    else:

        # Check if API returns a flag, indicating if any of the entitlements
        # have changed. Most of the times, there will be no change. We set the
        # status to setup_initializing and return
        if license_new_sku is None and not force_upload:
            print('Entitlements in the license have not changed')
            print('No need to upload the licence')
            print(f'Updating status in database to {db.setup_initializing}')
            db.update_status(serial_number, db.setup_initializing)
            return

        print('Entitlements have changed, reinserting a new license')
        version_from_dynamo = db.get_version(serial_number)
        if not version_from_dynamo:
            raise ValueError(
                f'''Cannot run licensing process because the version of
                {serial_number} is not set in activation table and it is
                required to determine which authentication to use for API call
                ''')
        ver = version.parse(version_from_dynamo)
        print('Version of the VM: {ver}')
        version_7_1_4 = version.parse("7.1.4")

        if ver >= version_7_1_4:
            print('Using JWT auth for license call')
            print("""Use JWT authentication, this is only available from Fsiem
                  version 7.1.4. From this version we don't need to submit
                  user password any more. The server checks JWT auth token""")
            fsiem.h5.upload_license_jwt(license_type, license_data,
                                        license_name)
        else:
            print('Using user password for license call')
            print('VM version is older than 7.1.4')
            # This code should be removed once all VMs are updated to
            # version 7.1.4 or later. We don't want to submit user pwd as
            # it may change.
            fsiem.h5.upload_license(license_type, license_data, license_name,
                                    new_password)
    print('License successfully inserted')

    if license_new_sku:
        print('Updating new SKU information')
        db.update_sku(serial_number, license_new_sku)

    print(f'Updating status in database to {db.setup_initializing}')
    db.update_status(serial_number, db.setup_initializing)
    now = str(datetime.utcnow())
    print(f'Updating licence inserted date to  {now}')
    db.set_license_inserted_on(serial_number, now)


def parse_args() -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Retrieves a license and inserts it into the fsiem super')
    parser = ArgumentParser(description=description)
    parser.add_argument('--super', type=str, required=True,
                        help='The address of the Super node')
    parser.add_argument('--license_type', type=str, default='va',
                        choices=['va', 'sp'],
                        help=('The license type: va for enterprise or sp for '
                              'service provider (default: va)'))
    parser.add_argument('--default_password', type=str, required=True,
                        help=('The default password for the default admin'
                              'account'))
    parser.add_argument('--new_password', type=str, required=True,
                        help='The new password for admin account')
    parser.add_argument('--secret_vm_auth', type=str, required=True,
                        help=('Credentials from secrets manager to '
                              'authenticate with cognito for JWT auth'))
    parser.add_argument('--secret_id', type=str, required=True,
                        help='The ID of the secrets manager secret (license)')
    parser.add_argument('--cognito_url', type=str, required=True,
                        help='The URL of cognito')
    parser.add_argument('--portal_api_url', type=str, required=True,
                        help='The URL of the portal api gateway')
    parser.add_argument('--serial_number', type=str, required=True,
                        help='The serial number of this deployment')
    parser.add_argument('--dynamodb_table', type=str, required=True,
                        help='The name of the dynamodb table')
    parser.add_argument('--dynamodb_region', type=str, required=True,
                        help='The region of the dynamodb table')
    return parser.parse_args()


if __name__ == '__main__':
    # Usage: python3 main.py --super 54.1.1.1 --license_type va
    # --default_password admin*1 --new_password user-provided-password
    # --secret_vm_auth arn:aws:s:a:1234:secret:fsiem_vm_auth_playground
    # --secret_id arn:aws:s:a:1234:secret:licensing-creds-playground
    # --cognito_url https://qwe --portal_api_url https://rty --serial_number 12
    # --dynamodb_table table --dynamodb_region region

    config = parse_args()
    super_url = f'https://{config.super}'
    main(super_url, config.license_type, config.default_password,
         config.new_password, config.secret_vm_auth, config.secret_id,
         config.cognito_url, config.portal_api_url, config.serial_number,
         config.dynamodb_table, config.dynamodb_region)
    print('All work is done')
