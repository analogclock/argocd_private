import random

import pytest
from fsiem_api_client.aws.ec2 import Ec2
from fsiem_api_client.aws.ssm_ops import SsmOps
from fsiem_api_client.backup_options_table import BackupOptions
from fsiem_api_client.const import BackupType, worker_disk_sizes
from fsiem_api_client.gzip_compress import GzipCompress


class TestSsmOps:

    region = 'us-east-1'
    sn = 'FSMCLD0000000181'
    uut = SsmOps(region=region, sn=sn)

    def test_lsblk(self):
        resp = self.uut._lsblk('i-0f7b5c96fa9a0d497')
        assert resp.status == 'Success'

    def test_find_disks_except_given_sizes(self):
        known_disks = ['25G', '100G']
        resp = self.uut._find_disks_except_given_sizes(
            'i-0f7b5c96fa9a0d497', known_disks)
        assert len(resp) > 0

    def test_clickhouse_count_external_storage_records(self):
        organization_id = -1
        items = ['(18250,20240119)']
        resp = self.uut.clickhouse_count_external_storage_records(
                                                            organization_id,
                                                            items)
        assert resp

    def test_clickhouse_copy_to_external_storage(self):
        organization_id = 1
        ext_storage = 'fsiemextstr-test-s3-cust-id-1'
        items = ['(18250,20240119)']
        file_name = 'external_storage_file_test'
        file_format = 'Parquet'
        resp = self.uut.clickhouse_copy_to_external_storage(organization_id,
                                                            ext_storage,
                                                            items, file_name,
                                                            file_format)
        assert resp

    def test_list_disks_on_supers(self):
        resp = self.uut.list_disks_on_supers()
        assert resp

    def test_list_disks_on_workers(self):
        resp = self.uut.list_disks_on_workers()
        assert resp

    def test_find_disks_supers(self):
        resp = self.uut.find_disks_supers(worker_disk_sizes)
        assert resp

    def test_find_disks_workers(self):
        resp = self.uut.find_disks_workers(worker_disk_sizes)
        assert resp

    def test_get_app_server_memory(self):
        resp = self.uut.get_app_server_memory(
            '/opt/glassfish/domains/domain1/config/domain.xml')
        assert resp

    def test_update_app_server_memory(self):
        ids = self.uut.ec2.get_instance_ids(self.sn, 'super')
        resp = self.uut.update_app_server_memory(
            ids, '5120m', '10240m',
            '/opt/glassfish/domains/domain1/config/domain.xml'
        )
        assert resp

    def test_get_workers_used_disk_space(self):
        resp = self.uut.get_workers_used_disk_space(worker_disk_sizes)
        assert resp > 0

    def test_clickhouse_archive_size(self):
        resp = self.uut.clickhouse_archive_size()
        assert resp > 0

    def test_get_number_of_workers(self):
        resp = self.uut.get_number_of_workers()
        assert resp > 0

    def test_workers_instance_id(self):
        resp = self.uut.workers_instance_id()
        assert len(resp) > 0

    def test_worker_instance_id_by_dns(self):
        dns = 'ip-10-0-101-87.eu-west-1.compute.internal'
        resp = self.uut.worker_instance_id_by_dns(dns)
        assert resp

    def test_get_number_of_supers(self):
        resp = self.uut.get_number_of_supers()
        assert resp > 0

    def test_get_number_of_keepers(self):
        resp = self.uut.get_number_of_keepers()
        assert resp > 0

    def test_clickhouse_oldest_data(self):
        resp = self.uut.clickhouse_oldest_data()
        assert resp

    def test_expand_workers_clickhouse_fs(self):
        resp = self.uut.expand_workers_clickhouse_fs()
        assert resp

    #
    # Clickhouse backup and restore
    #
    opt = {
        'remote_storage': 's3',
        'log_level': 'warn',
        'region': region,
        's3_bucket': f'fsiem-clickhouse-backups-{region}-dev',
        's3_path': sn,
        's3_compression_level': '1',
        's3_compression_format': 'tar',
        's3_use_custom_storage_class': 'false',
        's3_storage_class': 'STANDARD',
        's3_concurrency': '1',
        's3_debug': 'false',
    }

    backup_options_str = """[{"S3_COMPRESSION_LEVEL": "6"}, {"S3_COMPRESSION_FORMAT": "bzip2"}, {"S3_USE_CUSTOM_STORAGE_CLASS": "false"}]"""  # noqa

    def test_clickhouse_backup_create(self):
        rnd = random.randint(1, 1000)
        full = f'backup-{rnd}-full'
        inc = f'backup-{rnd}-inc'

        parser = BackupOptions()
        backup_options = parser.from_str(self.backup_options_str)
        # Full backup
        resp = self.uut.clickhouse_backup_create(
            full, BackupType.FULL, None, self.opt, backup_options)

        # Incremental backup
        resp = self.uut.clickhouse_backup_create(
            inc, BackupType.INCREMENTAL, full, self.opt)
        assert resp

    def test_clickhouse_backup_list(self):
        resp = self.uut.clickhouse_backup_list(self.opt)
        assert resp

    def test_clickhouse_backup_cleanup(self):
        resp = self.uut.clickhouse_backup_cleanup(self.opt)
        assert resp

    def test_clickhouse_backup_delete(self):
        backups = self.uut.clickhouse_backup_list(self.opt)
        for backup in backups:
            resp = self.uut.clickhouse_backup_delete(
                backup.name, backup.location, self.opt)
            assert resp

    def test_clickhouse_backup_restore(self):
        full = 'backup-698-full'
        inc = 'backup-698-inc'

        # Restore from remote backups, delete locally cached copy
        resp = self.uut.clickhouse_backup_restore(full, self.opt)
        resp = self.uut.clickhouse_backup_delete(full, 'local', self.opt)

        resp = resp = self.uut.clickhouse_backup_restore(inc, self.opt)
        resp = self.uut.clickhouse_backup_delete(inc, 'local', self.opt)
        assert resp

    def test_clickhouse_metrics(self):
        instance_dns = 'ip-10-0-101-147.eu-west-1.compute.internal'
        resp = self.uut.clickhouse_metrics(instance_dns)
        assert resp

    def test_clickhouse_query_duration(self):
        instance_dns = 'ip-10-0-101-147.eu-west-1.compute.internal'
        resp = self.uut.clickhouse_query_duration(instance_dns)
        assert resp

    def test_clickhouse_query_count(self):
        instance_dns = 'ip-10-0-101-147.eu-west-1.compute.internal'
        resp = self.uut.clickhouse_query_count(instance_dns)
        assert resp

    def test_clickhouse_delete_partitions(self):
        self.uut.clickhouse_delete_partitions(['(18250,20231201)'])

    def test__split_partition_into_2_chunks(self):
        actual = self.uut._split_partition_into_2_chunks('(18250,20231201)')
        assert actual[0] == '18250'
        assert actual[1] == '20231201'

        actual = self.uut._split_partition_into_2_chunks('(18250, 20231201)')
        assert actual[0] == '18250'
        assert actual[1] == '20231201'

        with pytest.raises(ValueError):
            self.uut._split_partition_into_2_chunks('foo')
        with pytest.raises(ValueError):
            self.uut._split_partition_into_2_chunks('(18250, foo)')
        with pytest.raises(ValueError):
            self.uut._split_partition_into_2_chunks('(foo, 20231201)')

    def test_stop_app_server(self):
        ec2 = Ec2(self.region)
        ids = ec2.get_instance_ids(self.sn, 'super')
        resp = self.uut.stop_app_server(ids)
        assert resp

    def test_get_instance_info(self):
        resp = self.uut.get_instance_info('super', ['25g'])
        assert resp

    def test_clickhouse_online_parts(self):
        resp = self.uut.clickhouse_online_parts()
        assert resp

    def test_clickhouse_online_parts_gz(self):
        resp = self.uut.clickhouse_online_parts_gz()
        assert resp
        compressor = GzipCompress()
        result = compressor.decompress_str(resp)
        assert result

    def test_clickhouse_archive_parts(self):
        resp = self.uut.clickhouse_archive_parts()
        assert resp

    def test_clickhouse_archive_parts_gz(self):
        resp = self.uut.clickhouse_archive_parts_gz()
        assert resp
        compressor = GzipCompress()
        result = compressor.decompress_str(resp)
        assert result
