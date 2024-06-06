from main import lambda_handler


sn = 'FSMCLD0000000152'
env = 'playground'
super_url = f'https://{sn}.{env}.fortisiem.cloud'
password = 'Fortinet*11'


class TestItMain:

    def test_lambda_handler_add_org_collectors_to_super(self):
        event = {

            'User': 'super/admin',
            'Password': password,
            'OrgUser': 'org400User',
            'SuperUrl': super_url,
            'OrgName': 'org202',
            'CollectorEps': '300',
            'CollectorName': 'collector122',
            'SerialNumber': sn,
            'Command': 'add_org_collectors_to_super'
        }
        lambda_handler(event, None)
