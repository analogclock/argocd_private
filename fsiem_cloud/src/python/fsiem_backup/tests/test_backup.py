from fsiem_api_client.clickhouse_backup_table import (
    BackupInfo, BackupInfoHistory)
from backup import get_deletable_backups


def one(type, current_number, total_number):
    return BackupInfo(serial_number='', name=total_number, start_date='',
                      stop_date='', status='', failed_reason='',
                      previous_backup_name='',
                      type=type, current_seq_number=current_number,
                      total_seq_number=total_number, s3_location='',
                      backup_options='')


def test_get_deletable_backups_3():
    history = BackupInfoHistory(
        [one('full', 1, 1), one('incremental', 2, 2), one('incremental', 3, 3)]
    )
    assert not get_deletable_backups(history, 3)


def test_get_deletable_backups_4():
    history = BackupInfoHistory(
        [one('full', 1, 1), one('incremental', 2, 2), one('incremental', 3, 3),
         one('full', 1, 4)]
    )
    assert not get_deletable_backups(history, 3)


def test_get_deletable_backups_5():
    history = BackupInfoHistory(
        [one('full', 1, 1), one('incremental', 2, 2), one('incremental', 3, 3),
         one('full', 1, 4), one('incremental', 2, 5)]
    )
    assert not get_deletable_backups(history, 3)


def test_get_deletable_backups_6():
    history = BackupInfoHistory(
        [one('full', 1, 1), one('incremental', 2, 2), one('incremental', 3, 3),
         one('full', 1, 4), one('incremental', 2, 5), one('incremental', 3, 6)]
    )
    actual = get_deletable_backups(history, 3)
    assert actual[0].total_seq_number == 3
    assert actual[1].total_seq_number == 2
    assert actual[2].total_seq_number == 1


def test_get_deletable_backups_7():
    history = BackupInfoHistory(
        [one('full', 1, 1), one('incremental', 2, 2), one('incremental', 3, 3),
         one('full', 1, 4), one('incremental', 2, 5), one('incremental', 3, 6),
         one('full', 1, 7)]
    )
    actual = get_deletable_backups(history, 3)
    assert 3 == len(actual)
    assert actual[0].total_seq_number == 3
    assert actual[1].total_seq_number == 2
    assert actual[2].total_seq_number == 1


def test_get_deletable_backups_8():
    history = BackupInfoHistory(
        [one('full', 1, 1), one('incremental', 2, 2), one('incremental', 3, 3),
         one('full', 1, 4), one('incremental', 2, 5), one('incremental', 3, 6),
         one('full', 1, 7), one('incremental', 2, 8)]
    )
    actual = get_deletable_backups(history, 3)
    assert 3 == len(actual)
    assert actual[0].total_seq_number == 3
    assert actual[1].total_seq_number == 2
    assert actual[2].total_seq_number == 1


def test_get_deletable_backups_9():
    history = BackupInfoHistory(
        [one('full', 1, 1), one('incremental', 2, 2), one('incremental', 3, 3),
         one('full', 1, 4), one('incremental', 2, 5), one('incremental', 3, 6),
         one('full', 1, 7), one('incremental', 2, 8), one('incremental', 3, 9)]
    )
    actual = get_deletable_backups(history, 3)
    assert 6 == len(actual)
    assert actual[0].total_seq_number == 6
    assert actual[1].total_seq_number == 5
    assert actual[2].total_seq_number == 4
    assert actual[3].total_seq_number == 3
    assert actual[4].total_seq_number == 2
    assert actual[5].total_seq_number == 1


def test_get_deletable_backups_10():
    history = BackupInfoHistory(
        [one('full', 1, 1), one('incremental', 2, 2), one('incremental', 3, 3),
         one('full', 1, 4), one('incremental', 2, 5), one('incremental', 3, 6),
         one('full', 1, 7), one('incremental', 2, 8), one('incremental', 3, 9),
         one('full', 1, 10)]
    )
    actual = get_deletable_backups(history, 3)
    assert 6 == len(actual)
    assert actual[0].total_seq_number == 6
    assert actual[1].total_seq_number == 5
    assert actual[2].total_seq_number == 4
    assert actual[3].total_seq_number == 3
    assert actual[4].total_seq_number == 2
    assert actual[5].total_seq_number == 1


def test_get_deletable_backups_11():
    history = BackupInfoHistory(
        [one('full', 1, 1), one('incremental', 2, 2), one('incremental', 3, 3),
         one('full', 1, 4), one('incremental', 2, 5), one('incremental', 3, 6),
         one('full', 1, 7), one('incremental', 2, 8), one('incremental', 3, 9),
         one('full', 1, 10), one('incremental', 2, 11)]
    )
    actual = get_deletable_backups(history, 3)
    assert 6 == len(actual)
    assert actual[0].total_seq_number == 6
    assert actual[1].total_seq_number == 5
    assert actual[2].total_seq_number == 4
    assert actual[3].total_seq_number == 3
    assert actual[4].total_seq_number == 2
    assert actual[5].total_seq_number == 1


def test_get_deletable_backups_12():
    history = BackupInfoHistory(
        [one('full', 1, 1), one('incremental', 2, 2), one('incremental', 3, 3),
         one('full', 1, 4), one('incremental', 2, 5), one('incremental', 3, 6),
         one('full', 1, 7), one('incremental', 2, 8), one('incremental', 3, 9),
         one('full', 1, 10), one('incremental', 2, 11),
         one('incremental', 3, 12)]
    )
    actual = get_deletable_backups(history, 3)
    expected_len = 9
    assert expected_len == len(actual)
    for i in range(0, 9):
        assert actual[i].total_seq_number == expected_len
        expected_len -= 1
