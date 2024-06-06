from time import sleep
from fsiem_api_client.services.h5_service import H5_ACTION_TYPE
from net_ops import check_if_ip, resolve_dns_to_ipv4
from fsiem_api_client.const import FsiemInstanceRole, phmonitor_delay_sec, \
    ch_propagate_delay
from fsiem_api_client.aws.ssm_ops import SsmOps
from fsiem_api_client.fsiem_api import FsiemApi
from fsiem_api_client.activation_table import ActivationTable
from fsiem_api_client.services.worker_service import WORKER_TYPE


ROLE_SUPER = FsiemInstanceRole.super.name
ROLE_WORKER = FsiemInstanceRole.worker.name
ROLE_KEEPER = FsiemInstanceRole.keeper.name
ROLE_INGESTION = FsiemInstanceRole.ingestion.name


def wait_for_app_restart():
    """Sleeping for some time to let the server restart

    Some operations result in a server restart, and if we don't wait for it,
    we will get low level HTTP server errors.
    """
    print('Waiting for phMonitor to restart...')
    sleep(phmonitor_delay_sec)


def set_deployment_type_to_cloud(fsiem: FsiemApi):
    """Call FortiSiem API and set its deployment type to `cloud`.
       This will automatically hide some UI in FortiSiem VM.

    Parameters
    ----------
    fsiem : FsiemApi
        The Fsiem API client
    """
    print('Setting FortiSiem VM deployment type to `cloud`')
    resp = fsiem.config.set_deployment_type_cloud()
    print(f'Deployment type set to cloud, resp code: `{resp.status_code}`')


def set_version_db(fsiem: FsiemApi, db: ActivationTable, serial_no: str):
    """Retrieve the FSIEM version and set it in the activation table

    Parameters
    ----------
    fsiem : FsiemApi
        The Fsiem API client
    db : ActivationTable
        The ActivationTable class
    serial_no : str
        The serial number of the deployment
    """
    version = fsiem.h5.get_version()
    db.update_version(serial_no, version)


def clickhouse_super_setup(fsiem: FsiemApi, disk_sizes: list, region: str,
                           serial_no: str, new_pwd: str, email: str) -> None:
    """Configure setup on super and workers

    Parameters
    ----------
    fsiem: FsiemApi
        The Fsiem API client
    disk_sizes : list
        A list of disk with known sizes ['25GB', '60GB']
    region: str
        Deployment region
    serial_no : str
        The serial number of the deployment
    new_pwd: str
        User password for new deployment
    email: str
        Admin email
    """
    if fsiem.h5.clickhouse_check_storage():
        print('ClickHouse already configured')
        return

    ssm = SsmOps(region, serial_no)
    supers_info = ssm.get_instance_info(ROLE_SUPER, disk_sizes)

    print(f'==> Setup of {len(supers_info)} super(s)')
    for super_info in supers_info:
        id = super_info['InstanceId']
        dns = super_info['PrivateDnsName']
        ip = super_info['PrivateIpAddress']
        disks = super_info['ClickHouseDiskPaths']
        print(f'Instance id: {id}, dns: {dns}, ip: {ip}, disks: {disks}')
        print('Super test')
        fsiem.h5.clickhouse_super(
            disks, None, new_pwd, email, H5_ACTION_TYPE.TEST)
        print('Super save')
        fsiem.h5.clickhouse_super(
            disks, None, new_pwd, email, H5_ACTION_TYPE.ADD)

        wait_for_app_restart()

        print('Update org bucket mapping')
        fsiem.h5.update_org_bucket_mapping()


def clickhouse_get_new_workers(fsiem: FsiemApi, worker_disk_sizes: list[str],
                               worker_ips: list[str]) -> list[str]:
    """Generate a list of IP addresses for _new_ workers. This will return
       an empty list if all workers are old (so already been added before)"""
    worker_ipv4s = []
    if worker_ips:
        worker_ipv4s, worker_dns = check_if_ip(worker_ips)
        worker_ipv4s.extend(resolve_dns_to_ipv4(worker_dns))
    return fsiem.h5.check_old_workers(worker_ipv4s) if worker_ipv4s else []


