from json import load
from scrape_metrics import (sort_query_duration_response,
                            sort_query_count_response,
                            sort_clickhouse_metrics_response)


def test_sort_query_duration_response():
    output = {
        'meta': [
            {'name': 'event_time_h', 'type': 'DateTime'},
            {'name': 'count_m', 'type': 'UInt64'},
            {'name': 'avg_duration', 'type': 'Float64'}
        ],
        'data': [
            {
                'event_time_h': '2023-07-24 17:00:00',
                'count_m': '333',
                'avg_duration': 1.5555555555555556
            },
            {
                'event_time_h': '2023-07-24 18:00:00',
                'count_m': '457',
                'avg_duration': 1.5929978118161925
            },
            {
                'event_time_h': '2023-07-24 19:00:00',
                'count_m': '463',
                'avg_duration': 1.8272138228941686
            },
            {
                'event_time_h': '2023-07-24 20:00:00',
                'count_m': '455',
                'avg_duration': 1.778021978021978
            },
            {
                'event_time_h': '2023-07-24 21:00:00',
                'count_m': '456',
                'avg_duration': 1.7214912280701755
            },
            {
                'event_time_h': '2023-07-24 22:00:00',
                'count_m': '456',
                'avg_duration': 1.5986842105263157
            },
            {
                'event_time_h': '2023-07-24 23:00:00',
                'count_m': '455',
                'avg_duration': 1.6747252747252748
            }
        ],
        'rows': 29,
        'statistics': {
            'elapsed': 0.007363966,
            'rows_read': 156701,
            'bytes_read': 2194252
        }
    }

    expected = {
        'event_time_h': '2023-07-24 23:00:00',
        'count_m': '455',
        'avg_duration': 1.6747252747252748
    }

    actual = sort_query_duration_response(output)
    assert actual == expected


def test_sort_query_count_response():
    output = {
        "meta": [
            {
                "name": "event_time_m",
                "type": "DateTime"
            },
            {
                "name": "client_name",
                "type": "String"
            },
            {
                "name": "count()",
                "type": "UInt64"
            },
            {
                "name": "query_kind",
                "type": "LowCardinality(String)"
            }
        ],
        "data": [
            {
                "event_time_m": "2023-07-19 20:01:00",
                "client_name": "ClickHouse",
                "count()": "2",
                "query_kind": "Select"
            },
            {
                "event_time_m": "2023-07-19 20:01:00",
                "client_name": "unknown_or_http",
                "count()": "2",
                "query_kind": "Select"
            },
            {
                "event_time_m": "2023-07-19 20:01:00",
                "client_name": "ClickHouse client",
                "count()": "7",
                "query_kind": "Select"
            },
            {
                "event_time_m": "2023-07-19 20:00:00",
                "client_name": "ClickHouse",
                "count()": "5",
                "query_kind": "Select"
            },
            {
                "event_time_m": "2023-07-19 20:00:00",
                "client_name": "unknown_or_http",
                "count()": "10",
                "query_kind": "Select"
            },
            {
                "event_time_m": "2023-07-19 19:59:00",
                "client_name": "ClickHouse",
                "count()": "2",
                "query_kind": "Select"
            },
            {
                "event_time_m": "2023-07-19 19:59:00",
                "client_name": "unknown_or_http",
                "count()": "2",
                "query_kind": "Select"
            },
        ],
        "rows": 23,
        "rows_before_limit_at_least": 23,
        "statistics": {
            "elapsed": 0.006889924,
            "rows_read": 10540,
            "bytes_read": 173523
        }
    }
    expected = {
        'Select': {
            'ClickHouse': '2',
            'unknown_or_http': '2',
            'ClickHouse client': '7'
        }
    }
    actual = sort_query_count_response(output)
    assert actual == expected


def test_sort_clickhouse_metrics_response():
    with open('test/clickhouse_metrics_output.json', 'r') as f:
        output = load(f)
    expected = {
        'ActiveAsyncDrainedConnections': '0',
        'ActiveSyncDrainedConnections': '0',
        'AsyncDrainedConnections': '0',
        'AsynchronousReadWait': '0',
        'BackgroundBufferFlushSchedulePoolTask': '0',
        'BackgroundCommonPoolTask': '0',
        'BackgroundDistributedSchedulePoolTask': '0',
        'BackgroundFetchesPoolTask': '0',
        'BackgroundMergesAndMutationsPoolTask': '0',
        'BackgroundMessageBrokerSchedulePoolTask': '0',
        'BackgroundMovePoolTask': '0',
        'BackgroundSchedulePoolTask': '0',
        'BrokenDistributedFilesToInsert': '0',
        'CacheDetachedFileSegments': '0',
        'CacheDictionaryUpdateQueueBatches': '0',
        'CacheDictionaryUpdateQueueKeys': '0',
        'CacheFileSegments': '1883',
        'ContextLockWait': '0',
        'DelayedInserts': '0',
        'DictCacheRequests': '0',
        'DiskSpaceReservedForMerge': '0',
        'DistributedFilesToInsert': '0',
        'DistributedSend': '0',
        'EphemeralNode': '2',
        'FilesystemCacheReadBuffers': '0',
        'GlobalThread': '276',
        'GlobalThreadActive': '263',
        'HTTPConnection': '0',
        'InterserverConnection': '0',
        'KafkaAssignedPartitions': '0',
        'KafkaBackgroundReads': '0',
        'KafkaConsumers': '0',
        'KafkaConsumersInUse': '0',
        'KafkaConsumersWithAssignment': '0',
        'KafkaLibrdkafkaThreads': '0',
        'KafkaProducers': '0',
        'KafkaWrites': '0',
        'LocalThread': '110',
        'LocalThreadActive': '40',
        'MMappedFileBytes': '486789408',
        'MMappedFiles': '7',
        'MaxDDLEntryID': '0',
        'MaxPushedDDLEntryID': '0',
        'MemoryTracking': '1464078336',
        'Merge': '0',
        'MySQLConnection': '0',
        'NetworkReceive': '0',
        'NetworkSend': '0',
        'OpenFileForRead': '23',
        'OpenFileForWrite': '0',
        'PartMutation': '0',
        'PartsActive': '894',
        'PartsCommitted': '894',
        'PartsCompact': '1712',
        'PartsDeleteOnDestroy': '0',
        'PartsDeleting': '0',
        'PartsInMemory': '0',
        'PartsOutdated': '2420',
        'PartsPreActive': '0',
        'PartsPreCommitted': '0',
        'PartsTemporary': '0',
        'PartsWide': '1602',
        'PendingAsyncInsert': '0',
        'PostgreSQLConnection': '0',
        'Query': '1',
        'QueryPreempted': '0',
        'QueryThread': '0',
        'RWLockActiveReaders': '1',
        'RWLockActiveWriters': '0',
        'RWLockWaitingReaders': '0',
        'RWLockWaitingWriters': '0',
        'Read': '2',
        'ReadonlyReplica': '0',
        'ReplicatedChecks': '0',
        'ReplicatedFetch': '0',
        'ReplicatedSend': '0',
        'Revision': '54463',
        'S3Requests': '0',
        'SendExternalTables': '0',
        'SendScalars': '0',
        'StorageBufferBytes': '0',
        'StorageBufferRows': '0',
        'SyncDrainedConnections': '0',
        'TCPConnection': '2',
        'TablesToDropQueueSize': '0',
        'VersionInteger': '22006001',
        'Write': '0',
        'ZooKeeperRequest': '0',
        'ZooKeeperSession': '1',
        'ZooKeeperWatch': '5',
    }
    actual = sort_clickhouse_metrics_response(output)
    assert actual == expected
