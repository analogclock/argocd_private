import pytest
from fsiem_api_client.clickhouse_config import (CH_STORAGE_TYPE,
                                                ClickHouseConfig)


class TestClickHouseConfig:

    def test__disk_config(self):
        uut = ClickHouseConfig()
        with pytest.raises(ValueError):
            uut._disk_config('', CH_STORAGE_TYPE.HOT)
        with pytest.raises(ValueError):
            uut._disk_config(['foo'], 'foo')

    def test__disk_config_hot(self):
        uut = ClickHouseConfig()
        disks = ['/dev/1', '/dev/2']
        expected = [
            {'diskPath': '/dev/1', 'mountPoint': '/data-clickhouse-hot-1'},
            {'diskPath': '/dev/2', 'mountPoint': '/data-clickhouse-hot-2'},
        ]
        actual = uut._disk_config(disks, CH_STORAGE_TYPE.HOT)
        assert expected[0]['diskPath'] == actual[0]['diskPath']
        assert expected[0]['mountPoint'] == actual[0]['mountPoint']
        assert expected[1]['diskPath'] == actual[1]['diskPath']
        assert expected[1]['mountPoint'] == actual[1]['mountPoint']

    def test__disk_config_warm(self):
        uut = ClickHouseConfig()
        disks = ['/dev/1', '/dev/2', '/dev/3']
        expected = [
            {'diskPath': '/dev/1', 'mountPoint': '/data-clickhouse-warm-1'},
            {'diskPath': '/dev/2', 'mountPoint': '/data-clickhouse-warm-2'},
            {'diskPath': '/dev/3', 'mountPoint': '/data-clickhouse-warm-3'},
        ]
        actual = uut._disk_config(disks, CH_STORAGE_TYPE.WARM)
        for i, x in enumerate(expected):
            assert expected[i]['diskPath'] == actual[i]['diskPath']
            assert expected[i]['mountPoint'] == actual[i]['mountPoint']

    def test_disk_config_hot(self):
        uut = ClickHouseConfig()
        hot = ['/dev/1', '/dev/2']
        expected = {
            'hotList':
            [
                {'diskPath': '/dev/1', 'mountPoint': '/data-clickhouse-hot-1'},
                {'diskPath': '/dev/2', 'mountPoint': '/data-clickhouse-hot-2'}
            ]
        }
        actual = uut.disk_config(hot, None)
        assert expected == actual

    def test_disk_config_warm(self):
        uut = ClickHouseConfig()
        hot = ['/dev/1', '/dev/2']
        warm = ['/dev/3', '/dev/4']
        expected = {
            'hotList': [
                {'diskPath': '/dev/1', 'mountPoint': '/data-clickhouse-hot-1'},
                {'diskPath': '/dev/2', 'mountPoint': '/data-clickhouse-hot-2'}
            ],
            'warmList':
            [
                {'diskPath': '/dev/3', 'mountPoint': '/data-clickhouse-warm-1'},  # noqa
                {'diskPath': '/dev/4', 'mountPoint': '/data-clickhouse-warm-2'}
            ]
        }
        actual = uut.disk_config(hot, warm)
        assert expected == actual

    def test_zookeeper_config(self):
        uut = ClickHouseConfig()
        keepers = [
            {'PrivateIpAddress': '111'},
            {'PrivateIpAddress': '222'},
            {'PrivateIpAddress': '333'},
            {'PrivateIpAddress': '444'}
        ]
        expected = {
            '1': '111',
            '2': '222',
            '3': '333',
            '4': '444',
        }
        actual = uut.zookeeper_config(keepers)
        assert expected == actual
        first = {list(actual.keys())[0]: list(actual.values())[0]}
        second = {list(actual.keys())[1]: list(actual.values())[1]}
        third = {list(actual.keys())[2]: list(actual.values())[2]}
        fourth = {list(actual.keys())[3]: list(actual.values())[3]}
        assert {'1': '111'} == first
        assert {'2': '222'} == second
        assert {'3': '333'} == third
        assert {'4': '444'} == fourth

    def test__node_disk_config(self):
        uut = ClickHouseConfig()
        hot = ['/dev/1', '/dev/2']
        expected = [
            {'data-clickhouse-hot-1': '/dev/1'},
            {'data-clickhouse-hot-2': '/dev/2'},
        ]
        actual = uut._node_disk_config(hot, CH_STORAGE_TYPE.HOT)
        assert expected == actual

        warm = ['/dev/3', '/dev/4']
        expected = [
            {'data-clickhouse-warm-1': '/dev/3'},
            {'data-clickhouse-warm-2': '/dev/4'},
        ]
        actual = uut._node_disk_config(warm, CH_STORAGE_TYPE.WARM)
        assert expected == actual

    def test__node_disks_config(self):
        uut = ClickHouseConfig()
        hot = ['/dev/1', '/dev/2']
        expected = {
            'hot': {
                'disks': [
                    {'data-clickhouse-hot-1': '/dev/1'},
                    {'data-clickhouse-hot-2': '/dev/2'}
                ]
            },
            'archive': {
                'bucket': '<s3_bucket>/<serial_number>',
                'region': 'us-east-1'
            }
        }
        actual = uut._node_disks_config(
            hot, None, '<s3_bucket>/<serial_number>', 'us-east-1')
        assert expected == actual

        warm = ['/dev/3', '/dev/4']
        expected = {
            'hot': {
                'disks': [
                    {'data-clickhouse-hot-1': '/dev/1'},
                    {'data-clickhouse-hot-2': '/dev/2'}
                ]
            },
            'warm': {
                'disks': [
                    {'data-clickhouse-warm-1': '/dev/3'},
                    {'data-clickhouse-warm-2': '/dev/4'}
                ]
            },
            'archive': {
                'bucket': '<s3_bucket>/<serial_number>',
                'region': 'us-east-1'
            }
        }
        actual = uut._node_disks_config(hot, warm,
                                        '<s3_bucket>/<serial_number>',
                                        'us-east-1')
        assert expected == actual

    def test_shards_config(self):
        uut = ClickHouseConfig()
        workers = [
            {'PrivateIpAddress': '1', 'ClickHouseDiskPaths': ['/dev/1']},
            {'PrivateIpAddress': '2', 'ClickHouseDiskPaths': ['/dev/2']},
        ]
        expected = [{
            'id': 1,
            'type': 'shard',
            'name': 'Shard 1',
            'index': 1,
            'nodes': [
                {
                    'id': 2,
                    'ip': '1',
                    'name': 'Replica 2',
                    'ingest': True,
                    'query': True,
                    'storage_configuration': {
                        'hot': {
                            'disks': [
                                {'data-clickhouse-hot-1': '/dev/1'}
                            ]
                        },
                        'archive': {
                            'bucket': '<s3_bucket>/<serial_number>',
                            'region': 'us-east-1'
                        }
                    },
                    'usingAwsToArchive': True
                },
                {
                    'id': 3,
                    'ip': '2',
                    'name': 'Replica 3',
                    'ingest': True,
                    'query': True,
                    'storage_configuration': {
                        'hot': {
                            'disks': [
                                {'data-clickhouse-hot-1': '/dev/2'}
                            ]
                        }, 'archive': {
                            'bucket': '<s3_bucket>/<serial_number>',
                            'region': 'us-east-1'
                        }
                    },
                    'usingAwsToArchive': True
                }
            ]
        }]
        actual = uut.shards_config(None, workers,
                                   '<s3_bucket>/<serial_number>', 'us-east-1')
        assert expected == actual

    def test_shards_config_with_super(self):
        uut = ClickHouseConfig()
        supers = [
            {'PrivateIpAddress': '1', 'ClickHouseDiskPaths': ['/dev/super']},
        ]
        workers = [
            {'PrivateIpAddress': '2', 'ClickHouseDiskPaths': ['/dev/1']},
            {'PrivateIpAddress': '3', 'ClickHouseDiskPaths': ['/dev/2']},
        ]
        expected = [{
            'id': 1,
            'type': 'shard',
            'name': 'Shard 1',
            'index': 1,
            'nodes': [
                {
                    'id': 1,
                    'ip': '1',
                    'name': 'Replica 1',
                    'ingest': False,
                    'query': False,
                    'storage_configuration': {
                        'hot': {
                            'disks': [
                                {'data-clickhouse-hot-1': '/dev/super'}
                            ]
                        }
                    },
                    'usingAwsToArchive': False
                },
                {
                    'id': 2,
                    'ip': '2',
                    'name': 'Replica 2',
                    'ingest': True,
                    'query': True,
                    'storage_configuration': {
                        'hot': {
                            'disks': [
                                {'data-clickhouse-hot-1': '/dev/1'}
                            ]
                        },
                        'archive': {
                            'bucket': '<s3_bucket>/<serial_number>',
                            'region': 'us-east-1'
                        }
                    },
                    'usingAwsToArchive': True
                },
                {
                    'id': 3,
                    'ip': '3',
                    'name': 'Replica 3',
                    'ingest': True,
                    'query': True,
                    'storage_configuration': {
                        'hot': {
                            'disks': [
                                {'data-clickhouse-hot-1': '/dev/2'}
                            ]
                        }, 'archive': {
                            'bucket': '<s3_bucket>/<serial_number>',
                            'region': 'us-east-1'
                        }
                    },
                    'usingAwsToArchive': True
                }
            ]
        }]
        actual = uut.shards_config(supers, workers,
                                   '<s3_bucket>/<serial_number>', 'us-east-1')
        assert expected == actual

    def test_multiple_shards_config(self):
        uut = ClickHouseConfig()

        workers = [
            {'PrivateIpAddress': '1', 'ClickHouseDiskPaths': ['/dev/1']},
            {'PrivateIpAddress': '2', 'ClickHouseDiskPaths': ['/dev/2']},
            {'PrivateIpAddress': '3', 'ClickHouseDiskPaths': ['/dev/3']},
            {'PrivateIpAddress': '4', 'ClickHouseDiskPaths': ['/dev/4']},
        ]
        expected = [
            {
                'id': 1,
                'type': 'shard',
                'name': 'Shard 1',
                'index': 1,
                'nodes': [
                    {
                        'id': 2,
                        'ip': '1',
                        'name': 'Replica 2',
                        'ingest': True,
                        'query': True,
                        'storage_configuration': {
                            'hot': {
                                'disks': [
                                    {'data-clickhouse-hot-1': '/dev/1'}
                                ]
                            },
                            'archive': {
                                'bucket': '<s3_bucket>/<serial_number>',
                                'region': 'us-east-1'
                            }
                        },
                        'usingAwsToArchive': True
                    },
                    {
                        'id': 3,
                        'ip': '2',
                        'name': 'Replica 3',
                        'ingest': True,
                        'query': True,
                        'storage_configuration': {
                            'hot': {
                                'disks': [
                                    {'data-clickhouse-hot-1': '/dev/2'}
                                ]
                            }, 'archive': {
                                'bucket': '<s3_bucket>/<serial_number>',
                                'region': 'us-east-1'
                            }
                        },
                        'usingAwsToArchive': True
                    }
                ]
            },
            {
                'id': 2,
                'type': 'shard',
                'name': 'Shard 2',
                'index': 2,
                'nodes': [
                    {
                        'id': 2,
                        'ip': '3',
                        'name': 'Replica 2',
                        'ingest': True,
                        'query': True,
                        'storage_configuration': {
                            'hot': {
                                'disks': [
                                    {'data-clickhouse-hot-1': '/dev/3'}
                                ]
                            },
                            'archive': {
                                'bucket': '<s3_bucket>/<serial_number>',
                                'region': 'us-east-1'
                            }
                        },
                        'usingAwsToArchive': True
                    },
                    {
                        'id': 3,
                        'ip': '4',
                        'name': 'Replica 3',
                        'ingest': True,
                        'query': True,
                        'storage_configuration': {
                            'hot': {
                                'disks': [
                                    {'data-clickhouse-hot-1': '/dev/4'}
                                ]
                            }, 'archive': {
                                'bucket': '<s3_bucket>/<serial_number>',
                                'region': 'us-east-1'
                            }
                        },
                        'usingAwsToArchive': True
                    }
                ]
            }
        ]
        actual = uut.shards_config(None, workers,
                                   '<s3_bucket>/<serial_number>', 'us-east-1')

        assert len(expected) == len(actual)
        assert expected == actual
