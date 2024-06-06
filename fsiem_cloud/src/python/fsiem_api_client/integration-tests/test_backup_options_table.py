from fsiem_api_client.backup_options_table import BackupOptionsTable


sn = "00001"
backup_options = """[{"S3_COMPRESSION_LEVEL": "1"}, {"S3_COMPRESSION_FORMAT": "tar"}, {"S3_USE_CUSTOM_STORAGE_CLASS": "false"}]""" # noqa


class TestBackupOptionsTable:

    uut = BackupOptionsTable('fsiem_backup_options_playground', 'us-east-1')

    def test_insert(self):
        self.uut.delete(sn)
        self.uut.insert(sn, backup_options)

    def test_insert_if_does_not_exist(self):
        self.uut.insert_if_does_not_exist(sn, backup_options)
        self.uut.delete(sn)
        self.uut.insert_if_does_not_exist(sn, backup_options)
        assert self.uut.exists(sn)

    def test_get_one(self):
        resp = list(self.uut.get(sn))
        assert len(resp) > 0
        resp = list(self.uut.get("does-not-exists"))
        assert len(resp) == 0

    def test_delete(self):
        resp = self.uut.delete(sn)
        assert resp

    def test_update(self):
        self.uut.delete(sn)
        self.uut.insert(sn, backup_options)

        self.uut.update(sn, "[]")
        resp = list(self.uut.get(sn))
        assert not resp
