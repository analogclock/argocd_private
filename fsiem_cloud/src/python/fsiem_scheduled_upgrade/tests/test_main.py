import boto3
from moto import mock_aws
from freezegun import freeze_time
from sched_upgrades_table import SchedUpgradesTable
from main import (find_pending_upgrades, check_activation_entry,
                  get_upgrade_path)


def create_table_range_key(table_name: str, region: str, hash_key: str,
                           range_key: str):
    client = boto3.client('dynamodb', region_name=region)
    client.create_table(
        TableName=table_name,
        AttributeDefinitions=[
            {
                'AttributeName': hash_key,
                'AttributeType': 'S'
            },
            {
                'AttributeName': range_key,
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': hash_key,
                'KeyType': 'HASH'
            },
            {
                'AttributeName': range_key,
                'KeyType': 'RANGE'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )


def create_table(table_name: str, region: str, schema: str):
    client = boto3.client('dynamodb', region_name=region)
    client.create_table(
        TableName=table_name,
        AttributeDefinitions=[
            {
                'AttributeName': schema,
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': schema,
                'KeyType': 'HASH'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )


def put_item(table_name: str, region: str, item: dict):
    client = boto3.client('dynamodb', region_name=region)
    client.put_item(
        TableName=table_name,
        Item=item
    )


def create_instance(serial_number: str, role: str, region: str):
    client = boto3.client('ec2', region_name=region)
    image_response = client.describe_images()
    image_id = image_response['Images'][0]['ImageId']

    ec2 = boto3.resource('ec2')
    response = ec2.create_instances(
        ImageId=image_id,
        InstanceType='m1.small',
        MaxCount=2,
        MinCount=2,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'SerialNumber',
                        'Value': serial_number
                    },
                    {
                        'Key': 'Role',
                        'Value': role
                    }
                ]
            }
        ]
    )
    instance_ids = []
    for instance in response:
        instance_ids.append(instance.id)
    response = client.describe_instances(
        InstanceIds=instance_ids
    )
    return instance_ids


@mock_aws
def test_find_pending_upgrades_correct():
    table = 'marktest'
    region = 'us-east-1'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    create_table_range_key(table, region, hash_key, range_key)
    sched_table = SchedUpgradesTable(table, region)

    items = [
        {
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
        },
        {
            hash_key: {
                'S': 'test456'
            },
            range_key: {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2902-05-23T02:26:00'
            },
            'status': {
                'S': 'Pending'
            }
        },
        {
            hash_key: {
                'S': 'test789'
            },
            range_key: {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2002-05-23T02:26:00'
            },
            'status': {
                'S': 'Failed'
            }
        }
    ]

    expected = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2002-05-23T02:26:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]

    actual = find_pending_upgrades(items, sched_table)
    assert actual == expected


@mock_aws
@freeze_time('2023-01-31 01:00:00', tz_offset=0)
def test_find_pending_upgrades_close_times():
    table = 'marktest'
    region = 'us-east-1'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    create_table_range_key(table, region, hash_key, range_key)
    sched_table = SchedUpgradesTable(table, region)

    items = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2023-01-31T00:00:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]

    expected = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2023-01-31T00:00:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]
    actual = find_pending_upgrades(items, sched_table)
    assert actual == expected


