from fsiem_api_client.aws.ssm_ops import SsmOps
from fsiem_api_client.aws.dynamodb_simple_table import DynamoDbSimpleTable
from main import main, update_clickhouse_parts


def test_update_clickhouse_parts():
    sn = 'FSMCLD0000000181'
    region = 'us-east-1'
    ssm_ops = SsmOps(region, sn)
    db = DynamoDbSimpleTable('fsiem_metrics_storage_playground', region)
    update_clickhouse_parts(sn, ssm_ops, db)


def test_main_backup():
    main(sn='FSMCLD0000000181',
         activation_tbl='fsiem_activation_table_playground',
         metrics_storage_tbl='fsiem_metrics_storage_playground',
         dynamodb_region='us-east-1',
         s3_bucket='fsiem-clickhouse-data-us-east-1-playground',
         s3_dir='FSMCLD0000000181',
         region='us-east-1')
