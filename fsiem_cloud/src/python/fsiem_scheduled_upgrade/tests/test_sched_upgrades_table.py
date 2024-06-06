from moto import mock_aws
from sched_upgrades_table import SchedUpgradesTable
from test_main import create_table_range_key, put_item


@mock_aws
def test_get_scheduled_upgrades_correct():
    table = 'marktest'
    region = 'us-east-1'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    create_table_range_key(table, region, hash_key, range_key)

    item = {
        hash_key: {
            'S': 'test123'
        },
        range_key: {
            'S': '6.4.0_6.5.0'
        },
        'scheduled': {
            'S': '2002-05-23T02:26:00'
        },
        'status': {
            'S': 'Pending'
        }
    }
    put_item(table, region, item)
    sched_table = SchedUpgradesTable(table, region)

    expected = [item]
    actual = sched_table.get_all_upgrades()
    assert actual == expected


@mock_aws
def test_update_scheduled_upgrade_status_pending():
    table = 'marktest'
    region = 'us-east-1'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    serial_number = 'test123'
    upgrade_path = '6.4.0_6.5.0'
    create_table_range_key(table, region, hash_key, range_key)

    item = {
        hash_key: {
            'S': serial_number
        },
        range_key: {
            'S': upgrade_path
        },
        'scheduled': {
            'S': '6.5.0'
        },
        'status': {
            'S': 'Pending'
        }
    }
    put_item(table, region, item)
    sched_table = SchedUpgradesTable(table, region)

    expected = None
    actual = sched_table.update_status(serial_number, upgrade_path,
                                       sched_table.status_pending)
    assert actual == expected


@mock_aws
def test_update_scheduled_upgrade_status_complete():
    table = 'marktest'
    region = 'us-east-1'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    serial_number = 'test123'
    upgrade_path = '6.4.0_6.5.0'
    create_table_range_key(table, region, hash_key, range_key)

    item = {
        hash_key: {
            'S': serial_number
        },
        range_key: {
            'S': upgrade_path
        },
        'scheduled': {
            'S': '6.5.0'
        },
        'status': {
            'S': 'Complete'
        }
    }
    put_item(table, region, item)
    sched_table = SchedUpgradesTable(table, region)

    expected = None
    actual = sched_table.update_status(serial_number, upgrade_path,
                                       sched_table.status_complete)
    assert actual == expected


@mock_aws
def test_update_scheduled_upgrade_status_failed():
    table = 'marktest'
    region = 'us-east-1'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    serial_number = 'test123'
    upgrade_path = '6.4.0_6.5.0'
    create_table_range_key(table, region, hash_key, range_key)

    item = {
        hash_key: {
            'S': serial_number
        },
        range_key: {
            'S': upgrade_path
        },
        'scheduled': {
            'S': '6.5.0'
        },
        'status': {
            'S': 'Failed'
        }
    }
    put_item(table, region, item)
    sched_table = SchedUpgradesTable(table, region)

    expected = None
    actual = sched_table.update_status(serial_number, upgrade_path,
                                       sched_table.status_failed)
    assert actual == expected
