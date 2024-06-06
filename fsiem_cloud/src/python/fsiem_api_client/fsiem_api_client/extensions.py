from itertools import islice


def chunk(it, size):
    """Yield successive n-sized chunks from iterable.

    >>> list(chunk(range(14), 3))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13)]

    Based on: https://stackoverflow.com/a/22045226/706456
    """
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())
