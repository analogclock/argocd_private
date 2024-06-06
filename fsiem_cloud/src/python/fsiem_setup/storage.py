from fsiem_api_client.aws.ssm_ops import SsmOps


def expand_fs_worker_disks(region: str, serial_no: str):
    """Attempt to expand file system of worker ClickHouse disks.

    If the disk has increased since last run, file system will expand to cover
    all available storage. If disk hasn't increased, this operation does
    nothing and returns a success code.

    Parameters
    ----------
    region : str
        The deployment region
    serial_no : str
        The serial number of deployment
    """
    ssm = SsmOps(region, serial_no)
    ssm.expand_workers_clickhouse_fs()
    print('File system expanded (if needed) successfully')