@mock_aws
@freeze_time('2023-03-31 01:00:00', tz_offset=0)
def test_find_pending_upgrades_scheduledLocal():
    table = 'marktest'
    region = 'us-east-1'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    create_table_range_key(table, region, hash_key, range_key)
    sched_table = SchedUpgradesTable(table, region)

    items = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2023-03-22T00:00:00'
            },
            'scheduledLocal': {
                'S': '2023-03-22T00:00:00.0000000+01:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]

    expected = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2023-03-22T00:00:00'
            },
            'scheduledLocal': {
                'S': '2023-03-22T00:00:00.0000000+01:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]
    actual = find_pending_upgrades(items, sched_table)
    assert actual == expected


@mock_aws
@freeze_time('2023-03-22 00:59:59.999999', tz_offset=0)
def test_find_pending_upgrades_scheduledLocal_near_time_not_added():
    table = 'marktest'
    region = 'us-east-1'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    create_table_range_key(table, region, hash_key, range_key)
    sched_table = SchedUpgradesTable(table, region)

    items = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2023-03-22T01:00:00'
            },
            'scheduledLocal': {
                'S': '2023-03-22T02:00:00+01:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]

    actual = find_pending_upgrades(items, sched_table)
    assert len(actual) == 0


@mock_aws
@freeze_time('2023-03-22 01:00:00.999999', tz_offset=0)
def test_find_pending_upgrades_scheduledLocal_just_over():
    table = 'marktest'
    region = 'us-east-1'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    create_table_range_key(table, region, hash_key, range_key)
    sched_table = SchedUpgradesTable(table, region)

    items = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2023-03-22T01:00:00'
            },
            'scheduledLocal': {
                'S': '2023-03-22T02:00:00.0000000+01:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]

    expected = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2023-03-22T01:00:00'
            },
            'scheduledLocal': {
                'S': '2023-03-22T02:00:00.0000000+01:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]
    actual = find_pending_upgrades(items, sched_table)
    assert actual == expected


@mock_aws
def test_find_pending_upgrades_invalid_date_string():
    table = 'marktest'
    region = 'us-east-1'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    create_table_range_key(table, region, hash_key, range_key)
    sched_table = SchedUpgradesTable(table, region)

    items = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2023-13-31T00:00:00.0000000'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]

    expected = []
    actual = find_pending_upgrades(items, sched_table)
    assert actual == expected


@mock_aws
def check_activation_entry_correct():
    table = 'marktest'
    region = 'us-east-1'
    schema = 'serialNumber'
    create_table(table, region, schema)

    item1 = {
        'serialNumber': {
            'S': 'test123'
        },
        'status': {
            'S': 'LicenseInProgress'
        }
    }
    put_item(table, region, item1)

    item2 = {
        'serialNumber': {
            'S': 'test456'
        },
        'status': {
            'S': 'Complete'
        }
    }
    put_item(table, region, item2)

    item3 = {
        'serialNumber': {
            'S': 'test789'
        },
        'status': {
            'S': 'CreateFailed'
        }
    }
    put_item(table, region, item3)

    items = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2002-05-23T02:26:00'
            },
            'status': {
                'S': 'Pending'
            }
        },
        {
            'serialNumber': {
                'S': 'test456'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2002-05-23T02:26:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]
    expected = [
        {
            'serialNumber': {
                'S': 'test456'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2002-05-23T02:26:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]
    actual = check_activation_entry(table, region, items)
    assert actual == expected


@mock_aws
def check_activation_entry_prevent_update():
    table = 'marktest'
    region = 'us-east-1'
    schema = 'serialNumber'
    create_table(table, region, schema)

    item1 = {
        'serialNumber': {
            'S': 'test123'
        },
        'preventUpdate': {
            'BOOL': True
        },
        'status': {
            'S': 'Complete'
        }
    }
    put_item(table, region, item1)

    item2 = {
        'serialNumber': {
            'S': 'test456'
        },
        'status': {
            'S': 'Complete'
        }
    }
    put_item(table, region, item2)

    items = [
        {
            'serialNumber': {
                'S': 'test123'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2002-05-23T02:26:00'
            },
            'status': {
                'S': 'Pending'
            }
        },
        {
            'serialNumber': {
                'S': 'test456'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2002-05-23T02:26:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]
    expected = [
        {
            'serialNumber': {
                'S': 'test456'
            },
            'upgradePath': {
                'S': '6.4.0_6.5.0'
            },
            'scheduled': {
                'S': '2002-05-23T02:26:00'
            },
            'status': {
                'S': 'Pending'
            }
        }
    ]
    actual = check_activation_entry(table, region, items)
    assert actual == expected


@mock_aws
def test_get_upgrade_path_complete():
    table = 'marktest'
    region = 'us-east-1'
    schema = 'upgradePath'
    create_table(table, region, schema)

    sched_table = 'marktest2'
    hash_key = 'serialNumber'
    range_key = 'upgradePath'
    create_table_range_key(sched_table, region, hash_key, range_key)
    sched_table = SchedUpgradesTable(table, region)

    upgrade_path = '6.4.0_6.5.0'
    serial_no = 'fsmcld000001'

    item = {
        schema: {
            'S': upgrade_path
        },
        'currentVersion': {
            'S': '6.4.0'
        },
        'newVersion': {
            'S': '6.5.0'
        },
        'zipName': {
            'S': 'FSM_Upgrade_All_6.5.0_build1511'
        },
        'ssmDocName': {
            'S': 'upgrade_node_640_650_playground'
        }
    }
    put_item(table, region, item)

    expected = item
    actual = get_upgrade_path(upgrade_path, table, region, serial_no,
                              sched_table)
    assert actual == expected


# trigger_automation

# get_automation_status
