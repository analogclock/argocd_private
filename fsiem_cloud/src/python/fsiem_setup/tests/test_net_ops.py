from net_ops import check_if_ip


def test_check_if_ip_correct():
    addresses = ['10.0.0.1', 'google.com', '2001:4860:4860::8888']

    expected = ['10.0.0.1'], ['google.com']
    actual = check_if_ip(addresses)

    assert actual == expected


def test_check_if_ip_empty():
    addresses = []

    expected = [], []
    actual = check_if_ip(addresses)

    assert actual == expected
