import json
import pytest
from csv_data_provider import CsvDataProvider
from clickhouse_calc import ClickHouseCalc
from calc import STORAGE_TYPE, LAST_CHANGED_ON, VERSION


class TestFsiemResourceCalc:

    def test_validate_number_of_seats_error(self):
        for i in range(-2, 1):
            with pytest.raises(ValueError):
                ClickHouseCalc(i, 500)
        for i in range(1001, 1005):
            with pytest.raises(ValueError):
                ClickHouseCalc(i, 500)

    def test_validate_number_of_seats(self):
        for i in range(1, 1001):
            ClickHouseCalc(i, 500)

    def test_get_data_workers(self):
        for i in range(1, 61):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 2
        for i in range(61, 121):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 4
        for i in range(121, 181):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 6
        for i in range(181, 241):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 8
        for i in range(241, 301):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 10
        for i in range(301, 361):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 12
        for i in range(361, 421):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 14
        for i in range(421, 481):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 16
        for i in range(481, 541):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 18
        for i in range(541, 601):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 20
        for i in range(601, 661):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 22
        for i in range(661, 721):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 24
        for i in range(721, 781):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 26
        for i in range(781, 841):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 28
        for i in range(841, 901):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 30
        for i in range(901, 961):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 32
        for i in range(961, 1001):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_data_workers() == 34

    def test_get_data_workers_full_range(self):
        valid_range = range(2, 36, 2)
        for i in range(1, 1001):
            uut = ClickHouseCalc(i, 500)
            n = uut.get_data_workers()
            assert n in valid_range

    def test_get_keeper_workers(self):
        for i in range(1, 2):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_keeper_workers() == 0
        for i in range(3, 61):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_keeper_workers() == 1
        for i in range(61, 1001):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_keeper_workers() == 3

    def test_get_ingestion_workers(self):
        for i in range(1, 1001):
            uut = ClickHouseCalc(i, 500)
            assert uut.get_ingestion_workers() == 0

    def test_get(self):
        csv_file = 'tests/data/Scalability_Tests_V1_CH.csv'
        data_provider = CsvDataProvider(csv_file, STORAGE_TYPE.CLICKHOUSE)
        for entry in data_provider.read():
            uut = ClickHouseCalc(entry.number_of_seats, 500)
            entry.app_server_mem_gb = uut.get_app_server_mem_gb()
            getter = uut.get()

            assert entry.super_instance_types[0] == \
                getter.super_instance_types[0], \
                f'N seats: {entry.number_of_seats}'
            assert entry.worker_instance_types[0] == \
                getter.worker_instance_types[0], \
                f'N seats: {entry.number_of_seats}'
            if entry.number_of_seats == 1 or entry.number_of_seats == 2:
                assert getter.keeper_instance_types == [], \
                    f'N seats: {entry.number_of_seats}'
            else:
                assert entry.keeper_instance_types[0] == \
                    getter.keeper_instance_types[0], \
                    f'N seats: {entry.number_of_seats}'

            # Set missing fields
            # Not ideal as test class is reused, but this works
            entry.super_instance_types = uut.get_super_instance_types()
            entry.worker_instance_types = uut.get_worker_instance_types()
            entry.keeper_instance_types = uut.get_keeper_instance_types()
            entry.ingestion_instance_types = uut.get_ingestion_instance_types()
            assert entry == uut.get(), f'N seats: {entry.number_of_seats}'

    def test_get_json(self):
        uut = ClickHouseCalc(5, 500)
        expected_json = {
            'shards': 1, 'replicas': 2,
            'data_workers': 2, 'keeper_workers': 1, 'ingestion_workers': 0,
            'super_instance_types': [
                'm6i.2xlarge', 'm6a.2xlarge', 'm5.2xlarge'
            ],
            'worker_instance_types': [
                'm6i.2xlarge', 'm6a.2xlarge', 'm5.2xlarge'
            ],
            'keeper_instance_types': [
                'c6i.xlarge', 'c6a.xlarge', 'c5.xlarge'
            ],
            'ingestion_instance_types': [
                'c6i.xlarge', 'c6a.xlarge', 'c5.xlarge'
            ],
            'cmdb_iops': 3000,
            'cmdb_throughput': 200,
            'data_disk_iops': 3000,
            'data_disk_throughput': 280,
            'opt_iops': 3000,
            'opt_throughput': 200,
            'data_disk_count': 5,
            'data_disk_size': 100,
            'app_server_mem_gb': 5, 'number_of_seats': 5,
            'last_changed_on': LAST_CHANGED_ON, 'version': VERSION}
        expected = json.dumps(expected_json, default=vars)
        actual = json.dumps(uut.get(), default=vars)
        assert expected == actual
