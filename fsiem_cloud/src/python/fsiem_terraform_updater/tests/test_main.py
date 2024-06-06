from freezegun import freeze_time
from main import region_midnight
import pytest


@freeze_time("2012-01-14 00:04:34", tz_offset=0)
def test_region_midnight_false():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'us-east-1'
        }
    }
    expected = False
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=0)
def test_region_midnight_unknown_region():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'us-east-3'
        }
    }
    with pytest.raises(KeyError):
        region_midnight(item)


@freeze_time("2012-01-14 00:04:34", tz_offset=0)
def test_region_midnight_eu_west_1():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'eu-west-1'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=0)
def test_region_midnight_eu_west_2():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'eu-west-1'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=-1)
def test_region_midnight_eu_central_1():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'eu-central-1'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=-1)
def test_region_midnight_eu_north_1():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'eu-north-1'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=-1)
def test_region_midnight_eu_west_3():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'eu-west-3'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=5)
def test_region_midnight_us_east_1():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'us-east-1'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=5)
def test_region_midnight_us_east_2():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'us-east-2'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=5)
def test_region_midnight_ca_central_1():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'ca-central-1'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=8)
def test_region_midnight_us_west_2():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'us-west-2'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=-5.5)
def test_region_midnight_ap_south_1():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'ap-south-1'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=-8)
def test_region_midnight_ap_southeast_1():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'ap-southeast-1'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=-11)
def test_region_midnight_ap_southeast_2():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'ap-southeast-2'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected


@freeze_time("2012-01-14 00:04:34", tz_offset=-3)
def test_region_midnight_me_south_1():
    item = {
        'serialNumber': {
            'S': 'test'
        },
        'region': {
            'S': 'me-south-1'
        }
    }
    expected = True
    actual = region_midnight(item)
    assert actual == expected
