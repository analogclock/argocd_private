from calc import STORAGE_TYPE
from main import get_json_output


def test_get_json_output_clickhouse():
    n = 5
    type = STORAGE_TYPE('clickhouse')
    j_str = get_json_output(n, type, online_size=500, max_per_disk=10000)
    assert j_str


def test_get_json_output_eventdb():
    n = 5
    type = STORAGE_TYPE('eventdb')
    j_str = get_json_output(n, type, online_size=500, max_per_disk=10000)
    assert j_str
