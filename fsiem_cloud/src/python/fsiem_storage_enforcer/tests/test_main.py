from main import get_cleanup_size


def test_get_cleanup_size_correct():
    assert get_cleanup_size(12, 15, 5) == -2
    assert get_cleanup_size(15, 25, 5) == 5
