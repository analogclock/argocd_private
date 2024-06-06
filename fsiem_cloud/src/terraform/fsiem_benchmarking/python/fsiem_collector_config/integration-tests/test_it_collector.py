from collector import add_org_collectors_to_super, provision_collectors


sn = 'FSMCLD0000000152'
env = 'playground'
super_url = f'https://{sn}.{env}.fortisiem.cloud'
password = 'Fortinet*11'
org_name = 'org303'
event = {
            'User': 'admin',
            'EnvId': env,
            'Password': password,
            'OrgUser': 'org400User',
            'SuperUrl': super_url,
            'OrgName': org_name,
            'CollectorEps': '300',
            'CollectorName': 'test_collector, test_collector_1',
            'SerialNumber': sn,
        }


class TestItCollector:

    def test_add_org_collectors_to_super(self):
        # Note, if you get HTTP 500, change the OrgName value
        actual = add_org_collectors_to_super(event)
        assert actual.status_code == 204

    def test_provision_collectors(self):
        # This test needs to have an org already added

        # TODO: remove this later. This was used during manual testing,
        # collector was deployed with diff serial number
        event['SerialNumber'] = 'coll152'

        provision_collectors(event)
