import string


def to_unicode_code_point(input: str) -> [int]:
    """Convert string to array of Unicode numeric values

    Parameters
    ----------
    input : str
        Unicode string

    Returns
    -------
    [int]
        A list of numbers, each number is a unicode value for the char
    """
    return [ord(c) for c in input]


def contains_only_printable_ascii(s: str) -> bool:
    """Returns True if the Unicode string only contains printable ASCII"""
    return all(c in string.printable for c in s)


def contains_subset_ascii(s: str) -> bool:
    """Checks if string only contains limited ASCII charset:
    - English letters (upper case and lower case)
    - Digits
    - Space, dot, dash, underscore, equals, star, etc

    Parameters
    ----------
    s : str
        input string

    Returns
    -------
    bool
        True if each and every char in the string matches the condition,
        otherwise False
    """
    white_list = string.ascii_letters + string.digits + " .,-:_=*()/@"
    return all(c in white_list for c in s)
