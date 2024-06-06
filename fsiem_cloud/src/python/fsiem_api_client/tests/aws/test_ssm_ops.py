import pytest
from fsiem_api_client.aws.ssm_ops import DfResponse, SsmOps
from fsiem_api_client.backup_options_table import BackupOptions
from fsiem_api_client.const import BackupType


class TestSsmOps:

    region = 'eu-west-1'
    sn = 'FSMCLD0000000181'
    uut = SsmOps(region=region, sn=sn)

    def test_parse_lsblk_response(self):
        # Got this from running lsblk on 6.6 super
        lsblk_output = '''{\n   "blockdevices": [\n      {"name": "/dev/nvme0n1", "size": "25G",\n         "children": [\n            {"name": "/dev/nvme0n1p1", "size": "1G"},\n            {"name": "/dev/nvme0n1p2", "size": "24G",\n               "children": [\n                  {"name": "/dev/mapper/rl-swap", "size": "2.5G"},\n                  {"name": "/dev/mapper/rl-root", "size": "21.5G"}\n               ]\n            }\n         ]\n      },\n      {"name": "/dev/nvme1n1", "size": "60G",\n         "children": [\n            {"name": "/dev/nvme1n1p1", "size": "60G"}\n         ]\n      },\n      {"name": "/dev/nvme2n1", "size": "100G",\n         "children": [\n            {"name": "/dev/nvme2n1p1", "size": "22.4G"},\n            {"name": "/dev/nvme2n1p2", "size": "68.9G"}\n         ]\n      },\n      {"name": "/dev/nvme3n1", "size": "60G",\n         "children": [\n            {"name": "/dev/nvme3n1p1", "size": "60G"}\n         ]\n      }\n   ]\n}\n''' # noqa
        disk_size = '60G'
        actual = self.uut._parse_lsblk_response(lsblk_output, disk_size)
        assert len(actual) == 2

    def test_parse_lsblk_response_except(self):
        # Got this from running lsblk on 6.6 super
        lsblk_output = '''{\n   "blockdevices": [\n      {"name": "/dev/nvme0n1", "size": "25G",\n         "children": [\n            {"name": "/dev/nvme0n1p1", "size": "1G"},\n            {"name": "/dev/nvme0n1p2", "size": "24G",\n               "children": [\n                  {"name": "/dev/mapper/rl-swap", "size": "2.5G"},\n                  {"name": "/dev/mapper/rl-root", "size": "21.5G"}\n               ]\n            }\n         ]\n      },\n      {"name": "/dev/nvme1n1", "size": "60G",\n         "children": [\n            {"name": "/dev/nvme1n1p1", "size": "60G"}\n         ]\n      },\n      {"name": "/dev/nvme2n1", "size": "100G",\n         "children": [\n            {"name": "/dev/nvme2n1p1", "size": "22.4G"},\n            {"name": "/dev/nvme2n1p2", "size": "68.9G"}\n         ]\n      },\n      {"name": "/dev/nvme3n1", "size": "60G",\n         "children": [\n            {"name": "/dev/nvme3n1p1", "size": "60G"}\n         ]\n      }\n   ]\n}\n''' # noqa
        disk_sizes = ['60G', '25G']
        actual = self.uut._parse_lsblk_response_except(
            lsblk_output, disk_sizes)
        assert len(actual) == 1

    def test__parse_df_resp(self):
        # Got this from running df on worker
        output = 'Filesystem          1073741824-blocks  Used Available Capacity Mounted on\ndevtmpfs                           8G    0G        8G       0% /dev\ntmpfs                              8G    0G        8G       0% /dev/shm\ntmpfs                              8G    1G        8G       1% /run\ntmpfs                              8G    0G        8G       0% /sys/fs/cgroup\n/dev/mapper/rl-root               22G   15G        8G      67% /\n/dev/nvme1n1p2                    69G    5G       65G       7% /opt\n/dev/nvme0n1p1                     1G    1G        1G      69% /boot\ntmpfs                              2G    0G        2G       0% /run/user/500\n/dev/nvme2n1                     500G    5G      496G       1% /data-clickhouse-hot-1\n'  # noqa
        uut = SsmOps('us-east-1', 'sn')
        actual = uut._parse_df_resp(output, size_unit='G')
        assert len(actual) == 9

    def test_to_json_str(self):
        # Got this from running df on worker
        output = 'Filesystem          1073741824-blocks  Used Available Capacity Mounted on\ndevtmpfs                           8G    0G        8G       0% /dev\ntmpfs                              8G    0G        8G       0% /dev/shm\ntmpfs                              8G    1G        8G       1% /run\ntmpfs                              8G    0G        8G       0% /sys/fs/cgroup\n/dev/mapper/rl-root               22G   15G        8G      67% /\n/dev/nvme1n1p2                    69G    5G       65G       7% /opt\n/dev/nvme0n1p1                     1G    1G        1G      69% /boot\ntmpfs                              2G    0G        2G       0% /run/user/500\n/dev/nvme2n1                     500G    5G      496G       1% /data-clickhouse-hot-1\n'  # noqa
        uut = SsmOps('us-east-1', 'sn')
        items = uut._parse_df_resp(output, size_unit='G')
        resp = DfResponse(total_size=111, size_unit='G', items=items)
        j = resp.to_json_str()
        assert j

    def test_get_app_server_memory_cmd_injection(self):
        cmd = '/opt/glassfish/domains/domain1/config/domain.xml; touch /tmp/x1'
        with pytest.raises(ValueError):
            self.uut.get_app_server_memory(cmd)

    def test_update_app_server_memory_cmd_injection(self):
        cmd = '/opt/glassfish/domains/domain1/config/domain.xml; touch /tmp/x1'
        with pytest.raises(ValueError):
            self.uut.update_app_server_memory(
                ['foo'], 'touch /tmp/om1', '10240m', cmd)
        with pytest.raises(ValueError):
            self.uut.update_app_server_memory(
                ['foo'], '5120m', 'touch /tmp/om1', cmd)
        with pytest.raises(ValueError):
            self.uut.update_app_server_memory(
                ['foo'], '5120m', '10240m', cmd)

    def test_stop_app_server_id_none(self):
        with pytest.raises(ValueError):
            self.uut.stop_app_server(None)

    def test_find_disks_workers(self):
        with pytest.raises(ValueError):
            self.uut.find_disks_workers(['touch /tmp/om1'])

    def test_get_instance_info_cmd_injection(self):
        with pytest.raises(ValueError):
            self.uut.get_instance_info('super1', ['25g'])
        with pytest.raises(ValueError):
            self.uut.get_instance_info('super', ['test bar'])

    def test_find_disks_supers_cmd_injection(self):
        with pytest.raises(ValueError):
            self.uut.find_disks_supers(['test bar'])

    def test_find_disks_workers_cmd_injection(self):
        with pytest.raises(ValueError):
            self.uut.find_disks_workers(['test bar'])

    def test_get_workers_used_disk_space(self):
        with pytest.raises(ValueError):
            self.uut.get_workers_used_disk_space(['test bar'])

    def test_worker_instance_id_by_dns(self):
        with pytest.raises(ValueError):
            self.uut.worker_instance_id_by_dns(None)
        with pytest.raises(ValueError):
            self.uut.worker_instance_id_by_dns('')

    def test_clickhouse_copy_to_external_storage(self):
        c = 123
        d = 'fsiem-s3-test-bucket-185'
        p = ['(18250,20230902)']
        f = 'external_storage_file_test'
        fmt = 'Parquet'

        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, None, p, f, fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, '', p, f, fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, None, f, fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, [], f, fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, p, None, fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, p, '', fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, p, f, None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, p, f, '')

        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, "b; foo", p, f,
                                                         fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, "b; foo", f,
                                                         fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, p, "b; foo",
                                                         fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, p, f, "b; foo")

        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, "b && foo", p, f,
                                                         fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, "b && foo", f,
                                                         fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, p, "b && foo",
                                                         fmt)
        with pytest.raises(ValueError):
            self.uut.clickhouse_copy_to_external_storage(c, d, p, f,
                                                         "b && foo")

    def test_clickhouse_delete_partitions(self):
        p = ['(18250,20230902)']

        with pytest.raises(ValueError):
            self.uut.clickhouse_delete_partitions(None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_delete_partitions([])
        with pytest.raises(ValueError):
            self.uut.clickhouse_delete_partitions(['b && foo'])
        with pytest.raises(ValueError):
            self.uut.clickhouse_delete_partitions(['b ; foo'])
        with pytest.raises(ValueError):
            self.uut.clickhouse_delete_partitions(p, None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_delete_partitions(p, '')
        with pytest.raises(ValueError):
            self.uut.clickhouse_delete_partitions(p, 'foo', None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_delete_partitions(p, 'foo', '')

    def test_clickhouse_backup_create(self):
        n = "name"
        t = BackupType.FULL
        p = "previous-backup"
        o = {
            'remote_storage': 's3',
            'log_level': 'warn',
            'region': 'us-east-1',
            's3_bucket': 'fsiem-clickhouse-backups-us-east-1-dev',
            's3_path': '111',
            's3_compression_level': '1',
            's3_compression_format': 'tar',
            's3_use_custom_storage_class': 'false',
            's3_storage_class': 'STANDARD',
            's3_concurrency': '1',
            's3_debug': 'false',
        }
        backup_options_str = """[{"S3_COMPRESSION_LEVEL": "6"}, {"S3_COMPRESSION_FORMAT": "bzip2"}, {"S3_USE_CUSTOM_STORAGE_CLASS": "false"}]"""  # noqa
        parser = BackupOptions()
        ov = parser.from_str(backup_options_str)

        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_create(None, t, p, o, ov)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_create('', t, p, o, ov)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_create(';', t, p, o, ov)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_create(n, t, '|', o, ov)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_create(n, t, p, None, ov)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_create(n, t, p, [], ov)

    def test_clickhouse_backup_restore(self):
        n = "name"
        o = {
            'remote_storage': 's3',
            'log_level': 'warn',
        }
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_restore(None, o)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_restore('', o)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_restore(';', o)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_restore(n, None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_restore(n, {})
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_restore(n, {';': 'foo'})

    def test_clickhouse_backup_delete(self):
        n = "name"
        loc = "location"
        o = {'remote_storage': 's3'}
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_delete(None, loc, o)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_delete('', loc, o)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_delete(';', loc, o)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_delete(n, None, o)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_delete(n, '', o)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_delete(n, "&&", o)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_delete(n, loc, None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_delete(n, loc, {})
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_delete(n, loc, {"&&": "foo"})

    def test_clickhouse_backup_list(self):
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_list(None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_list({})
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_list({"&&": "foo"})

    def test_clickhouse_backup_cleanup(self):
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_cleanup(None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_cleanup({})
        with pytest.raises(ValueError):
            self.uut.clickhouse_backup_cleanup({"&&": "foo"})

    def test_clickhouse_metrics(self):
        with pytest.raises(ValueError):
            self.uut.clickhouse_metrics(None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_metrics('')
        with pytest.raises(ValueError):
            self.uut.clickhouse_metrics("&&")

    def test_clickhouse_query_duration(self):
        with pytest.raises(ValueError):
            self.uut.clickhouse_query_duration(None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_query_duration('')
        with pytest.raises(ValueError):
            self.uut.clickhouse_query_duration("&&")

    def test_clickhouse_query_count(self):
        with pytest.raises(ValueError):
            self.uut.clickhouse_query_count(None)
        with pytest.raises(ValueError):
            self.uut.clickhouse_query_count('')
        with pytest.raises(ValueError):
            self.uut.clickhouse_query_count("&&")
