from packaging import version
import pytest


def test_version_parse():
    with pytest.raises(Exception):
        assert version.parse("")
    with pytest.raises(Exception):
        assert version.parse(None)

    version_7_1_4 = version.parse("7.1.4")
    assert 7 == version_7_1_4.major
    assert 1 == version_7_1_4.minor
    assert 4 == version_7_1_4.micro

    assert version.parse("7.1.4") > version.parse("7.1.1")
    assert version.parse("7.1.4.1234") > version.parse("7.1.1.1234")

    assert version.parse("0.0.0")
