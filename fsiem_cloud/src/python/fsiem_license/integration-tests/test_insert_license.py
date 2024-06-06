import json
from fsiem_api_client.activation_table import ActivationTable
from fsiem_api_client.aws.cognito import get_cognito_creds
from main import main


sn = 'FSMCLD0000000186'
supper_url = f'https://{sn}.playground.fortisiem.cloud'
portal_url = 'https://oo35plz18d.execute-api.us-east-1.amazonaws.com/playground-stage'  # noqa
secret_id_vm_auth = 'arn:aws:secretsmanager:us-east-1:023941436530:secret:fsiem-vm-auth-creds-playground-4Vw9N0'  # noqa
secret_id_license = 'arn:aws:secretsmanager:us-east-1:023941436530:secret:licensing-creds-playground-P0UO0Q'  # noqa
cognito_url = 'https://forticloud-fsiem-playground.auth.us-east-1.amazoncognito.com'  # noqa
dynamodb_table = 'fsiem_activation_table_playground'
dynamodb_region = 'us-east-1'


class TestFsiemApi:

    def test_license_stack(self):
        db = ActivationTable(dynamodb_table, dynamodb_region)
        db.update_status(sn, db.license_in_progress)

        cred = json.dumps(get_cognito_creds('fsiem-vm-auth-creds-playground'))
        main(supper_url, 'va', 'admin*1', 'Fortinet*11', cred,
             secret_id_license, cognito_url,
             portal_url, sn, dynamodb_table, dynamodb_region)
