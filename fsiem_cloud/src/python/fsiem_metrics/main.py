from argparse import ArgumentParser
from datetime import datetime
from fsiem_api_client.activation_table import ActivationTable
from fsiem_api_client.aws.dynamodb_simple_table import DynamoDbSimpleTable
from fsiem_api_client.aws.ssm_ops import SsmOps
from fsiem_api_client.const import worker_disk_sizes
from fsiem_api_client.deployment_metrics import DeploymentMetrics


def update_clickhouse_parts(sn: str, ssm_ops: SsmOps, db: DynamoDbSimpleTable):
    """Get partition metrics for online and archive storage using SSM. Save
    the compressed version into the metrics table of DynamoDB.

    Parameters
    ----------
    sn : str
        serial number
    ssm_ops : SsmOps
        Instance of SSM operation helper class
    db : DynamoDbSimpleTable
        DynamoDb table
    """
    archive_gz = ssm_ops.clickhouse_archive_parts_gz()
    online_gz = ssm_ops.clickhouse_online_parts_gz()
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
    print(f'Partition metric updated for: {sn}')


def update_clickhouse_sizes(sn: str, ssm_ops: SsmOps,
                            db: ActivationTable, s3_bucket: str,
                            s3_dir: str):
    """Update the sizes of live and archive clickhouse data in the activation
    table

    Parameters
    ----------
    sn : str
        The serial number of this deployment
    ssm_ops : SsmOps
        SSM operations
    db : ActivationTable
        A class to access the dynamodb activation table
    s3_bucket : str
        The s3 bucket used to store clickhouse archive data
    s3_dir : str
        The dir in the s3 archive bucket used by this deployment

    """
    print(f"Archive storage S3: {s3_bucket}/{s3_dir}")

    # We used to calculate this from S3, but it is slow and costly
    # from fsiem_api_client.aws.s3 import S3
    # ...
    # s3 = S3(region)
    # metrics = s3.s3_dir_metrics(s3_bucket, s3_dir)
    # archive = metrics.s3_archive_size_bytes

    # Get archive disk size by querying clickhouse
    archive = ssm_ops.clickhouse_archive_size()
    metrics = DeploymentMetrics(
        s3_archive_bucket=s3_bucket,
        s3_archive_dir=s3_dir,
        s3_archive_size_bytes=archive)
    db.update_usage_size(ActivationTable.archive_storage, sn, archive)
    print(f"Archive size: {archive} bytes")

    print("Online storage on workers")
    online = ssm_ops.get_workers_used_disk_space(worker_disk_sizes)
    db.update_usage_size(ActivationTable.online_storage, sn,
                         online.total_size)
    print(f"Online size: {online.total_size} bytes")

    metrics.online_size_bytes = online.total_size
    metrics.online_metrics_json_str = online.to_json_str()
    print(f'Saving deployment metrics: {metrics}')
    db.set_deployment_metrics(sn, metrics)


def main(sn: str, activation_tbl: str, metrics_storage_tbl: str,
         dynamodb_region: str, s3_bucket: str, s3_dir: str, region: str):
    """Generate metrics for clickhouse storage, the metrics being stored in the
    activation table

    Parameters
    ----------
    sn : str
        The serial number of this deployment
    activation_table : str
        The name of the activation dynamodb table
    metrics_storage_table : str
        The name of the metrics storage dynamodb table
    dynamodb_region : str
        The aws region the activation dynamodb table is located in
    s3_bucket : str
        The s3 bucket used to store clickhouse archive data
    s3_dir : str
        The dir in the s3 archive bucket used by this deployment
    region : str
        The region the deployment is located in
    """
    try:
        ssm_ops = SsmOps(region, sn)
        activation_tbl = ActivationTable(activation_tbl, dynamodb_region)
        metrics_tbl = DynamoDbSimpleTable(metrics_storage_tbl, dynamodb_region)

        current_status = activation_tbl.get_status(sn)
        if current_status != activation_tbl.complete:
            print(f'Do not run when status is `{current_status}`. Exiting.')
            return

        # Update clickhouse or EFS metrics
        print("Updating metrics for ClickHouse storage")
        update_clickhouse_sizes(sn, ssm_ops, activation_tbl, s3_bucket, s3_dir)
        print("Updated online and archive storage usage")

        # Update clickhouse partition sizes
        update_clickhouse_parts(sn, ssm_ops, metrics_tbl)

    except Exception as e:
        print(f'Failed to get and save metrics: {e}')


def parse_args() -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Captures metrics for FortiSIEM deployment')
    parser = ArgumentParser(description=description)
    parser.add_argument('--serial_number', type=str, required=True,
                        help='The serial number of this deployment')
    parser.add_argument('--dynamodb_activation_table', type=str, required=True,
                        help='The name of the activation dynamodb table')
    parser.add_argument('--dynamodb_metrics_storage_table', type=str,
                        required=True,
                        help='The name of the metrics storage dynamodb table')
    parser.add_argument('--dynamodb_region', type=str, required=True,
                        help='The region of the dynamodb table')
    parser.add_argument('--s3_bucket', type=str, required=True,
                        help='AWS S3 bucket name for ClickHouse archive')
    parser.add_argument('--s3_dir', type=str, required=True,
                        help='AWS S3 dir for ClickHouse archive in bucket')
    parser.add_argument('--region', type=str, required=True,
                        help='Deployment region')

    return parser.parse_args()


if __name__ == '__main__':
    # Usage:  python3 -u main.py --serial_number ${SERIAL_NUMBER} \
    # --dynamodb_activation_table ${DYNAMODB_ACTIVATION_TABLE} \
    # --dynamodb_metrics_storage_table ${DYNAMODB_METRICS_STORAGE_TABLE} \
    # --dynamodb_region ${DYNAMODB_REGION}
    # --s3_bucket ${S3_BUCKET} \
    # --s3_dir ${S3_DIR} \
    # --region ${REGION} \

    config = parse_args()
    main(config.serial_number, config.dynamodb_activation_table,
         config.dynamodb_metrics_storage_table, config.dynamodb_region,
         config.s3_bucket, config.s3_dir, config.region)
