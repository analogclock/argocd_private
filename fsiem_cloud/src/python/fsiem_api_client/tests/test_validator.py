import pytest
from fsiem_api_client.const import FsiemInstanceRole
from fsiem_api_client.validator import Validator

uut = Validator()


class TestValidator:

    def test_is_valid_role(self):
        assert uut.is_valid_role(FsiemInstanceRole.super.name)
        assert uut.is_valid_role(FsiemInstanceRole.keeper.name)
        assert uut.is_valid_role(FsiemInstanceRole.worker.name)
        assert not uut.is_valid_role('foo')

    def test_enforce_valid_role(self):
        uut.enforce_valid_role(FsiemInstanceRole.super.name)
        with pytest.raises(ValueError):
            uut.enforce_valid_role('\\foo')

    def test_are_valid_disk_sizes(self):
        assert uut.are_valid_disk_sizes(['100G', '25g', '1Ti', '10Gi'])
        assert not uut.are_valid_disk_sizes(['foo'])
        assert not uut.are_valid_disk_sizes(['10'])

    def test_enforce_valid_disk_sizes(self):
        uut.enforce_valid_disk_sizes(['100G'])
        with pytest.raises(ValueError):
            uut.enforce_valid_disk_sizes(['foo'])
        with pytest.raises(ValueError):
            uut.enforce_valid_disk_sizes(['1234;rm-rf;b'])

    def test_is_valid_memory_size(self):
        assert uut.is_valid_memory_size('5120m')
        assert uut.is_valid_memory_size('10240m')
        assert not uut.is_valid_memory_size('foo')
        assert not uut.is_valid_memory_size('10')

    def test_enforce_valid_memory_size(self):
        uut.enforce_valid_memory_size('10240m')
        with pytest.raises(ValueError):
            uut.enforce_valid_memory_size('10')

    def test_is_single_sql_statement(self):
        assert uut.is_single_sql_statement('select * from foo')
        assert not uut.is_single_sql_statement('select * from foo; drop bar')

    def test_enforce_single_sql_statement(self):
        uut.enforce_single_sql_statement('select * from foo')
        with pytest.raises(ValueError):
            uut.enforce_single_sql_statement('select * from foo; drop bar')

    def test_enforce_subset_ascii(self):
        uut.enforce_subset_ascii('foo')
        with pytest.raises(ValueError):
            uut.enforce_subset_ascii(';')

    def test_enforce_int(self):
        uut.enforce_int(-1)
        with pytest.raises(ValueError):
            uut.enforce_int(';')

    def test_enforce_dict_subset_ascii(self):
        options = {
            "remote_storage": "s3",
            "log_level": "info",
            "s3_bucket": "fsiem-clickhouse-backups-us-east-1-playground",
            "region": "us-east-1",
            "s3_path": "FSMCLD0000000154",
            "s3_compression_level": "1",
            "s3_compression_format": "tar",
            "s3_use_custom_storage_class": "false",
            "s3_storage_class": "STANDARD",
            "s3_concurrency": 1,
            "s3_debug": True,
            "email": "no-reply@mail.playground.fortisiem.cloud",
            "ip4": "127.0.0.1",
            "ip6": "0:::0"
        }
        uut.enforce_dict_subset_ascii(options)
        with pytest.raises(ValueError):
            uut.enforce_dict_subset_ascii({'foo': ';'})

    def test_enforce_list_subset_ascii(self):
        uut.enforce_list_subset_ascii(['(18250,20230902)', '(x,y)', 1, True])
        with pytest.raises(ValueError):
            uut.enforce_list_subset_ascii([])
        with pytest.raises(ValueError):
            uut.enforce_list_subset_ascii(None)
        with pytest.raises(ValueError):
            uut.enforce_list_subset_ascii(['&&'])
        with pytest.raises(ValueError):
            uut.enforce_list_subset_ascii(['(18250,20230902; run foobar)'])

    def test_is_valid_s3_bucket_name(self):
        assert uut.is_valid_s3_bucket_name('test-ssm-alt-region')
        assert not uut.is_valid_s3_bucket_name('touch tests3bucket1')

    def test_is_valid_s3_bucket_prefix(self):
        assert uut.is_valid_s3_bucket_prefix('test-ssm-alt-region/dir1/')

        assert not uut.is_valid_s3_bucket_prefix('test-;ssm-alt-region/dir1/')
