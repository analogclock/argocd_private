from fsiem_api_client.string_utils import to_unicode_code_point, \
    contains_only_printable_ascii, contains_subset_ascii


def test_to_unicode_code_point():
    actual = to_unicode_code_point('England')
    assert actual == [69, 110, 103, 108, 97, 110, 100]
    actual = to_unicode_code_point(u'Українa')
    assert actual == [1059, 1082, 1088, 1072, 1111, 1085, 97]


# Select * from foo where sn='{user_input}'
# Consider user input to be: \\u0027; drop table foo
# Then database command will look like this
# Select * from foo where sn='\; drop table foo'
def test_still_a_single_quote():
    single_quote1 = to_unicode_code_point('\'')
    single_quote2 = to_unicode_code_point(u'\u0027')
    assert single_quote1 == single_quote2


def test_contains_only_printable_ascii():
    assert contains_only_printable_ascii('England')
    assert not contains_only_printable_ascii('Українa')


def test_contains_subset_ascii():
    assert contains_subset_ascii('')
    assert contains_subset_ascii('England')
    assert not contains_subset_ascii('Українa')
    assert not contains_subset_ascii(';')
