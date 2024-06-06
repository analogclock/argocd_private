import copy
from enum import Enum
from string import Template

from fsiem_api_client.extensions import chunk


class CH_STORAGE_TYPE(Enum):
    HOT = 'hot',
    WARM = 'warm'


class ClickHouseConfig:

    def _disk_config(self, disk_paths: list, type: CH_STORAGE_TYPE) -> list:
        """Get a list of ClickHouse disk configuration

        Parameters
        ----------
        disk_paths : list
            A list of disk paths, e.g. ['/dev/sdf', '/dev/sde']
        type : CH_STORAGE_TYPE
            ClickHouse storage type: 'hot' or 'warm'

        Returns
        -------
        list
            A list of ClickHouse disk configs, for example:
            [
                {'diskPath':'/dev/sdf','mountPoint':'/data-clickhouse-hot-1'},
                {'diskPath':'/dev/sde','mountPoint':'/data-clickhouse-hot-2'},
            ]
        """
        if not disk_paths:
            raise ValueError('disk_path is None')
        if type not in (CH_STORAGE_TYPE.HOT,
                        CH_STORAGE_TYPE.WARM):
            raise ValueError(f'Unexpected type: {type}')
        config = []
        mount_point = Template('/data-clickhouse-$type-$index')
        for i, disk_path in enumerate(disk_paths):
            mp = mount_point.substitute(type=type.name.lower(), index=i+1)
            config.append({'diskPath': disk_path, 'mountPoint': mp})
        return config

    def _node_disk_config(self, disk_paths: list,
                          type: CH_STORAGE_TYPE) -> list:
        """Get a list of ClickHouse node disk configurations

        Parameters
        ----------
        disk_paths : list
            A list of disk paths, e.g. ['/dev/sdf', '/dev/sde']
        type : CH_STORAGE_TYPE
            ClickHouse storage type: 'hot' or 'warm'

        Returns
        -------
        list
            A list of ClickHouse node disk configs, for example:
            [
                {'data-clickhouse-hot-1':'/dev/sdf'},
                {'data-clickhouse-hot-2':'/dev/sde'}
            ]
        """
        if not disk_paths:
            raise ValueError('disk_path is None')
        if type not in (CH_STORAGE_TYPE.HOT, CH_STORAGE_TYPE.WARM):
            raise ValueError(f'Unexpected type: {type}')
        config = []
        mount_point = Template('data-clickhouse-$type-$index')
        for i, disk_path in enumerate(disk_paths):
            mp = mount_point.substitute(type=type.name.lower(), index=i+1)
            config.append({mp: disk_path})
        return config

    def _node_disks_config(self, hot: list, warm: list, s3_bucket: str,
                           s3_region: str) -> dict:
        """Get a dictionary of ClickHouse node disk configuration.
        Must include hot, may include warm and archive.

        Returns
        -------
        dict
            A json object, for example:
            Hot:
            {
                'hot': {
                    'disks': [{ 'data-clickhouse-hot-1': '/dev/nvme4n1' }]
                },
                'archive': { 'bucket': '<s3_bucket>/<serial_number>',
                             'region': 'us-east-1' }
                           }
            }
            Or hot and warm
            {
                'hot': {
                    'disks': [{ 'data-clickhouse-hot-1': '/dev/nvme4n1' }]
                },
                'warm': {
                    'disks': [{ 'data-clickhouse-warm-1': '/dev/nvme5n1' }]
                },
                'archive': { 'bucket': '<s3_bucket>/<serial_number>',
                             'region': 'us-east-1' }
                           }
            }
        """
        if not hot:
            raise ValueError('hot disks are None')
        h = self._node_disk_config(hot, CH_STORAGE_TYPE.HOT)
        result = {}
        result['hot'] = {'disks': h}
        if warm:
            w = self._node_disk_config(warm, CH_STORAGE_TYPE.WARM)
            result['warm'] = {'disks': w}
        if s3_bucket:
            result['archive'] = {'bucket': s3_bucket, 'region': s3_region}
        return result

    def disk_config(self, hot: list, warm: list) -> dict:
        """Get json dictionary of ClickHouse disk configuration

        Returns
        -------
        dict
            A json object, for example:
            Hot:
            {
                'hotList': [
                    {
                        'diskPath': '/dev/nvme2n1',
                        'mountPoint': '/data-clickhouse-hot-1'
                    }
                ]
            }
            Or, hot and warm
            {
                'hotList': [
                    {
                        'diskPath': '/dev/nvme2n1',
                        'mountPoint': '/data-clickhouse-hot-1'
                    }
                ],
                'warmList': [
                    {
                        'diskPath': '/dev/nvme3n1',
                        'mountPoint': '/data-clickhouse-warm-1'
                    }
                ]
            }
        """
        if not hot:
            raise ValueError('hot disks are None')
        h = self._disk_config(hot, CH_STORAGE_TYPE.HOT)
        if warm:
            w = self._disk_config(warm, CH_STORAGE_TYPE.WARM)
        return {'hotList': h, 'warmList': w} if warm else {'hotList': h}

    def zookeeper_config(self, keepers: list) -> dict:
        """Get a dictionary of ClickHouse zookeeper configuration

        Combines all PrivateIpAddress of keepers and returns a
        dictionary (not a list) with:

            'string index number (starts from 1)' => 'IP Address'

        Parameters
        ----------
        keepers : list
            A list of keeper info, if super is used as a keeper, it should
            be the first element (FSIEM requirement)

        Returns
        -------
        dict
            A dictionary of ClickHouse zookeeper IPs, for example:
            {
                '1': '10.0.103.253',
                '2': '10.0.101.169',
                '3': '10.0.102.221'
            }
        """
        # we must always have keepers
        if not keepers:
            raise ValueError('keepers is None')

        ips = list(map(lambda x: x['PrivateIpAddress'], keepers))

        config = {}

        # Note starts from 1 and 1 is reserved for super
        i = 1
        for ip in ips:
            config.update({str(i): ip})
            i += 1
        return config

    def shards_config(self, supers: list, workers: list, s3_bucket: str,
                      s3_region: str) -> list:
        """Get a list of ClickHouse shard configuration

        Uses supers and workers info to make a list of shard config.
        Note super does not participate in ingest/query.

        Parameters
        ----------
        supers: list
            A list of supers info
        workers: list
            A list of workers info
        s3_bucket: str
            Bucket name (with additional path) where to store archive data
        s3_region: str
            S3 bucket region

        Returns
        -------
        list
            A list of shards, for example:
            [
                {
                    'id': 1, 'type': 'shard', 'name': 'Shard 1', 'index': 1,
                    'nodes': [
                        {
                            'id': 1, 'ip': '10.0.103.253', 'name': 'Replica 2',
                            'ingest': true, 'query': true,
                            'storage_configuration': {
                                'hot': { 'disks': [
                                    {'data-clickhouse-hot-1': '/dev/nvme4n1'} ]
                                },
                                'archive': {
                                    'bucket': '<s3_bucket>/<serial_number>',
                                    'region': 'us-east-1' }
                                }
                            }, 'usingAwsToArchive': true
                        }, {
                            'id': 2, 'ip': '10.0.101.169', 'name': 'Replica 3',
                            'ingest': true, 'query': true,
                            'storage_configuration': {
                                'hot': {'disks': [
                                    {'data-clickhouse-hot-1': '/dev/nvme4n1'}]
                                },
                                'archive': {
                                    'bucket': '<s3_bucket>/<serial_number>',
                                    'region': 'us-east-1' }
                                }
                            }, 'usingAwsToArchive': true
                        },
                        {
                            'id': 3, 'ip': '10.0.101.100', 'name': 'Replica 3',
                            'ingest': false, 'query': false,
                            'storage_configuration': {
                                'hot': {'disks': [
                                    {'data-clickhouse-hot-1': '/dev/nvme4n1'}]
                                },
                                'archive': {
                                    'bucket': '<s3_bucket>/<serial_number>',
                                    'region': 'us-east-1' }
                                }
                            }, 'usingAwsToArchive': true
                        }
                    ]
                }
            ]
        """
        if not workers:
            raise ValueError('workers is None')

        config = []

        # Replicas
        nodes = []

        # Super has to have an id 1, as that's what it's configured by default
        if supers:
            print('Only the first super is considered')
            super = supers[0]
            hot = super['ClickHouseDiskPaths']
            storage_cfg = self._node_disks_config(hot, None, None, None)
            node = {
                'id': 1, 'ip': super['PrivateIpAddress'],
                'ingest': False, 'query': False,
                'name': 'Replica 1',
                'storage_configuration': storage_cfg,
                'usingAwsToArchive': False
            }
            nodes.append(node)

        # create a set of 2 workers
        # i.e 4 workers == [[w_1, w_2], [w_3, w_4]]
        shard_i = 1
        for chunk_workers in chunk(workers, 2):
            # 0 is not in use, 1 is taken by super, so starting from 2

            i = 2
            for info in chunk_workers:
                hot = info['ClickHouseDiskPaths']
                storage_cfg = self._node_disks_config(hot, None,
                                                      s3_bucket, s3_region)
                node = {
                    'id': i, 'ip': info['PrivateIpAddress'], 'ingest': True,
                    'name': f'Replica {i}', 'query': True,
                    'storage_configuration': storage_cfg,
                    'usingAwsToArchive': True
                }
                nodes.append(node)
                i += 1

            # Shards
            # deep copy our existing nodes
            # if we do not then we have a shallow
            # copy meaning our clear will overwrite
            shard = {
                'id': shard_i,
                'type': 'shard',
                'name': f'Shard {shard_i}',
                'index': shard_i,
                'nodes': copy.deepcopy(nodes)
            }

            # append the new shard to the cluster
            # add 1 to our shards
            # clear our existing nodes, ready to run again
            config.append(shard)
            shard_i += 1
            nodes.clear()
        return config
