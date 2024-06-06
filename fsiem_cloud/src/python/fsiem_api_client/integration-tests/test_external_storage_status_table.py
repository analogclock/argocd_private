from fsiem_api_client.external_storage_table import ExternalStorageStatusTable


sn = "FSMCLD0000000181"
organization_id = -1
start_datetime = '2024_02_11_18_10_16'
end_datetime = '2024_02_11_18_15_16'
bytes_copied = 0


class TestExternalStorageStatusTable:

    uut = ExternalStorageStatusTable(
                        'fsiem_external_storage_status_table_playground',
                        'us-east-1')

    def test_update_ext_st_status_table(self):

        resp = self.uut.update_external_storage_table(
                         sn, organization_id, start_datetime, end_datetime,
                         bytes_copied)
        assert resp
