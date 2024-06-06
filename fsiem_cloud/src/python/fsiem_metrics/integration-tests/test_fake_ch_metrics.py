import json
import random
from datetime import datetime, timedelta

from fsiem_api_client.aws.dynamodb_simple_table import DynamoDbSimpleTable
from fsiem_api_client.gzip_compress import GzipCompress

sn = 'FSMCLD0000000185'
region = 'us-east-2'
metrics_table = 'fsiem_metrics_storage_dev'
db = DynamoDbSimpleTable(metrics_table, 'us-east-1')

ONE_MB_IN_BYTES = 1 * 1024 * 1024
ONE_GB_IN_BYTES = 1 * 1024 * ONE_MB_IN_BYTES
TEN_GB_IN_BYTES = 10 * ONE_GB_IN_BYTES


def generate_data(start_date, num_days):
    """Generate fake data that mimics metrics in ClickHouse
    Example output:

    [
        {"d": "20240214", "r": "280339889", "b": "5158121403", "aB": 18,
            "uB": "195071790410", "aUB": 696},
        {"d": "20240214", "r": "280339889", "b": "5158121403", "aB": 18,
            "uB": "195071790410", "aUB": 696}
    ]
    """
    data = []
    current_date = start_date
    for _ in range(num_days):
        obj = {
            'd': current_date.strftime('%Y%m%d'),
            'r': random.randint(1000, 10000),
            'b': random.randint(ONE_MB_IN_BYTES, TEN_GB_IN_BYTES),
            'aB': round(random.uniform(TEN_GB_IN_BYTES, TEN_GB_IN_BYTES), 2),
            'uB': random.randint(ONE_MB_IN_BYTES, TEN_GB_IN_BYTES),
            'aUB': round(random.uniform(TEN_GB_IN_BYTES, TEN_GB_IN_BYTES), 2)
        }
        data.append(obj)
        current_date -= timedelta(days=1)
    return data


def generate_data_gz(start_date, num_days):
    data = generate_data(start_date, num_days)
    data_str = json.dumps(data)
    compressor = GzipCompress()
    return compressor.compress_str(data_str)


def test_upload_fake_data():
    start_date = datetime.now()
    num_days = 365
    archive_gz = generate_data_gz(start_date, num_days)
    online_gz = generate_data_gz(start_date, num_days)
    now = datetime.utcnow().isoformat()
    item = {
        'serialNumber': {'S': sn},
        'lastUpdated': {'S': now},
        'archiveGzip': {'B': archive_gz},
        'onlineGzip': {'B': online_gz},
    }
    print('Update Clickhouse partition metrics')
    print(f'Payload size: {len(archive_gz) + len(online_gz)} bytes')
    db.upsert(item)
