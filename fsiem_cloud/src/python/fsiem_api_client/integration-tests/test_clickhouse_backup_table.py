from datetime import datetime
from fsiem_api_client.clickhouse_backup_table import (
    BackupStatus, ClickhouseBackupTable)
from fsiem_api_client.clickhouse_backup_table import BackupInfo


class TestClickHouseBackupTable:

    full = BackupInfo(serial_number='FSMCLD0000000154',
                      name='2023-03-31-full-0000',
                      start_date=datetime.utcnow().isoformat(),
                      stop_date=datetime.utcnow().isoformat(),
                      status=BackupStatus.backup_in_progress,
                      failed_reason='',
                      previous_backup_name='none',
                      type='full',
                      current_seq_number=1,
                      total_seq_number=1,
                      s3_location='fsiem-clickhouse-backups-us-east-1-playground/FSMCLD0000000154',  # noqa
                      backup_options='')
    inc1 = BackupInfo(serial_number='FSMCLD0000000154',
                      name='2023-03-31-inc-2222',
                      start_date=datetime.utcnow().isoformat(),
                      stop_date=datetime.utcnow().isoformat(),
                      status=BackupStatus.backup_in_progress,
                      failed_reason='',
                      previous_backup_name='2023-03-31-full-0000',
                      type='incremental',
                      current_seq_number=2,
                      total_seq_number=2,
                      s3_location='fsiem-clickhouse-backups-us-east-1-playground/FSMCLD0000000154',  # noqa
                      backup_options='')
    inc2 = BackupInfo(serial_number='FSMCLD0000000154',
                      name='2023-03-31-inc-1111',
                      start_date=datetime.utcnow().isoformat(),
                      stop_date=datetime.utcnow().isoformat(),
                      failed_reason='',
                      status=BackupStatus.backup_in_progress,
                      previous_backup_name='2023-03-31-inc-0001',
                      type='incremental',
                      current_seq_number=3,
                      total_seq_number=3,
                      s3_location='fsiem-clickhouse-backups-us-east-1-playground/FSMCLD0000000154',  # noqa
                      backup_options='')
    many_backups = [full, inc1, inc2]

    uut = ClickhouseBackupTable('fsiem_clickhouse_backup_dev', 'us-east-1')

    def test_insert(self):
        self.uut.delete(self.full)
        self.uut.insert(self.full)

    def test_insert_many(self):
        self.uut.delete_many(self.many_backups)
        self.uut.insert_many(self.many_backups)
        assert self.uut.exists(self.full)

    def test_insert_if_does_not_exist(self):
        self.uut.insert_if_does_not_exist(self.full)
        self.uut.delete(self.full)
        self.uut.insert_if_does_not_exist(self.full)
        assert self.uut.exists(self.full)

    def test_insert_many_if_does_not_exist(self):
        self.uut.insert_many_if_does_not_exist(self.many_backups)
        self.uut.delete_many(self.many_backups)
        self.uut.insert_many_if_does_not_exist(self.many_backups)
        assert self.uut.exists(self.full)

    def test_get_one(self):
        resp = self.uut.get_one('FSMCLD0000000154', '2023-03-31-full-0000')
        assert resp

    def test_delete(self):
        resp = self.uut.delete(self.full)
        assert resp

    def test_delete_many(self):
        if not self.uut.exists(self.full):
            self.uut.insert(self.full)
        if not self.uut.exists(self.inc1):
            self.uut.insert(self.inc1)
        if not self.uut.exists(self.inc2):
            self.uut.insert(self.inc2)
        self.uut.delete_many(self.many_backups)

    def test_update(self):
        self.uut.delete(self.full)
        self.uut.insert(self.full)
        self.full.previous_backup_name = 'new_backup'
        self.uut.update(self.full)
        resp = self.uut.get_one(self.full.serial_number, self.full.name)
        assert resp.previous_backup_name == 'new_backup'

    def test_get_backup_history(self):
        # insert backups out of order
        self.uut.delete_many(self.many_backups)
        self.uut.insert(self.full)
        self.uut.insert(self.inc2)
        self.uut.insert(self.inc1)

        resp = self.uut.get_backup_history('FSMCLD0000000154')

        # check history is ordered by total sequence number
        assert resp.all[0].name == self.full.name
        assert resp.all[1].name == self.inc1.name
        assert resp.all[2].name == self.inc2.name