def clickhouse_has_new_workers(fsiem: FsiemApi,  worker_disk_sizes: list[str],
                               worker_ips: list[str]) -> bool:
    """Returns True if there is any new worker, otherwise False."""
    return len(clickhouse_get_new_workers(
        fsiem, worker_disk_sizes, worker_ips)) > 0


def clickhouse_worker_setup(fsiem: FsiemApi, worker_disk_sizes: list,
                            keeper_disk_sizes: list, region: str,
                            serial_no: str, worker_ips: list,
                            s3_bucket: str,
                            s3_region: str) -> None:
    """Configure ClickHouse on workers

    Parameters
    ----------
    fsiem: FsiemApi
        The Fsiem API client
    worker_disk_sizes: list
        A list of disk with known sizes ['25GB', '60GB']
    keeper_disk_sizes: list
        A list of disk with known sizes ['25GB', '60GB']
    region: str
        Deployment region
    serial_no : str
        The serial number of the deployment
    worker_ips : list
        The local IP addresses of the worker nodes
    s3_bucket: str
        Bucket name (with additional path) where to store archive data
    s3_region: str
        S3 bucket region
    """
    new_workers = clickhouse_get_new_workers(
        fsiem, worker_disk_sizes, worker_ips)

    ssm = SsmOps(region, serial_no)
    workers_info = ssm.get_instance_info(ROLE_WORKER, worker_disk_sizes)
    keepers_info = ssm.get_instance_info(ROLE_KEEPER, keeper_disk_sizes)
    ingestion_info = ssm.get_instance_info(ROLE_INGESTION, worker_disk_sizes)
    print('==> Combined setup of workers and keepers')
    print(f'Number of workers: {len(workers_info)}')
    print(f'Number of keepers: {len(keepers_info)}')
    print(f'Number of ingestion_workers: {len(ingestion_info)}')

    # extend workers with any keepers we have
    workers_info.extend(keepers_info)
    workers_info.extend(ingestion_info)
    for i, worker_info in enumerate(workers_info):
        id = worker_info['InstanceId']
        dns = worker_info['PrivateDnsName']
        ip = worker_info['PrivateIpAddress']
        disks = worker_info['ClickHouseDiskPaths']

        if ip not in new_workers:
            print(f'Skipping {ip} as it was already configured')
            continue

        print(f'{i}.  Id: {id}, dns: {dns}, ip: {ip}, disks: {disks}')
        print('Worker test')
        fsiem.h5.clickhouse_worker(
            disks, None, dns, ip, s3_bucket, s3_region, H5_ACTION_TYPE.TEST)
        print('Worker save')
        fsiem.h5.clickhouse_worker(
            disks, None, dns, ip, s3_bucket, s3_region, H5_ACTION_TYPE.ADD)
        print('Update org bucket mapping')
        fsiem.h5.update_org_bucket_mapping()


