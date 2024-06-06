from datetime import datetime
from fsiem_api_client.clickhouse_restore_table import (
    RestoreStatus, ClickhouseRestoreTable)
from fsiem_api_client.clickhouse_restore_table import RestoreInfo


class TestClickHouseRestoreTable:

    r1 = RestoreInfo(serial_number='FSMCLD0000000154',
                     name='2023-03-31-restore-1',
                     start_date=datetime.utcnow().isoformat(),
                     stop_date=datetime.utcnow().isoformat(),
                     status=RestoreStatus.restore_in_progress,
                     failed_reason='',
                     restored_from='backup1',
                     total_seq_number=1,
                     s3_location='fsiem-clickhouse-backups-us-east-1-playground/FSMCLD0000000154')  # noqa
    r2 = RestoreInfo(serial_number='FSMCLD0000000154',
                     name='2023-03-31-restore-2',
                     start_date=datetime.utcnow().isoformat(),
                     stop_date=datetime.utcnow().isoformat(),
                     status=RestoreStatus.restore_in_progress,
                     failed_reason='',
                     restored_from='backup2',
                     total_seq_number=2,
                     s3_location='fsiem-clickhouse-backups-us-east-1-playground/FSMCLD0000000154')  # noqa
    r3 = RestoreInfo(serial_number='FSMCLD0000000154',
                     name='2023-03-31-restore-3',
                     start_date=datetime.utcnow().isoformat(),
                     stop_date=datetime.utcnow().isoformat(),
                     status=RestoreStatus.restore_in_progress,
                     failed_reason='',
                     restored_from='backup3',
                     total_seq_number=3,
                     s3_location='fsiem-clickhouse-backups-us-east-1-playground/FSMCLD0000000154')  # noqa

    many_restores = [r1, r2, r3]

    uut = ClickhouseRestoreTable(
        'fsiem_clickhouse_restore_playground', 'us-east-1')

    def test_insert(self):
        self.uut.delete(self.r1)
        self.uut.insert(self.r1)

    def test_insert_many(self):
        self.uut.delete_many(self.many_restores)
        self.uut.insert_many(self.many_restores)
        assert self.uut.exists(self.r1)

    def test_insert_if_does_not_exist(self):
        self.uut.insert_if_does_not_exist(self.r1)
        self.uut.delete(self.r1)
        self.uut.insert_if_does_not_exist(self.r1)
        assert self.uut.exists(self.r1)

    def test_insert_many_if_does_not_exist(self):
        self.uut.insert_many_if_does_not_exist(self.many_restores)
        self.uut.delete_many(self.many_restores)
        self.uut.insert_many_if_does_not_exist(self.many_restores)
        assert self.uut.exists(self.r1)

    def test_get_one(self):
        self.uut.insert_if_does_not_exist(self.r1)
        resp = self.uut.get_one('FSMCLD0000000154', self.r1.name)
        assert resp

    def test_delete(self):
        resp = self.uut.delete(self.r1)
        assert resp

    def test_delete_many(self):
        if not self.uut.exists(self.r1):
            self.uut.insert(self.r1)
        if not self.uut.exists(self.r2):
            self.uut.insert(self.r2)
        if not self.uut.exists(self.r3):
            self.uut.insert(self.r3)
        self.uut.delete_many(self.many_restores)

    def test_update(self):
        self.uut.delete(self.r1)
        self.uut.insert(self.r1)
        self.r1.restored_from = 'new_backup'
        self.uut.update(self.r1)
        resp = self.uut.get_one(self.r1.serial_number, self.r1.name)
        assert resp.restored_from == 'new_backup'

    def test_get_backup_history(self):
        # insert backups out of order
        self.uut.delete_many(self.many_restores)
        self.uut.insert(self.r1)
        self.uut.insert(self.r3)
        self.uut.insert(self.r2)

        resp = self.uut.get_restore_history('FSMCLD0000000154')

        # check history is ordered by total sequence number
        assert resp.all[0].name == self.r1.name
        assert resp.all[1].name == self.r2.name
        assert resp.all[2].name == self.r3.name
