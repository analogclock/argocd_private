import pytest
from calc import Calc


class TestCalc:

    def test_get_app_server_mem_gb_error(self):
        for i in range(-2, 1):
            with pytest.raises(ValueError):
                uut = Calc(i)
                uut.get_app_server_mem_gb()
        for i in range(1001, 1005):
            with pytest.raises(ValueError):
                uut = Calc(i)
                uut.get_app_server_mem_gb()

    def test_get_app_server_mem_gb(self):
        for i in range(1, 7):
            uut = Calc(i)
            assert 5 == uut.get_app_server_mem_gb()
        for i in range(7, 15):
            uut = Calc(i)
            assert 10 == uut.get_app_server_mem_gb()
        for i in range(15, 1001):
            uut = Calc(i)
            assert 20 == uut.get_app_server_mem_gb()

    def test_get_data_disk_count(self):
        assert 5 == Calc(5, 38 * 500).get_data_disk_count()

    def test_get_data_disk_size(self):
        # size of 500 GB
        assert 100 == Calc(5, 500).get_data_disk_size()

        # size of 2500 GB
        assert 500 == Calc(5, 2500).get_data_disk_size()

        # size of 10 TB
        assert 2000 == Calc(5, 10000).get_data_disk_size()

        # size of 10.5 TB
        assert 2100 == Calc(5, 10500).get_data_disk_size()

        # size of 19 TB
        assert 3800 == Calc(5, 19000).get_data_disk_size()
