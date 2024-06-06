from fsiem_api_client.external_storage_table import ExternalStorageTable


sn = "FSMCLD0000000181"
organization_id = -1
last_update = '2024_02_11_18_15_16'
last_status = 'Successful'


class TestExternalStorageTable:

    uut = ExternalStorageTable('fsiem_external_storage_table_playground',
                               'us-east-1')

    def test_get_ext_storage_dests(self):
        resp = self.uut.get_external_storage_dests(sn)
        assert resp

    def test_update_external_storage_table(self):
        resp = self.uut.update_external_storage_table(sn, organization_id,
                                                      last_update, last_status)
        assert resp