def clickhouse_config(fsiem: FsiemApi, super_disk_sizes: list,
                      worker_disk_sizes: list, keeper_disk_sizes: list,
                      region: str, serial_no: str, s3_bucket: str,
                      s3_region: str) -> None:
    """Configure ClickHouse

    Parameters
    ----------
    fsiem: FsiemApi
        The Fsiem API client
    super_disk_sizes : list
        A list of disk with known sizes ['25GB', '60GB']
    worker_disk_sizes : list
        A list of disk with known sizes ['25GB', '60GB']
    keeper_disk_sizes : list
        A list of disk with known sizes ['25GB', '60GB']
    region: str
        Deployment region
    serial_no : str
        The serial number of the deployment
    """
    print('==> Configuring cluster')
    ssm = SsmOps(region, serial_no)
    supers_info = ssm.get_instance_info(ROLE_SUPER, super_disk_sizes)
    workers_info = ssm.get_instance_info(ROLE_WORKER, worker_disk_sizes)
    keepers_info = ssm.get_instance_info(ROLE_KEEPER, keeper_disk_sizes)

    # add everything we have to the all_keepers
    all_keepers = supers_info + keepers_info

    print('Step 1. Cluster config test and save (super in cluster)')
    fsiem.h5.clickhouse_config(
        supers_info, all_keepers, workers_info,
        s3_bucket, s3_region, H5_ACTION_TYPE.TEST)
    fsiem.h5.clickhouse_config(
        supers_info, all_keepers, workers_info,
        s3_bucket, s3_region, H5_ACTION_TYPE.ADD)
    # NB: server usually returns HTTP 200 OK
    #     {"progress":0,"status":"InProgress","payload":950056}
    # We need to wait until this is done, but there isn't API available to get
    # a job status. We can read it's status in redis or app server db.
    # For now, to keep things easy, we will just sleep.
    print('Allowing ClickHouse to propagate changes')
    sleep(ch_propagate_delay)

    print('Step 2. Cluster config test and save (remove super from cluster)')
    fsiem.h5.clickhouse_config(
        None, all_keepers, workers_info,
        s3_bucket, s3_region, H5_ACTION_TYPE.TEST)
    fsiem.h5.clickhouse_config(
        None, all_keepers, workers_info,
        s3_bucket, s3_region, H5_ACTION_TYPE.ADD)

    print('Allowing ClickHouse to propagate changes')
    sleep(ch_propagate_delay)


def clickhouse_archive_setup(fsiem: FsiemApi, s3_bucket: str, s3_region: str):
    """Setup archive storage with ClickHouse

    Parameters
    ----------
    s3_bucket: str
        Bucket name (with additional path) where to store archive data
    s3_region: str
        S3 bucket region
    """
    print(f'Setting up archive storage for: {s3_bucket} in {s3_region}')
    fsiem.h5.clickhouse_s3_archive(s3_bucket, s3_region, H5_ACTION_TYPE.TEST)
    fsiem.h5.clickhouse_s3_archive(s3_bucket, s3_region, H5_ACTION_TYPE.ADD)


def event_query_worker_setup(fsiem: FsiemApi, worker_url: str,
                             type: WORKER_TYPE):
    """Setup the event or query workers setting with the worker load balancer
    URL

    Parameters
    ----------
    fsiem : FsiemApi
        The Fsiem API client
    worker_url : str
        The worker load balancer URL to add
    setting : str
        The worker setting to get, event or query
    """
    print(f'Checking existing settings for `{type}` workers')
    workers = fsiem.worker.get(type)
    if workers == [worker_url]:
        print(f'URLs for `{type}` workers already added, skipping')
        return
    elif workers:
        print(f'Current addresses `{workers}` do not match `{type}` types, '
              'will delete all existing addresses and add new')
        fsiem.worker.delete(workers, type)
    else:
        print(f'No workers `{type}` workers set, will add them')
    print(f'Adding `{worker_url}` to `{type}` worker types')
    fsiem.worker.add(worker_url, type)


def app_server_mem_setup(region: str, serial_no: str, app_server_mem_gb: int):
    """Update the JVM memory setting for the App Server

    Parameters
    ----------
    region : str
        The region the cluster was deployed in
    serial_no : str
        The serial number of the cluster
    app_server_mem_gb : int
        The amount of memory, in GB, to assign to the App Server in the JVM
        settings
    """
    new_memory = f'{app_server_mem_gb * 1024}m'
    filename = '/opt/glassfish/domains/domain1/config/domain.xml'
    print(f'New: {new_memory}')
    ssm = SsmOps(region, serial_no)
    response = ssm.get_app_server_memory(filename)

    for instance, output in response.items():
        # remove surrounding characters
        memory = output.strip()
        memory = memory.removeprefix('<jvm-options>-Xms')
        memory = memory.removesuffix('</jvm-options>')
        print(f'{instance} memory: {memory}')

        if memory == new_memory:
            print(f'Current memory settings for {instance} are correct, '
                  'no need to update')
            continue
        print(f'Current memory settings for {instance} are not correct, '
              'updating')
        ssm.update_app_server_memory(
            [instance], memory, new_memory, filename
        )
        print(f'Stopping App Server on {instance}')
        ssm.stop_app_server([instance])
