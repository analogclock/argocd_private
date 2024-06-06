from fsiem import eps, i_inline_report_queue, original_inline_report_queue


def test_eps_correct(fs):
    fs.create_file(
        '/opt/phoenix/cache/EventPerSecInfo',
        contents='3 Min: 0.02    15 Min: 0.03    30 Min: 0.04'
    )
    avg_time = '3 Min'
    expected = 0.02
    actual = eps(avg_time)
    assert actual == expected


def test_original_inline_report_queue_correct(fs):
    fs.create_file('/data/eventdb/CUSTOMER_001/report/original/new/REPT_1.rpt')
    fs.create_file('/data/eventdb/CUSTOMER_002/report/original/new/REPT_2.rpt')
    fs.create_file('/data/eventdb/CUSTOMER_003/report/original/new/REPT_3.rpt')
    expected = 3
    actual = original_inline_report_queue()
    assert actual == expected


def test_i_inline_report_queue_i300_correct(fs):
    fs.create_file(
        '/data/eventdb/CUSTOMER_001/report/i300/new/REPT_2.rpt',
        contents='test\n'
    )
    fs.create_file(
        '/data/eventdb/CUSTOMER_003/report/i300/new/REPT_4.rpt',
        contents='test\ntest\n'
    )
    fs.create_file(
        '/data/eventdb/CUSTOMER_005/report/i300/new/REPT_6.rpt',
        contents='test\ntest\ntest'
    )
    fs.create_file(
        '/data/eventdb/CUSTOMER_001/report/i900/new/REPT_9.rpt',
        contents='test\n'
    )
    expected = 6
    actual = i_inline_report_queue('i300')
    assert actual == expected


def test_i_inline_report_queue_i900_correct(fs):
    fs.create_file(
        '/data/eventdb/CUSTOMER_001/report/i300/new/REPT_2.rpt',
        contents='test'
    )
    fs.create_file(
        '/data/eventdb/CUSTOMER_001/report/i900/new/REPT_9.rpt',
        contents='test\ntest'
    )
    expected = 2
    actual = i_inline_report_queue('i900')
    assert actual == expected
