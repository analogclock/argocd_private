from enum import Enum
import json
from packaging import version
from requests import Response
from uuid import UUID
from fsiem_api_client.clickhouse_config import ClickHouseConfig
from fsiem_api_client.http_call import HttpCall


class H5_ACTION_TYPE(Enum):
    TEST = 'test'
    ADD = 'add'
    REMOVE = 'remove'


class H5Service:

    path_test_clickhouse_cfg = '/phoenix/rest/h5/sys/config/clickhouse/test'
    path_update_clickhouse_cfg = '/phoenix/rest/h5/sys/config/clickhouse/update'  # noqa
    path_test_storage = '/phoenix/rest/h5/sys/config/storage/test'
    path_update_storage = '/phoenix/rest/h5/sys/config/storage/update'
    path_update_org_bucket_mapping = '/phoenix/rest/h5/sys/config/storage/orgBucketMapping/update'  # noqa
    path_test_archive = '/phoenix/rest/h5/sys/config/archive/test'
    path_update_archive = '/phoenix/rest/h5/sys/config/archive/update'
    path_license_status = '/phoenix/rest/h5/sec/license'
    path_add_worker = '/phoenix/rest/h5/server/worker/op'
    path_check_storage = '/phoenix/rest/h5/sys/configs/find'
    path_get_version = '/phoenix/rest/h5/sys/version'
    path_get_uuid = '/phoenix/rest/h5/sec/uuid'
    path_upload_license = '/phoenix/uploadLicense'

    def __init__(self, http: HttpCall, super_url: str):
        if not http:
            raise ValueError('http cannot be None.')
        if not super_url:
            raise ValueError('super url cannot be None.')
        self.http = http
        self.super_url = super_url

    def update_org_bucket_mapping(self) -> Response:
        """Execute a call to update org bucket mapping"""
        url = f'{self.super_url}{self.path_update_org_bucket_mapping}'
        data = []
        return self.http.retry_post(url, data=data, ok_text='"OK"',
                                    verbose=False)

    def clickhouse_check_storage(self) -> bool:
        """Check if ClickHouse storage was configured"""
        url = f'{self.super_url}{self.path_check_storage}'
        params = {'category': 'Storage', 'perUser': 'false'}
        r = self.http.retry_get(url, params=params)
        try:
            r_json = json.loads(r.text)
            for entry in r_json:
                if entry.get('value') == 'clickhouse':
                    return True
            return False
        except Exception:
            return False

    def clickhouse_super(self, hot: list, warm: list, pwd: str,
                         email: str, action: H5_ACTION_TYPE) -> Response:
        """Test or save ClickHouse storage on super

        Parameters
        ----------
        hot: list
            List of hot disks
        warm: list
            List of warm disks
        pwd: str
            Admin password
        email: str
            admin email
        action: H5_ACTION_TYPE
            Type of API call: TEST or ADD
        """
        if not hot:
            raise ValueError('hot disks are None')
        if not email:
            raise ValueError('admin email is None')

        url = 'unset_value'
        if action == H5_ACTION_TYPE.TEST:
            url = f'{self.super_url}{self.path_test_storage}'
        elif action == H5_ACTION_TYPE.ADD:
            url = f'{self.super_url}{self.path_update_storage}'

        cfg = ClickHouseConfig()
        ch_cfg = json.dumps(cfg.disk_config(hot, warm))
        json_request = [
            {'left': 'storage_type', 'right': 'clickhouse'},
            {'left': 'clickhouse_config', 'right': ch_cfg},
            {'left': 'init_admin_pwd', 'right': pwd},
            {'left': 'init_admin_email', 'right': email},
        ]

        # posting a password, don't print data
        return self.http.retry_post(url, json=json_request, verbose=False,
                                    ok_text=['"OK"', 'Succeed', 'InProgress',
                                             'Start'])

    def clickhouse_worker(self, hot: list, warm: list, dns: str, ip: str,
                          s3_bucket: str, s3_region: str,
                          action: H5_ACTION_TYPE) -> Response:
        """Test or save ClickHouse storage on workers

        Parameters
        ----------
        hot: list
            List of hot disks
        warm: list
            List of warm disks
        dns:
            DNS of the worker
        ip: str
            IP of the worker
        s3_bucket: str
            Bucket name (with additional path) where to store archive data
        s3_region: str
            S3 bucket region
        action: H5_ACTION_TYPE
            Type of API call: TEST or ADD
        """
        url = f'{self.super_url}{self.path_add_worker}'
        cfg = ClickHouseConfig()
        ch_cfg = cfg.disk_config(hot, warm)
        bucket_cfg = json.dumps({'bucket': s3_bucket, 'region': s3_region})
        json_req = {
            'active': False, 'custId': None, 'grpNid': None, 'ipAddr': ip,
            'mode': None, 'rsExpiration': 0, 'rsLicensed': False, 'id': 949502,
            'hostName': dns, 'runningOn': 'VM', 'storageConfig': ch_cfg,
            'bucket': bucket_cfg, 'usingAwsToArchive': True
        }
        op = 'unset_value'
        if action == H5_ACTION_TYPE.TEST:
            op = H5_ACTION_TYPE.TEST.value
            ok_text = '"SUCCESS"'
        elif action == H5_ACTION_TYPE.ADD:
            op = H5_ACTION_TYPE.ADD.value
            ok_text = '"SUCCESS"'
        elif action == H5_ACTION_TYPE.REMOVE:
            op = H5_ACTION_TYPE.REMOVE.value
            ok_text = '"VA removed successfully"'
        params = {'operation': op}
        return self.http.retry_post(
            url, params=params, json=json_req, ok_text=ok_text)

    def clickhouse_config(self, supers: list, keepers: list, workers: list,
                          s3_bucket: str, s3_region: str,
                          action: H5_ACTION_TYPE) -> Response:
        """Test or save ClickHouse config

        Parameters
        ----------
        supers: list
            List of supers info - optional
        keepers: list
            List of keepers info
        workers: list
            List of workers info
        s3_bucket: str
            Bucket name (with additional path) where to store archive data
        s3_region: str
            S3 bucket region
        action: H5_ACTION_TYPE
            Type of API call: TEST or ADD
        """
        if not keepers:
            raise ValueError('keepers are None')
        if not workers:
            raise ValueError('workers are None')

        url = 'unset_value'
        if action == H5_ACTION_TYPE.TEST:
            url = f'{self.super_url}{self.path_test_clickhouse_cfg}'
        elif action == H5_ACTION_TYPE.ADD:
            url = f'{self.super_url}{self.path_update_clickhouse_cfg}'

        cfg = ClickHouseConfig()
        shards = cfg.shards_config(supers, workers, s3_bucket, s3_region)
        all_keepers = cfg.zookeeper_config(keepers)
        json_req = {
            'engine': 'replicated_merge_tree',
            'clickhouse_cluster': {'shards': shards},
            'zookeeper_cluster': all_keepers
        }
        return self.http.retry_post(
            url, json=json_req, ok_text=['Succeed', 'InProgress', 'Start'])

    def clickhouse_s3_archive(self, s3_bucket: str, s3_region: str,
                              action: H5_ACTION_TYPE) -> Response:
        """Test or save archive storage backed by S3 for ClickHouse

        Parameters
        ----------
        s3_bucket: str
            Bucket name (with additional path) where to store archive data
        s3_region: str
            S3 bucket region
        action: H5_ACTION_TYPE
            Type of API call: TEST or ADD
        """
        url = 'unset_value'
        op = 'unset_value'
        if action == H5_ACTION_TYPE.TEST:
            url = f'{self.super_url}{self.path_test_archive}'
            op = 'test'
        elif action == H5_ACTION_TYPE.ADD:
            url = f'{self.super_url}{self.path_update_archive}'
            op = 'save'
        json = [
            {'left': 'archive_storage_type', 'right': 'clickhouse_s3'},
            {'left': 'use_environment_variables', 'right': True},
            {'left': 'buckets',
                'right': [{'bucket': s3_bucket, 'region': s3_region}]},
            {'left': 'mode', 'right': op}
        ]
        return self.http.retry_post(url, json=json, ok_text='"OK"')

    def check_old_workers(self, workers: list) -> list[str]:
        """Check specified workers to add against the existing worker nodes
        to avoid adding existing nodes, which results in an error.

        Parameters
        ----------
        workers : list
            The IP addresses of the worker nodes to add

        Returns
        -------
        list
            The IP addresses of worker nodes to add that aren't already added
        """
        print('Checking if workers were already added')
        url = f'{self.super_url}{self.path_license_status}'
        r = self.http.retry_get(url, verbose=False)
        r_json = json.loads(r.text)
        existing_ips = []
        for node in r_json['workerList']:
            existing_ips.append(node['ipAddr'])

        new_workers = []
        for worker in workers:
            if worker in existing_ips:
                print(f'- Already added as worker: {worker}')
            else:
                new_workers.append(worker)
        return new_workers

    def add_worker(self, worker: str) -> Response:
        """Add a new worker

        Parameters
        ----------
        worker : str
            The ipv4 address of the worker to add
        """
        url = f'{self.super_url}{self.path_add_worker}'
        params = {'operation': 'add'}
        json = {
            'active': False, 'custId': None, 'grpNid': None,
            'ipAddr': worker, 'mode': None, 'rsExpiration': 0,
            'rsLicensed': False, 'hostName': ''
        }
        expected_responses = ['"Worker added successfully"', '"SUCCESS"']
        return self.http.retry_post(
            url, params=params, json=json, ok_text=expected_responses)

    def get_version(self) -> str:
        """Gets the current version of the FortiSiem cluster

        Returns
        -------
        str
            The FortiSiem version number
        """
        url = f'{self.super_url}{self.path_get_version}'
        r = self.http.retry_get(url)
        fsiem_version = r.text.strip('"')
        if not isinstance(version.parse(fsiem_version), version.Version):
            raise ValueError(f'Unexpected response: {fsiem_version}')
        return fsiem_version

    def get_uuid(self) -> str:
        """Queries the supers API to get the UUID

        Returns
        -------
        str
            The UUID of the super
        """
        url = f'{self.super_url}{self.path_get_uuid}'
        r = self.http.retry_get(url)
        # Trim the returned string down to just the UUID
        uuid = r.text
        trim_strings = ['\"', '\t', '\\t', 'UUID:', ' ']
        for trimming in trim_strings:
            uuid = uuid.replace(trimming, '')

        # Use uuid module to check returned string is actually a valid UUID
        UUID(uuid, version=4)
        return uuid

    def upload_license(self, license_type: str, license_data: bytes,
                       license_name: str, default_password: str) -> Response:
        """Upload the license file to the fsiem super

        Parameters
        ----------
        license_type: str
            The license type. Either va for enterprise or sp for service
            provider
        license_data : bytes
            The license itself
        license_name : str
            The name of the license file
        default_password: str
            The default password for the default admin account
        """
        url = f'{self.super_url}{self.path_upload_license}'
        params = {'mode': license_type}
        files = {
            'uploadFile': (
                license_name,
                license_data
            ),
            'filePathInput': (None, 'license'),
            'username': (None, 'admin'),
            'password': (None, default_password),
            'modeBox': (None, license_type)
        }
        print('Using username and password to submit license data')
        r = self.http.post(url, params=params, files=files, verbose=False)
        r.raise_for_status()
        success = 'You have successfully registered your virtual appliance'
        if success not in r.text:
            raise ValueError(f'Unexpected response: {r.text}')
        print('License info submitted OK')
        return r

    def upload_license_jwt(self, license_type: str,
                           license_data: bytes,
                           license_name: str) -> Response:
        """Upload the license file to the fsiem super using JWT auth

        Parameters
        ----------
        license_type: str
            The license type. Either va for enterprise or sp for service
            provider
        license_data : bytes
            The license itself
        license_name : str
            The name of the license file
        """
        url = f'{self.super_url}{self.path_upload_license}'
        params = {'mode': license_type}
        files = {
            'uploadFile': (
                license_name,
                license_data
            ),
            'filePathInput': (None, 'license'),
            'modeBox': (None, license_type)
        }
        print('Using JWT authentication to submit license data')
        r = self.http.post(url, params=params, files=files, verbose=False)
        r.raise_for_status()
        success = 'You have successfully registered your virtual appliance'
        if success not in r.text:
            raise ValueError(f'Unexpected response: {r.text}')
        print('License info submitted OK')
        return r
